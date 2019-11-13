from django import forms

class ClassroomCreationForm(forms.ModelForm):

    class Meta:
        fields = ('title', 'description', )