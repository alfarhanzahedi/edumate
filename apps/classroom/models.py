from django.db import models

from mdeditor.fields import MDTextField

from apps.accounts.models import User

class Classroom(models.Model):
    teacher = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'teacher_of_classrooms')
    students = models.ManyToManyField(User, related_name = 'student_of_classrooms')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    unique_code = models.CharField(max_length = 6)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.title}'

class Post(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE, related_name = 'posts')
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'author_of_posts')
    post_raw = MDTextField()
    post_html = models.TextField()

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.id}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'comments')
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'author_of_comments')
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.id}'
    