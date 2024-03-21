
from django.contrib.auth import get_user_model
User = get_user_model()


if not User.objects.filter(is_superuser=True).first():
    user = User.objects.create(
        username = 'ockham',
        email = 'ockham-byron@protonmail.com',
        is_superuser = True,
    )
    user.set_password('FakePassword')
    user.save()