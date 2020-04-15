from django.core.cache import cache

from .models import User

def invalidate_cache_for__get_user(username):
    return cache.delete(f'user-{username}')

def get_user(username):
    user = cache.get(f'user-{username}')

    if user is None:
        cache.set(f'user-{username}', User.objects.get(username = username))
        user = cache.get(f'user-{username}')

    return user
