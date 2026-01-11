# Generated manually to fix slug max_length issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
