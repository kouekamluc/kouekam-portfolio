import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kouekam_hub.settings")
django.setup()

User = get_user_model()
username = 'kouekam'
email = os.getenv('SUPERUSER_EMAIL', 'kouekam@example.com')
password = 'kklkinkklk'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully.")
else:
    print(f"Superuser '{username}' already exists.")
