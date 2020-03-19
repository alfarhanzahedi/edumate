from django import forms

from .models import Exams
from .models import Questions
from .models import Options
from apps.accounts.models import User

class ExamCreationForm(forms.ModelForm):
    class Meta:
        model = Exams
        fields = ('title', 'description','instructions','duration','students','active_date','active_time',)
        help_texts = {
            'title': 'Name of the Examination',
            'description': 'Subjects',
        }
class AddQuestionsForm(forms.ModelForm): 
    class Meta:
        model = Questions
        fields = ('q_type','body','marks','img',)

class AddOptionsForm(forms.ModelForm):
    class Meta:
        model =  Options
        fields = ('text','ans',)


