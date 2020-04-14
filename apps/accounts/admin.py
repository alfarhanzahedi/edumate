from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .forms import CustomUserChangeForm
from .models import User
from .models import Student
from .models import Teacher

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'username', )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('role',),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {
            'fields': ('is_student', 'is_teacher', ),
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass
