from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.http import Http404
from django.contrib import messages

from apps.accounts.models import User
from apps.accounts.decorators import teacher_required
from apps.pages.common_functions import get_sidebar_context
from apps.classroom.models import Classroom
from .models import Exam
from .models import Question
from .forms import  ExamCreationForm
from .forms import ExamJoinForm
from .forms import ExamQuestionCreationForm

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
        context['exam'] = get_object_or_404(Exam.objects.select_related('classroom', 'classroom__teacher'), id = exam_id)
        context['questions'] = Question.objects.filter(exam = context['exam']).prefetch_related('options')
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
