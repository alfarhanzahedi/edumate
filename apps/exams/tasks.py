import logging
from smtplib import SMTPException

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core import mail
from django.utils.html import strip_tags

from celery import shared_task
from celery.utils.log import get_task_logger

from apps.accounts.models import User
from .models import Exam
from .models import Submission
from .models import Option

logger = get_task_logger(__name__)

def evaluate_single_submission_helper(submission_id):
    logger.info(f'Evaluating submission - {submission_id}.')

    submission = Submission.objects.prefetch_related(
        'answers',
        'answers__question',
        'answers__options'
    ).get(id = submission_id)
    
    for answer in submission.answers.all():
        if answer.is_evaluated:
            continue

        if answer.question.is_mcq():

            correct_option_ids = [option.id for option in answer.question.options.all() if option.is_answer == True]
            option_ids_in_answer = [option.id for option in answer.options.all()]

            if (option_ids_in_answer == correct_option_ids):
                answer.marks = answer.question.marks
            else:
                answer.marks = -1 * answer.question.negative_marks
        else:
            # Ignore for subjective questions as they are to be evaluated by the teacher.
            pass

        answer.is_evaluated = True
        answer.save()
    
    submission.is_evaluated = True
    submission.save()

    logger.info(f'Submission evaluation complete for - {submission_id}.')

@shared_task
def evaluate_single_submission(teacher_id, student_id, exam_id, submission_id):
    logger.info(f'Task started - evaluate_single_submission for submission - {submission_id}.')

    teacher = None
    student = None
    exam = None
    submission = None

    # ToDo: Handle exceptions with proper logging.

    try:
        teacher = User.objects.get(id = teacher_id)
    except User.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return
    
    try:
        student = User.objects.get(id = student_id)
    except User.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return

    try:
        exam = Exam.objects.get(id = exam_id)
    except Exam.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return
    
    try:
        submission = Submission.objects.get(id = submission_id)
    except Submission.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return

    evaluate_single_submission_helper(submission_id)    

    subject = f'Submission Evaluation Complete for {student.full_name()} - Edumate'
    html_message = render_to_string('exams/evaluate_single_submission_email.html', {
        'teacher': teacher,
        'student': student,
        'exam': exam
    })
    plain_message = strip_tags(html_message)

    try:
        mail.send_mail(
            subject,
            plain_message,
            'admin@edumate.com',
            [teacher.email],
            html_message = html_message,
            fail_silently = False
        )
    except (ConnectionRefusedError, SMTPException) as e:
        logger.exception(f'Evaluation completion email could not be sent. Exception - {e}.')

    logger.info(f'Task ended - evaluate_single_submission for submission - {submission_id}.')

@shared_task
def evaluate_all_submissions(teacher_id, exam_id):
    logger.info(f'Task started - evaluate_all_submissions for exam - {exam_id}.')

    teacher = None
    exam = None

    # ToDo: Handle exceptions with proper logging.

    try:
        teacher = User.objects.get(id = teacher_id)
    except User.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return

    try:
        exam = Exam.objects.get(id = exam_id)
    except Exam.DoesNotExist as e:
        logger.exception(f'Exception - {e}.')
        return

    submissions = Submission.objects.filter(exam = exam, is_submitted = True)

    for submission in submissions:
        evaluate_single_submission_helper(submission.id)
    
    subject = f'All Submission Evaluation Complete for {exam.title} - Edumate'
    html_message = render_to_string('exams/evaluate_all_submissions_email.html', {
        'teacher': teacher,
        'exam': exam
    })
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            'admin@edumate.com',
            [teacher.email],
            html_message = html_message,
            fail_silently = False
        )
    except (ConnectionRefusedError, SMTPException) as e:
        logger.exception(f'Evaluation completion email could not be sent. Exception - {e}.')

    logger.info(f'Task ended - evaluate_all_submissions for exam - {exam_id}.')
