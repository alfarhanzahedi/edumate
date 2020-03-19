from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from apps.classroom.models import Classroom
from apps.accounts.models import User
from apps.accounts.decorators import teacher_required

from .models import Exams
from .models import Options
from .models import Questions

import uuid
from .forms import ExamCreationForm
from .forms import AddQuestionsForm
from .forms import AddOptionsForm
def created_classroom(classroom, user):
    if classroom.teacher == user:
        return True
    return False

class CreateExam(View):

    
    @method_decorator([login_required, teacher_required])
    def get(self, request,id):
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = id)
        if not created_classroom(classroom, request.user):
            raise Http404
        form = ExamCreationForm()
        student_choices = classroom.students.all()
        students = [(i.id,i) for i in student_choices]
       # for i in student_choices:
           # student_name = User.object.get(i)
        #print(form)
        return render(request,'exams_create.html',{'form':form,'students':students,'current_classroom':classroom})
    def post(self,request,id):
        classroom = Classroom.objects.get(id = id)
        
        form = ExamCreationForm(request.POST)
        #print(request.POST)
        #print(form.errors)
        if form.is_valid():
            exam = form.save(commit = False)
            exam.unique_code = uuid.uuid4().hex[:6]
            exam.classroom = classroom
            exam.save()
            students=form.cleaned_data.get('students')

            for i in students:
                exam.students.add(i)
            exam.save()
            #print("Exam  created")
            messages.success(request,f'Exam with unique code - {exam.unique_code} now created. Start adding questions!')
            return redirect('add_question',id=id,e_id=exam.id)
        messages.error(request,f'Please enter valid details. Try again!')    
        return redirect("create_exam",id=id)

class AddQuestions(View):
    @method_decorator([login_required, teacher_required])
    def get(self,request,id,e_id):
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = id)
        if not created_classroom(classroom, request.user):
            raise Http404
        form = AddQuestionsForm()
       
        form2 = AddOptionsForm()
        #print(form2)
        return render(request,'add_questions.html',{'form':form,'form2':form2})
    
    def post(self,request,id,e_id):
        #if 'Add_Q' in request.POST:
            form = AddQuestionsForm(request.POST, request.FILES)
            exam = Exams.objects.get(id=e_id)
            if form.is_valid():
                question = form.save(commit=False)
                question.exam=exam
                question.save()
                #print(t_marks)
                if question.q_type == '1' or question.q_type == '2':
                    option_text = request.POST.getlist('text')
                    ans_list = request.POST.getlist('ans')
                    
                    i=1
                    for ot in option_text:
                        ans = False
                        if str(i) in ans_list:
                            ans = True
                        option_new = Options.objects.create(question = question,text=ot,ans=ans)
                        i+=1
                
                if 'Finish' in request.POST:
                    marks = Questions.objects.filter(exam=exam).values('marks')
                    t_marks = 0
                    for m in marks:
                        t_marks+=m['marks']
                #print(marks)
                #print(t_marks)
                    exam.total_marks = t_marks
                    exam.save()
                return redirect('add_question',id=id,e_id=e_id)
            return redirect("/")


