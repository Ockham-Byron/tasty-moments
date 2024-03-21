
from users.models import CustomUser

if not CustomUser.objects.filter(is_superuser=True).first():
    user = CustomUser.objects.create(
        username = 'ockham',
        email = 'ockham-byron@protonmail.com',
        is_superuser = True,
    )
    user.set_password('FakePassword')
    user.save()