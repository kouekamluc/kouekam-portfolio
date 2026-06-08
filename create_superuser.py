import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kouekam_hub.settings")
django.setup()

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'kouekam')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if not email or not password:
    raise SystemExit(
        "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD must be set to create a superuser."
    )

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully with email '{email}'.")
else:
    user = User.objects.get(username=username)
    user.email = email
    user.is_superuser = True
    user.is_staff = True
    user.save(update_fields=['email', 'is_superuser', 'is_staff'])
    print(f"Superuser '{username}' already exists; email and staff flags updated.")
