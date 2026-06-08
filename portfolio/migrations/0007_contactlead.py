from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_alter_project_slug_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(blank=True, max_length=200)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('closed', 'Closed'), ('spam', 'Spam')], default='new', max_length=20)),
                ('source_path', models.CharField(blank=True, max_length=255)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_error', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True, help_text='Private follow-up notes for this lead.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Contact Lead',
                'verbose_name_plural': 'Contact Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='contactlead',
            index=models.Index(fields=['status', '-created_at'], name='portfolio_c_status_14adcd_idx'),
        ),
        migrations.AddIndex(
            model_name='contactlead',
            index=models.Index(fields=['email'], name='portfolio_c_email_e746c8_idx'),
        ),
    ]
