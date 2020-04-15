from django.views import View
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from smtplib import SMTPException

from apps.pages.common_functions import get_sidebar_context
from apps.classroom.models import Post

from .models import User
from .models import Student
from .models import Teacher
from .forms import CustomUserCreationForm
from .forms import UserProfileChangeForm
from .tokens import account_activation_token
from .constants import Role
from .helpers import get_user
from .helpers import invalidate_cache_for__get_user

class SignUp(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'accounts/registration/signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = False
            user.save()

            role = int(form.cleaned_data.get('role'))
            if role == Role.STUDENT:
                user.is_student = True
                Student.objects.create(user = user)
            else:
                user.is_teacher = True
                Teacher.objects.create(user = user)
            user.save()
            
            current_site = get_current_site(request)
            subject = 'Activate your EduMate account'
            message = render_to_string('accounts/registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            user.email_user(subject, '', html_message = message,  from_email = 'EduMate Support<support@edumate.com>')
            return render(request, 'accounts/registration/account_activation_sent.html')
        return render(request, 'accounts/registration/signup.html', {'form': form})

class Activate(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk = uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Email-id confirmed successfully! Account activated.')
            return redirect('/')
        else:
            return render(request, 'accounts/registration/account_activation_invalid.html')

class UserProfileView(View):
    
    @method_decorator(login_required)
    def get(self, request, username):
        required_user = None

        if username != request.user.username:
            try:
                required_user = get_user(username)
            except User.DoesNotExist:
                raise Http404
        else:
            required_user = request.user

        context = get_sidebar_context(request)
        context['context_user'] = required_user

        post_list = None
        if required_user == request.user:
            # If the user is visiting their profile, then show all the posts made by them in all the classes.
            post_list = Post.objects.select_related('user', 'classroom', 'classroom__teacher') \
                                    .only(
                                        'post',
                                        'updated_at',
                                        'user__username',
                                        'user__first_name',
                                        'user__last_name',
                                        'user__profile_picture',
                                        'classroom__title',
                                        'classroom__teacher__id'
                                    ) \
                                    .filter(user = required_user).order_by('-updated_at')
        else:
            # If the user is visiting someone else's profile, say As, then show the posts made by A only in the classrooms where:
            # - the current user is the teacher, or
            # - the current user is a fellow classmate.
            post_list = Post.objects.distinct().select_related('user', 'classroom', 'classroom__teacher') \
                                               .only(
                                                    'post',
                                                    'updated_at',
                                                    'user__username',
                                                    'user__first_name',
                                                    'user__last_name',
                                                    'user__profile_picture',
                                                    'classroom__title',
                                                    'classroom__teacher__id'
                                                ) \
                                               .filter(Q(user = required_user) & (Q(classroom__students__in = [request.user]) | Q(classroom__teacher = request.user))).order_by('-updated_at')

        page = request.GET.get('page', 1)

        paginator = Paginator(post_list, 2)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['posts'] = posts
        
        return render(request, 'accounts/user_profile.html', context)

class UserProfileChangeView(View):

    @method_decorator(login_required)
    def get(self, request, username):
        context = get_sidebar_context(request)
        
        if request.user.username != username:
            return redirect('user_profile', username = request.user.username)

        context['profile_change_form'] = UserProfileChangeForm(instance = request.user)
        context['password_change_form'] = PasswordChangeForm(request.user)
        return render(request, 'accounts/user_profile_change.html', context)

    @method_decorator(login_required)
    def post(self, request, username):
        if request.user.username != username:
            return redirect('user_profile', username = request.user.username)
        
        context = None
        if 'user_profile_change_submit' in request.POST:
            profile_change_form = UserProfileChangeForm(request.POST, request.FILES, instance = request.user, request = request)
            user = request.user

            if profile_change_form.is_valid():
                profile_change_form.save()

                invalidate_cache_for__get_user(username)

                messages.success(request, 'Your information was updated successfully!')
                return redirect('user_profile', username = request.user.username)

            # If the form is not valid, generate the appropriate context.
            context = get_sidebar_context(request)
            context['profile_change_form'] = profile_change_form
            context['password_change_form'] = PasswordChangeForm(request.user)
            messages.error(request, 'Please correct the errors mentioned below and try again!')

        elif 'user_password_change_submit' in request.POST:
            password_change_form = PasswordChangeForm(request.user, request.POST)

            if password_change_form.is_valid():
                user = password_change_form.save()

                update_session_auth_hash(request, user)
                invalidate_cache_for__get_user(username)

                messages.success(request, 'Your password was successfully updated!')
                return redirect('user_profile', username = request.user.username)

            # If the form is not valid, generate the appropriate context.
            context = get_sidebar_context(request)
            context['password_change_form'] = password_change_form
            context['profile_change_form'] = UserProfileChangeForm(instance = request.user)
            messages.error(request, 'Please correct the errors mentioned below and try again!')

        return render(request, 'accounts/user_profile_change.html', context)
