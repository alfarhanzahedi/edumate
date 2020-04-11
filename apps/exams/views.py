from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.http.response import JsonResponse

from datetime import timedelta

from apps.accounts.models import User
from apps.accounts.decorators import teacher_required
from apps.pages.common_functions import get_sidebar_context
from apps.classroom.models import Classroom
from .models import Exam
from .models import Question
from .models import Option
from .models import Submission
from .models import Answer
from .forms import  ExamCreationForm
from .forms import ExamJoinForm
from .forms import ExamQuestionCreationForm
from .forms import AnswerForm

class ExamCreateView(View):

    def get(self, request, classroom_id):
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = classroom_id)
        if request.user != classroom.teacher:
            raise Http404
        context = get_sidebar_context(request)

        context['form'] = ExamCreationForm()
        context['form'].fields['students'].queryset = classroom.students.all()
        context['classroom'] = classroom
        return render(request, 'exams/exam_create_form.html', context)

    def post(self, request, classroom_id):
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = classroom_id)
        if request.user != classroom.teacher:
            raise Http404
        
        form = ExamCreationForm(request.POST)

        if not form.is_valid():
            context = get_sidebar_context(request)
            context['form'] = form
            context['classroom'] = classroom
            messages.error(request, 'Please correct the errors mentioned below and try again.')
            return render(request, 'exams/exam_create_form.html', context)

        exam = form.save(commit = False)
        exam.classroom = classroom
        exam.save()
        messages.success(request, f'Examination/Assignment - {exam.title} successfully created!')
        return redirect('exam_detail', classroom_id = classroom.id, exam_id = exam.id)

class ExamDetailView(View):

    def get(self, request, classroom_id, exam_id):
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = classroom_id)
        if request.user != classroom.teacher and request.user not in classroom.students.all():
            raise Http404
        context = get_sidebar_context(request)
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)
        context['exam'] = exam
        context['has_exam_started'] = exam.start_time <= timezone.now()
        if request.user == classroom.teacher or exam.end_time < timezone.now():
            context['questions'] = Question.objects.filter(exam = exam).prefetch_related('options')

        if request.user.is_student:
            context['submission'] = Submission.objects.filter(exam = exam, student = request.user).first()

        return render(request, 'exams/exam_detail.html', context)

class ExamUpdateView(View):

    def get(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)

        context['form'] = ExamCreationForm(instance=exam)
        context['form'].fields['students'].queryset = exam.classroom.students.all()
        context['classroom'] = exam.classroom
        context['exam'] = exam
        context['update_view'] = True
        return render(request, 'exams/exam_create_form.html', context)

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)
        
        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        form = ExamCreationForm(request.POST, instance = exam)

        if not form.is_valid():
            context = get_sidebar_context(request)
            context['form'] = form
            context['classroom'] = exam.classroom
            context['exam'] = exam
            context['update_view'] = True
            messages.error(request, 'Please correct the errors mentioned below and try again.')
            return render(request, 'exams/exam_create_form.html', context)

        form.save()
        messages.success(request, f'Examination/Assignment - {exam.title} successfully updated!')
        return redirect('exam_detail', classroom_id = exam.classroom.id, exam_id = exam.id)

class ExamJoinView(View):

    def post(self, request):
        redirect_to = request.POST.get('next', '/')
        form = ExamJoinForm(request.POST)
        
        if form.is_valid():
            unique_code = form.cleaned_data.get('unique_code')
            exam = Exam.objects.select_related('classroom', 'classroom__teacher').get(unique_code = unique_code)
            
            if exam.classroom.teacher == request.user:
                messages.warning(request, f'The creator of the examination/assignment cannot take the examination/assignment.')
                return redirect(redirect_to)
            
            if request.user in exam.students.all():
                return redirect('exam_detail', classroom_id = exam.classroom.id, exam_id = exam.id)
            
            exam.students.add(request.user)
            exam.save()
            messages.success(request, f'You can now take the examination/assignment - {exam.title}. All the best!')
            return redirect('exam_detail', classroom_id = exam.classroom.id, exam_id = exam.id)
        
        messages.error(request, f'The unique code is not associated with any examination/assignment!')
        return redirect(redirect_to)

class ExamPublishView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        exam.is_published = True
        exam.save()

        messages.success(request, 'Exam published successfully!')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)


class ExamQuestionCreateView(View):

    def get(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)
        context['exam'] = exam
        context['form'] = ExamQuestionCreationForm()
        return render(request, 'exams/exam_question_create_form.html', context)

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        form = ExamQuestionCreationForm(request.POST)

        is_mcq = form.data.get('type') in [Question.MCQ_SOC, Question.MCQ_MOC]

        is_form_valid = form.is_valid()
        is_options_valid = True

        if is_mcq:
            if 'option' not in request.POST:
                is_options_valid = False
                messages.error(request, 'Please select the correct answer for the MCQ!')

            all_options = request.POST['alloptions'].split(',')

            if len(all_options) < 2:
                is_options_valid = False
                messages.error(request, 'Please provide at least two options for an MCQ!')

        if not is_form_valid or not is_options_valid:
            context = get_sidebar_context(request)
            context['exam'] = exam
            context['form'] = form
            return render(request, 'exams/exam_question_create_form.html', context)
        
        question = form.save(commit = False)
        question.exam = exam
        question.save()

        if is_mcq:
            for option in all_options:
                question.options.create(
                    question = question,
                    body = option,
                    is_answer = (option in request.POST.getlist('option'))
                )
        messages.success(request, 'The question was successfully added.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamQuestionUpdateView(View):

    def get(self, request, classroom_id, exam_id, question_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)
        question = get_object_or_404(Question.objects.prefetch_related('options'), id = question_id)
        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)
        context['exam'] = exam
        context['form'] = ExamQuestionCreationForm(instance=question)
        context['question'] = question
        context['update_view'] = True
        return render(request, 'exams/exam_question_create_form.html', context)

    def post(self, request, classroom_id, exam_id, question_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        question = get_object_or_404(Question, id = question_id)
        form = ExamQuestionCreationForm(request.POST, instance = question)

        is_mcq = form.data.get('type') in [Question.MCQ_SOC, Question.MCQ_MOC]

        is_form_valid = form.is_valid()
        is_options_valid = True

        if is_mcq:
            if 'option' not in request.POST:
                is_options_valid = False
                messages.error(request, 'Please select the correct answer for the MCQ!')

            all_options = request.POST['alloptions'].split(',')

            if len(all_options) < 2:
                is_options_valid = False
                messages.error(request, 'Please provide at least two options for an MCQ!')

        if not is_form_valid or not is_options_valid:
            context = get_sidebar_context(request)
            context['exam'] = exam
            context['form'] = form
            context['question'] = question
            context['update_view'] = True
            return render(request, 'exams/exam_question_create_form.html', context)
        
        form.save()

        question.options.all().delete()

        if is_mcq:
            for option in all_options:
                question.options.create(
                    question = question,
                    body = option,
                    is_answer = (option in request.POST.getlist('option'))
                )

        messages.success(request, 'The question was successfully updated.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamQuestionDeleteView(View):

    def post(self, request, classroom_id, exam_id, question_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        get_object_or_404(Question, id = question_id).delete()
        messages.success(request, 'The question was successfully deleted.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamStartView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom'), id = exam_id)

        if exam.classroom.id != classroom_id or request.user not in exam.students.all():
            raise Http404
        
        if exam.start_time > timezone.now():
            messages.warning(request, f'The exam starts at {exam.start_time}!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)
        
        submission = None
        try:
            submission = Submission.objects.create(exam = get_object_or_404(Exam, id = exam_id), student = request.user)
        except IntegrityError:
            messages.warning(f'You cannot start the examination/assignment again!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        return redirect('submission_detail', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission.id)

class ExamResumeView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom'), id = exam_id)

        if exam.classroom.id != classroom_id or request.user not in exam.students.all():
            raise Http404

        submission = get_object_or_404(Submission, exam = exam, student = request.user)
        messages.success(request, f'Examination/assignment successfully submitted!')
        return redirect('submission_detail', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission.id)

class ExamEndView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom'), id = exam_id)

        if exam.classroom.id != classroom_id or request.user not in exam.students.all():
            raise Http404

        submission = get_object_or_404(Submission, exam = exam, student = request.user)
        submission.is_submitted = True
        submission.save()
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)


def get_exam_duration(exam):
    duration = None
    if not exam.is_open_exam:
        if exam.duration:
            duration = exam.duration * 60
        else:
            duration = (exam.end_time - exam.start_time).total_seconds()
    else:
        if not exam.duration:
            duration = (exam.end_time - exam.start_time).total_seconds()
        else:
            duration = exam.duration * 60

    return duration

class SubmissionDetailView(View):

    def get(self, request, classroom_id, exam_id, submission_id):
        submission = get_object_or_404(Submission.objects.select_related('exam', 'exam__classroom', 'student').prefetch_related('answers', 'answers__options', 'answers__question', 'exam__questions', 'exam__questions__options'), id = submission_id)

        exam_duration = get_exam_duration(submission.exam)

        print(exam_duration)

        if (submission.started_at + timedelta(minutes = exam_duration)) < timezone.now():
            submission.is_submitted = True
            submission.save()
            messages.warning(request, 'You have already taken this examination/assignment!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        if submission.is_submitted:
            messages.warning(request, 'You have already taken this examination/assignment!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        if request.user != submission.student or submission.exam.classroom.id != classroom_id or submission.exam.id != exam_id:
            raise Http404

        questions_and_answer = {}

        for question in submission.exam.questions.all():
            question_id = str(question.id)
            questions_and_answer[question_id] = {}
            questions_and_answer[question_id]['question'] = question
            questions_and_answer[question_id]['answer'] = None
            questions_and_answer[question_id]['form'] = AnswerForm()
    
        for answer in submission.answers.all():
            question_id = str(answer.question.id)
            questions_and_answer[question_id]['answer'] = answer
            if not questions_and_answer[question_id]['question'].is_mcq():
                questions_and_answer[question_id]['form'] = AnswerForm(instance = answer)

        time_left = (submission.started_at + timedelta(seconds = exam_duration)) - timezone.now()
        
        context = {
            'submission': submission,
            'exam': submission.exam,
            'questions_and_answer': questions_and_answer,
            'time_left': time_left.total_seconds()
        }
        return render(request, 'exams/submission_detail.html', context)

def is_exam_over(submission):
    exam = submission.exam
    exam_duration = get_exam_duration(exam)

    if exam.is_open_exam:
        return ((submission.started_at + timedelta(seconds = exam_duration)) < timezone.now())        
    else:
        return exam.end_time < timezone.noe()

class AnswerView(View):

    def post(self, request, classroom_id, exam_id, submission_id, question_id):
        submission = get_object_or_404(Submission.objects.select_related('exam', 'exam__classroom', 'student'), id = submission_id)
        question = get_object_or_404(Question.objects.select_related('exam'), id = question_id)

        if is_exam_over(submission):
            messages.warning(request, 'This examination/assignment is over!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        if request.user != submission.student or submission.exam.classroom.id != classroom_id or submission.exam.id != exam_id or question.exam.id != exam_id:
            raise Http404

        answer = Answer.objects.filter(student = request.user, question = question).first()

        if 'clear' in request.POST:
            if not answer is None:
                answer.delete()
            return JsonResponse({'status': 'success', 'message': 'Answer cleared successfully!'})

        if question.is_mcq():
            if not 'option' in request.POST:
                return JsonResponse({'status': 'fail', 'message': 'Please select atleast one option!'}, status = 400)
        else:
            if request.POST.get('body') == '':
                return JsonResponse({'status': 'fail', 'message': 'Please provide an answer!'}, status = 400)

        answer = Answer.objects.filter(student = request.user, question = question).first()

        if answer is None:
            answer = Answer.objects.create(
                submission = submission,
                question = question,
                student = request.user,
                body = request.POST['body'] if 'body' in request.POST else None
            )
        else:
            answer.body = request.POST['body'] if 'body' in request.POST else None
            answer.save()

        if question.is_mcq():
            answer.options.clear()
            for option in request.POST.getlist('option'):
                print(f'Option = {option}')
                answer.options.add(
                    Option.objects.get(id = int(option))
                )
        return JsonResponse({'status': 'success', 'message': 'Answer added successfully!'})
