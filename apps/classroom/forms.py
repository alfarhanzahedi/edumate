from django import forms

from .models import Classroom
from .models import Post
from .models import Comment

class ClassroomCreationForm(forms.ModelForm):

    class Meta:
        model = Classroom
        fields = ('title', 'description', )
        help_texts = {
            'title': 'A suitable title for the classroom. For example, CSEN 3201.',
            'description': 'A short description for the classroom.',
        }

class ClassroomJoinForm(forms.Form):
    unique_code = forms.CharField(
                    min_length = 6, 
                    max_length = 6, 
                    required = True,
                    help_text = 'The unique code shared by your teacher.'
                )
    def clean_unique_code(self):
        unique_code = self.cleaned_data.get('unique_code')
        try:
            Classroom.objects.get(unique_code = unique_code)
        except Classroom.DoesNotExist:
            raise forms.ValidationError('The code is not associated with any classroom!')
        return unique_code

class ClassroomPostCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('post_raw', )
        help_texts = {
            'post': 'Keep it simple and brief!'
        }
        
