import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kouekam_hub.settings")
django.setup()

User = get_user_model()
username = 'kouekam'
email = os.getenv('SUPERUSER_EMAIL', 'kouekamkamgouluc@gmail.com')
password = 'kklkinkklk'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully with email '{email}'.")
else:
    user = User.objects.get(username=username)
    # Update email and password to ensure they match the expected values
    user.email = email
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Superuser '{username}' updated with email '{email}'.")
