from django import forms
from django.utils import timezone
from django.forms import ValidationError

from .models import Exam
from .models import Question
from .models import Answer

class ExamCreationForm(forms.ModelForm):
    DATETIME_INPUT_FORMATS = [
       '%Y-%m-%d %H:%M'
    ]

    start_time = forms.DateTimeField(
        input_formats = DATETIME_INPUT_FORMATS,
        label = 'Start date and time',
        help_text = 'Start date and time for the examination/assignment. <br>' +
                    'The input format should be YYYYY-MM-DD HH:MM. Example: 2020-03-13 10:00. <br>'+
                    '24-hour format is to be followed.',
        widget=forms.TextInput(attrs={'placeholder': '2020-03-13 10:00'})

    )
    end_time = forms.DateTimeField(
        input_formats = DATETIME_INPUT_FORMATS,
        label = 'End date and time',
        help_text = 'End date and time for the examination/assignment. <br>' +
                    'The input format should be YYYY-MM-DD HH:MM. Example: 2020-03-14 13:00. <br>'+
                    '24-hour format is to be followed.',
        widget=forms.TextInput(attrs={'placeholder': '2020-03-13 10:00'})
    )

    class Meta:
        model = Exam
        fields = ('title', 'about', 'instructions', 'is_open_exam', 'is_resumable', 'start_time', 'end_time', 'duration', 'students')
        widgets = {
            'students': forms.SelectMultiple(attrs={'data-placeholder': 'Start typing to get suggestions...'})
        }
        labels = {
            'about': 'Description',
            'is_open_exam': 'Is open exam?',
            'is_resumable': 'Is resumable?'
        }
        help_texts = {
            'title': 'A suitable title for the examination/assignment. For example, CSEN 3012 - Assignment I.',
            'about': 'A short description for the examination/assignment.',
            'instructions': 'Instructions pertaining to the examination/assignment.',
            'is_open_exam': 'This option is not required if you want to schedule an examination/assessment. You are required to enter the start date, start time, and test duration.<br>' +
                            'If this option is enabled, then the students can attempt the test between the set start date/time and end date/time.' +
                            'Each candidate gets the same amount of time as the set test duration.',
            'is_resumable': 'This option determines if the examination/assignment can be resumed or not.',
            'duration': 'The duration for the examination/assignment (in minutes).<br>' +
                        'If left blank, the duration is from start time to end time.',
            'students': 'The students that can/need to take the examination/assignment.<br>' +
                        'A unique code will also be generated for the examination/assignment upon creation. ' +
                        'Students can join and take the examination/assignment via the unique code too.'
        }
    
    def clean(self):
        cleaned_data = self.cleaned_data
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        duration = cleaned_data.get('duration')

        # If the provided start and end datetime are invalid (i.e. not in the required format),
        # ignore further checking and return cleaned_data.
        # This is required to avoid errors down the line as start_time and end_time are set to None
        # if the input is invalid.
        if not start_time or not end_time:
            return cleaned_data

        # If self.instance is not set i.e. the form submitted requires the creation of the exam and not updation.
        if not self.instance.pk and start_time < timezone.now():
            self._errors['start_time'] = self.error_class(['The date/time cannot be set in the past!'])
            del cleaned_data['start_time']
        
        # If the form requires the updation of an exam and the update is changing the start_time of
        # the exam to a datetime which is past the time the exam was created, raise an error!
        if self.instance.pk and self.instance.created_at > start_time:
            self._errors['start_time'] = self.error_class(['The date/time cannot be past the time the examination/assignment was created!'])
            del cleaned_data['start_time']

        if end_time < start_time:
            self._errors['end_time'] = self.error_class(['End date and time cannot be earlier than start date and time!'])
            del cleaned_data['end_time']
        
        if duration and (duration * 60 > (end_time - start_time).total_seconds()):
            self._errors['duration'] = self.error_class(['The duration does not match with the difference between start and end date and time.'])
            del cleaned_data['duration']
        
        return cleaned_data

class ExamJoinForm(forms.Form):
    unique_code = forms.CharField(
                    min_length = 6, 
                    max_length = 6, 
                    required = True,
                    help_text = 'The unique code shared by your teacher.'
                )

class ExamQuestionCreationForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('type', 'body', 'solution','marks', 'negative_marks')
        help_texts = {
            'type': 'The type of the question.',
            'body': 'The actual question body.',
            'solution': 'The solution to the question. If the question is an MCQ, explanations to solutions can be provided here.',
            'marks': 'The maximum marks for the question.',
            'negative_marks': 'Any negative marks associated with the question. Does not effect subjective type questions.'
        }

class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('body',)
