from django.db import migrations, models


def set_initial_status(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    BlogPost.objects.filter(published_date__isnull=False).update(status='published')
    BlogPost.objects.filter(published_date__isnull=True).update(status='draft')


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_increase_slug_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Short summary for cards, SEO previews, and social sharing.'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('published', 'Published')], default='draft', max_length=20),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags', max_length=500),
        ),
        migrations.RunPython(set_initial_status, migrations.RunPython.noop),
    ]
