from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Prefetch
from django.http.response import JsonResponse

from datetime import timedelta
import logging

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
from .tasks import evaluate_single_submission
from .tasks import evaluate_all_submissions

logger = logging.getLogger(__name__)

def time_left(submission):
    # If the exam has ended or has not started yet, simply return -1.
    # This check has already been handled in the view, but, still, it made sense to keep the check
    # in this function too.
    if submission.exam.has_ended() or not submission.exam.has_started():
        return -1

    # When the exam is an 'open' exam.
    if submission.exam.is_open_exam:
        assumed_end_time = submission.started_at + timedelta(seconds = submission.exam.adjusted_duration())

        if assumed_end_time <= submission.exam.end_time:
            return (assumed_end_time - timezone.now()).total_seconds()

        return (submission.exam.end_time - timezone.now()).total_seconds()

    # When the exam is not an 'open' exam.
    return (submission.exam.end_time - timezone.now()).total_seconds()

class ExamCreateView(View):

    def get(self, request, classroom_id):
        classroom = get_object_or_404(
            Classroom.objects.select_related('teacher').only(
                'title',
                'description',
                'unique_code',
                'teacher__username',
                'teacher__first_name',
                'teacher__last_name'
            ),
            id = classroom_id
        )

        if request.user != classroom.teacher:
            raise Http404

        context = get_sidebar_context(request)

        context['exam_creation_form'] = ExamCreationForm()
        context['exam_creation_form'].fields['students'].queryset = classroom.students.all()
        context['classroom'] = classroom

        return render(request, 'exams/exam_create_form.html', context)

    def post(self, request, classroom_id):
        classroom = get_object_or_404(
            Classroom.objects.select_related('teacher').only(
                'title',
                'description',
                'unique_code',
                'teacher__username',
                'teacher__first_name',
                'teacher__last_name'
            ),
            id = classroom_id
        )        
        
        if request.user != classroom.teacher:
            raise Http404
        
        form = ExamCreationForm(request.POST)

        if not form.is_valid():
            context = get_sidebar_context(request)
            context['exam_creation_form'] = form
            context['exam_creation_form'].fields['students'].queryset = classroom.students.all()
            context['classroom'] = classroom

            messages.error(request, 'Please correct the errors mentioned below and try again.')
            return render(request, 'exams/exam_create_form.html', context)

        exam = form.save(commit = False)
        exam.classroom = classroom
        exam.save()

        messages.success(request, f'Examination/Assignment - \'{exam.title}\' successfully created!')
        return redirect('exam_detail', classroom_id = classroom.id, exam_id = exam.id)



class ExamDetailView(View):

    def get(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher'),
            id = exam_id
        )

        if (request.user != exam.classroom.teacher and not exam.is_published):
            raise Http404

        if (request.user != exam.classroom.teacher and not Exam.objects.filter(id = exam_id, students__in = [request.user]).exists()) or (exam.classroom.id != int(classroom_id)):
            raise Http404

        context = get_sidebar_context(request)
        context['exam'] = exam

        # If the user is the teacher, fetch the questions!
        if request.user == exam.classroom.teacher:
            context['questions'] = Question.objects.filter(exam = exam).prefetch_related('options')
            context['submissions'] = Submission.objects.filter(exam = exam, is_submitted = True).select_related('student')

        # If the user is a student, fetch their submission!
        if request.user.is_student:
            submission = Submission.objects.filter(exam = exam, student = request.user).first()

            if submission:
                if time_left(submission) < 0 and not submission.is_submitted:
                    submission.is_submitted = True
                    submission.save()

                # Fetch and display the question and answers submitted by the user only when
                # they submit the exam!
                if submission.is_submitted:
                    submission = Submission.objects.filter(exam = exam, student = request.user).prefetch_related(
                        'exam',
                        'exam__questions',
                        'exam__questions__options',
                        'answers',
                        'answers__question',
                        'answers__options'
                    ).first()

                    questions_and_answer = {}

                    for question in submission.exam.questions.all():
                        question_id = str(question.id)
                        questions_and_answer[question_id] = {}
                        questions_and_answer[question_id]['question'] = question
                        questions_and_answer[question_id]['answer'] = None

                    for answer in submission.answers.all():
                        question_id = str(answer.question.id)
                        questions_and_answer[question_id]['answer'] = answer
                    
                    context['submission'] = submission
                    context['questions_and_answer'] = questions_and_answer

        return render(request, 'exams/exam_detail.html', context)

class ExamUpdateView(View):

    def get(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher'),
            id = exam_id
        )

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)

        context['exam_creation_form'] = ExamCreationForm(instance = exam)
        context['exam_creation_form'].fields['students'].queryset = exam.classroom.students.all()

        context['classroom'] = exam.classroom
        context['exam'] = exam
        context['update_view'] = True

        return render(request, 'exams/exam_create_form.html', context)

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher'),
            id = exam_id
        )
        
        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        form = ExamCreationForm(request.POST, instance = exam)

        if not form.is_valid():
            context = get_sidebar_context(request)
            context['exam_creation_form'] = form
            context['exam_creation_form'].fields['students'].queryset = exam.classroom.students.all()

            context['classroom'] = exam.classroom
            context['exam'] = exam
            context['update_view'] = True
            
            messages.error(request, 'Please correct the errors mentioned below and try again!')
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

            exam = None
            try:
                exam = Exam.objects.select_related('classroom', 'classroom__teacher').only(
                    'id',
                    'classroom__id',
                    'classroom__title',
                    'classroom__teacher__id'
                ).get(unique_code = unique_code, is_published = True)
            except Exam.DoesNotExist:
                messages.error(request, 'The unique code is not associated with any classroom!')
                return redirect(redirect_to)

            if exam.classroom.teacher == request.user:
                messages.warning(request, 'The class teacher cannot take the examination/assignment.')
                return redirect(redirect_to)

            if not Classroom.objects.filter(id = exam.classroom.id, students__in = [request.user]).exists():
                messages.error(request, f'You are not a student of the classroom - \'{exam.classroom.title}\'. Hence, cannot take the examination/assignment!')
                return redirect(redirect_to)

            if Exam.objects.filter(id = exam.id, students__in = [request.user]).exists():
                messages.warning(request, f'You are already enrolled to take the examination/assignment!')
                return redirect('exam_detail', classroom_id = exam.classroom.id, exam_id = exam.id)
            
            exam.students.add(request.user)
            exam.save()

            messages.success(request, f'You can now take the examination/assignment - {exam.title}. All the best!')
            return redirect('exam_detail', classroom_id = exam.classroom.id, exam_id = exam.id)
        
        messages.error(request, f'The unique code provided is invalid!')
        return redirect(redirect_to)

class ExamPublishView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher'),
            id = exam_id
        )

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        exam.is_published = True
        exam.save()

        messages.success(request, 'Exam published successfully!')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)


class ExamQuestionCreateView(View):

    def get(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher').only(
                'id',
                'title',
                'classroom__id',
                'classroom__title',
                'classroom__teacher__id'
            ),
            id = exam_id
        )

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)
        context['exam'] = exam
        context['question_creation_form'] = ExamQuestionCreationForm()

        return render(request, 'exams/exam_question_create_form.html', context)

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher').only(
                'id',
                'classroom__id',
                'classroom__teacher__id'
            ),
            id = exam_id
        )

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404

        form = ExamQuestionCreationForm(request.POST)

        # Is the question type an MCQ?
        is_mcq = form.data.get('type') in [Question.MCQ_SOC, Question.MCQ_MOC]
        
        # Is the form valid?
        is_form_valid = form.is_valid()

        # Are the options valid?
        is_options_valid = True

        # What are all the options?
        all_options = None

        # If the question is an MCQ, handle the possible errors.

        # Note: All these errors are also handled in the front-end. But, it's better to handle
        # all the errors in the back-end too.
        if is_mcq:

            # There should be at least a single correct answer for an MCQ.
            if 'option' not in request.POST:
                is_options_valid = False
                messages.error(request, 'Please select the correct answer for the MCQ!')

            all_options = request.POST['alloptions'].split(',')

            # There should be at least 2 options for an MCQ.
            if len(all_options) < 2:
                is_options_valid = False
                messages.error(request, 'Please provide at least two options for an MCQ!')
            
            # ToDo: Check for empty strings as option values too.

        # If the options are valid, create the options that are to be stored in the DB.
        question_options = []
        if is_mcq and is_options_valid:
            question_options = map(lambda option : Option(body = option, is_answer = (option in request.POST.getlist('option'))), all_options)

        # If either the form is not valid, or there were errors in the options provided for the MCQ,
        # render the form again with the appropriate error messages.
        if not is_form_valid or not is_options_valid:

            context = get_sidebar_context(request)
            context['exam'] = exam
            context['question_creation_form'] = form
            context['question_options'] = question_options

            messages.error(request, 'Please correct the errors mentioned below and try again!')
            return render(request, 'exams/exam_question_create_form.html', context)


        question = form.save(commit = False)
        question.exam = exam
        question.save()

        if is_mcq:

            # bulk_create() does not returns the list of ids (i.e. pks) of the objects inserted
            # in the DB. Only PostgreSQL supports this.
            # See: https://stackoverflow.com/questions/15933689/how-to-get-primary-keys-of-objects-created-using-django-bulk-create
            # So, for now, insert all the options individually.
            option_ids = []
            for option in question_options:
                option.question = question
                option.save()
                option_ids.append(option.pk)

            # Directly passing the ids to add() results in just query as compared to N queries if all the
            # options are added individually.
            question.options.add(*option_ids)

        messages.success(request, 'The question was successfully added.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamQuestionUpdateView(View):

    def get(self, request, classroom_id, exam_id, question_id):
        question = get_object_or_404(
            Question.objects.select_related('exam', 'exam__classroom', 'exam__classroom__teacher').only(
                'id',
                'type',
                'body',
                'solution',
                'marks',
                'negative_marks',
                'exam__id',
                'exam__title',
                'exam__classroom__id',
                'exam__classroom__title',
                'exam__classroom__teacher__id'
            ).prefetch_related('options'),
            id = question_id
        )

        if request.user != question.exam.classroom.teacher or question.exam.classroom.id != int(classroom_id):
            raise Http404

        context = get_sidebar_context(request)
        context['exam'] = question.exam
        context['question_creation_form'] = ExamQuestionCreationForm(instance = question)
        context['question_options'] = question.options.all()
        context['update_view'] = True
    
        return render(request, 'exams/exam_question_create_form.html', context)

    def post(self, request, classroom_id, exam_id, question_id):
        question = get_object_or_404(
            Question.objects.select_related('exam', 'exam__classroom', 'exam__classroom__teacher').only(
                'id',
                'type',
                'body',
                'solution',
                'marks',
                'negative_marks',
                'exam__id',
                'exam__title',
                'exam__classroom__id',
                'exam__classroom__title',
                'exam__classroom__teacher__id'
            ).prefetch_related('options'),
            id = question_id
        )

        if request.user != question.exam.classroom.teacher or question.exam.id != int(exam_id) or question.exam.classroom.id != int(classroom_id):
            raise Http404

        form = ExamQuestionCreationForm(request.POST, instance = question)

        # Is the question type an MCQ?
        is_mcq = form.data.get('type') in [Question.MCQ_SOC, Question.MCQ_MOC]

        # Is the form valid?
        is_form_valid = form.is_valid()

        # Are the options valid?
        is_options_valid = True

        # What are all the options?
        all_options = None

        # If the question is an MCQ, handle the possible errors.

        # Note: All these errors are also handled in the front-end. But, it's better to handle
        # all the errors in the back-end too.
        if is_mcq:

            # There should be at least a single correct answer for an MCQ.
            if 'option' not in request.POST:
                is_options_valid = False
                messages.error(request, 'Please select the correct answer for the MCQ!')

            all_options = request.POST['alloptions'].split(',')

            # There should be at least 2 options for an MCQ.
            if len(all_options) < 2:
                is_options_valid = False
                messages.error(request, 'Please provide at least two options for an MCQ!')
            
            # ToDo: Check for empty strings as option values too.

        # If the options are valid, create the options that are to be stored in the DB.
        question_options = []
        if is_mcq and is_options_valid:
            question_options = map(lambda option : Option(body = option, is_answer = (option in request.POST.getlist('option'))), all_options)

        # If either the form is not valid, or there were errors in the options provided for the MCQ,
        # render the form again with the appropriate error messages.
        if not is_form_valid or not is_options_valid:

            context = get_sidebar_context(request)
            context['exam'] = question.exam
            context['question_creation_form'] = form
            context['question_options'] = question_options

            messages.error(request, 'Please correct the errors mentioned below and try again!')
            return render(request, 'exams/exam_question_create_form.html', context)

        form.save()

        # Delete all the options related to this particular question.
        # We will add the new options again.
        question.options.all().delete()

        if is_mcq:

            # bulk_create() does not returns the list of ids (i.e. pks) of the objects inserted
            # in the DB. Only PostgreSQL supports this.
            # See: https://stackoverflow.com/questions/15933689/how-to-get-primary-keys-of-objects-created-using-django-bulk-create
            # So, for now, insert all the options individually.
            option_ids = []
            for option in question_options:
                option.question = question
                option.save()
                option_ids.append(option.pk)

            # Directly passing the ids to add() results in just query as compared to N queries if all the
            # options are added individually.
            question.options.add(*option_ids)

        messages.success(request, 'The question was successfully updated.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamQuestionDeleteView(View):

    def post(self, request, classroom_id, exam_id, question_id):    
        question = get_object_or_404(
            Question.objects.select_related('exam', 'exam__classroom', 'exam__classroom__teacher').only(
                'id',
                'exam__id',
                'exam__classroom__id',
                'exam__classroom__teacher__id'
            ).prefetch_related('options'),
            id = question_id
        )

        if request.user != question.exam.classroom.teacher or question.exam.id != int(exam_id) or question.exam.classroom.id != int(classroom_id):
            raise Http404

        question.delete()

        messages.success(request, 'The question was successfully deleted.')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class ExamStartView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom'),
            id = exam_id
        )

        if exam.classroom.id != classroom_id or not Exam.objects.filter(id = exam_id, students__in = [request.user]).exists():
            raise Http404

        # Check if the exam has started or not.
        # If not, return the appropriate message.
        if not exam.has_started():
            messages.error(request, f'The examination/assignment - {exam.title} has not started yet!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # Check if the exam has ended.
        # If yes, return the appropriate message.
        if exam.has_ended():
            messages.error(request, f'The examination/assignment - {exam.title} has ended!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        submission = None
        # Try creating a submission for the current user.
        # If the submission is already present, return the appropriate message.
        try:
            submission = Submission.objects.create(exam = exam, student = request.user)
        except IntegrityError:
            messages.warning(f'You cannot start the examination/assignment again!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        return redirect('submission_detail', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission.id)

class ExamResumeView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(Exam.objects.select_related('classroom'), id = exam_id)

        if exam.classroom.id != classroom_id or not Exam.objects.filter(id = exam_id, students__in = [request.user]).exists():
            raise Http404

        # Check if the exam has started or not.
        # If not, return the appropriate message.
        if not exam.has_started():
            messages.error(request, f'The examination/assignment - {exam.title} has not started yet!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # Check if the exam has ended.
        # If yes, return the appropriate message.
        if exam.has_ended():
            messages.error(request, f'The examination/assignment - {exam.title} has ended!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # Check if the exam is resumable or not.
        # If not, return the appropriate message.
        if not exam.is_resumable:
            messages.error(request, f'The examination/assignment - {exam.title} is not resumable! That is, once submitted, you cannot resume!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # Fetch the submission of the student and perform the appropriate redirection.
        submission = get_object_or_404(Submission, exam = exam, student = request.user)
        return redirect('submission_detail', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission.id)

class ExamEndView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom').only(
                'id',
                'title',
                'classroom__id'
            ),
            id = exam_id
        )

        if exam.classroom.id != classroom_id or not Exam.objects.filter(id = exam_id, students__in = [request.user]).exists():
            raise Http404

        submission = get_object_or_404(Submission, exam = exam, student = request.user)

        if submission.is_submitted:
            messages.error(request, f'Your examination/assignment submission for \'{exam.title}\' has already been recorderd!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        submission.is_submitted = True
        submission.save()
 
        messages.success(request, f'Your examination/assignment submission for \'{exam.title}\' was successful!')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

class SubmissionDetailView(View):

    def get(self, request, classroom_id, exam_id, submission_id):
        submission = get_object_or_404(
            Submission.objects.select_related(
                'exam',
                'exam__classroom',
                'student'
            ).prefetch_related(
                'answers',
                'answers__options',
                'answers__question',
                'exam__questions',
                'exam__questions__options'
            ).only(
                'id',
                'started_at',
                'ended_at',
                'is_submitted',
                'exam__id',
                'exam__title',
                'exam__start_time',
                'exam__end_time',
                'exam__is_open_exam',
                'exam__duration',
                'exam__classroom__id',
                'exam__classroom__title',
                'student__id'
            ),
            id = submission_id
        )

        if request.user != submission.student or submission.exam.classroom.id != classroom_id or submission.exam.id != exam_id:
            raise Http404

        # If the user has already made the submission.
        if submission.is_submitted:
            messages.error(request, 'You have already taken this examination/assignment!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # If the exam is over, but the submission has not been made.
        # In such cases, mark the exam as submitted, and return the appropriate messages. 
        if submission.exam.has_ended():
            submission.is_submitted = True
            submission.save()

            messages.error(request, 'You have already taken this examination/assignment!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # Fetch all the questions of the exams and the answers that have been 'saved' by the user/student.
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

        context = {
            'submission': submission,
            'exam': submission.exam,
            'questions_and_answer': questions_and_answer,
            'time_left': time_left(submission)
        }
        return render(request, 'exams/submission_detail.html', context)

class AnswerView(View):

    def post(self, request, classroom_id, exam_id, submission_id, question_id):
        submission = get_object_or_404(
            Submission.objects.select_related('exam', 'exam__classroom', 'student'),
            id = submission_id
        )

        question = get_object_or_404(
            Question.objects.select_related('exam'),
            id = question_id
        )

        if request.user != submission.student or submission.exam.classroom.id != classroom_id or submission.exam.id != exam_id or question.exam.id != exam_id:
            raise Http404

        if time_left(submission) < 0:
            messages.error(request, 'This examination/assignment is over!')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        # .get() raise DoesNotExist exception whereas .filter() returns None if no record is found.
        answer = Answer.objects.filter(student = request.user, question = question).first()

        # If the answer is to be cleared -
        if 'clear' in request.POST:
            if not answer is None:
                answer.delete()
            return JsonResponse({'status': 'success', 'message': 'Answer cleared successfully!'})

        # If the answer is to be saved - 
        if question.is_mcq():
            # If no option was selected, return the apporpriate message.
            # We cannot save an empty response.
            if not 'option' in request.POST:
                return JsonResponse({'status': 'fail', 'message': 'Please select atleast one option!'}, status = 400)
        else:
            # For subjective question, check for non-empty strings and return the appropriate message.
            if request.POST.get('body') == '':
                return JsonResponse({'status': 'fail', 'message': 'Please provide an answer!'}, status = 400)

        # If no answer (submitted by the current user) was found, create one.
        if answer is None:
            answer = Answer.objects.create(
                submission = submission,
                question = question,
                student = request.user,
                body = request.POST['body'] if 'body' in request.POST else None
            )
        else:
            # Else, just update the 'body' of the answer.
            # We will updating the options (in case of MCQs below).
            answer.body = request.POST['body'] if 'body' in request.POST else None
            answer.save()

        if question.is_mcq():
            # Clear the previously submitted option(s).
            answer.options.clear()

            # Save the new options.
            option_ids = []
            for option in request.POST.getlist('option'):
                option_ids.append(Option.objects.get(id = int(option)).pk)
            
            # Calling add() with just the ids results in a single query!
            answer.options.add(*option_ids)

        return JsonResponse({'status': 'success', 'message': 'Answer added successfully!'})

class SubmissionEvaluateView(View):

    def get(self, request, classroom_id, exam_id, submission_id):
        submission = get_object_or_404(
            Submission.objects.select_related('student').prefetch_related(
                'exam',
                'exam__classroom',
                'exam__questions',
                'exam__questions__options',
                'answers',
                'answers__question',
                'answers__options'
            ),
            id = submission_id
        )

        if submission.exam.id != int(exam_id) or submission.exam.classroom.id != int(classroom_id):
            raise Http404

        # Fetch all the questions of the exams and the answers that have been 'saved' by the user/student.
        questions_and_answer = {}

        for question in submission.exam.questions.all():
            question_id = str(question.id)

            questions_and_answer[question_id] = {}
            questions_and_answer[question_id]['question'] = question
            questions_and_answer[question_id]['answer'] = None
    
        for answer in submission.answers.all():
            question_id = str(answer.question.id)

            questions_and_answer[question_id]['answer'] = answer

        context = get_sidebar_context(request)
        context['submission'] = submission
        context['submissions'] = context['submissions'] = Submission.objects.filter(exam = submission.exam, is_submitted = True).select_related('student')
        context['questions_and_answer'] = questions_and_answer

        return render(request, 'exams/submission_detail_teacher.html', context)

    def post(self, request, classroom_id, exam_id, submission_id):
        submission = get_object_or_404(
            Submission.objects.select_related('student').prefetch_related(
                'exam',
                'exam__classroom',
                'exam__classroom__teacher'
            ),
            id = submission_id,
            is_submitted = True
        )

        if request.user != submission.exam.classroom.teacher or submission.exam.id != int(exam_id) or submission.exam.classroom.id != int(classroom_id):
            raise Http404
        
        try:
            response = evaluate_single_submission.delay(
                submission.exam.classroom.teacher.id,
                submission.student.id,
                submission.exam.id,
                submission_id
            )
            logger.info(f'Job scheduled for evaluating a single submission (evaluate_single_submission) for submission - {submission_id}.')
        except Exception as e:
            logger.exception(f'Could not schedule job for evaluating a single submission (evaluate_single_submission) for submission - {submission_id}. Exception - {e}')

            messages.error(request, 'An internal server error ocurred! Please try again later.')
            return redirect('submission_evaluate', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission_id)

        messages.success(request, 'You will be emailed once the submission has been evaluated!')
        return redirect('submission_evaluate', classroom_id = classroom_id, exam_id = exam_id, submission_id = submission_id)

class AnswerEvaluateView(View):

    def post(self, request, classroom_id, exam_id, submission_id, question_id):
        submission = get_object_or_404(
            Submission.objects.select_related('exam', 'exam__classroom', 'exam__classroom__teacher', 'student'),
            id = submission_id
        )

        question = get_object_or_404(
            Question.objects.select_related('exam'),
            id = question_id
        )

        if request.user != submission.exam.classroom.teacher or submission.exam.classroom.id != classroom_id or submission.exam.id != exam_id or question.exam.id != exam_id:
            raise Http404

        if question.is_mcq():
            return JsonResponse({'status': 'fail', 'message': 'MCQs cannot be evaluated manually.'}, status = 0)

        try:
            marks = float(request.POST.get('marks'))
        except TypeError:
            return JsonResponse({'status': 'fail', 'message': 'Marks should be an integer/decimal.'}, status = 400)
            
        if marks > question.marks:
            return JsonResponse({'status': 'fail', 'message': 'Marks cannot be greater than the maximum scorable marks.'}, status = 400)

        answer = get_object_or_404(Answer, question = question, student = submission.student)

        answer.marks = marks
        answer.is_evaluated = True
        answer.save()

        return JsonResponse({'status': 'success', 'message': 'Marks saved successfully.'})


class ExamEvaluateView(View):

    def post(self, request, classroom_id, exam_id):
        exam = get_object_or_404(
            Exam.objects.select_related('classroom', 'classroom__teacher'),
            id = exam_id
        )

        if request.user != exam.classroom.teacher or exam.classroom.id != int(classroom_id):
            raise Http404
        
        try:
            response = evaluate_all_submissions.delay(
                request.user.id,
                exam.id
            )
            logger.info(f'Job scheduled for evaluating all submissions (evaluate_all_submissions) for exam - {exam_id}.')
        except Exception as e:
            logger.exception(f'Could not schedule job for evaluating all submissions (evaluate_all_submissions) for exam - {exam_id}. Exception - {e}')

            messages.error(request, 'An internal server error ocurred! Please try again later.')
            return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)

        messages.success(request, 'You will be emailed once all the submissions have been evaluated!')
        return redirect('exam_detail', classroom_id = classroom_id, exam_id = exam_id)
