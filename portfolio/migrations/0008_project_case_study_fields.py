from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_contactlead'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='problem',
            field=models.TextField(blank=True, help_text='What problem or opportunity this project addressed.'),
        ),
        migrations.AddField(
            model_name='project',
            name='results',
            field=models.TextField(blank=True, help_text='Outcomes, metrics, lessons, or impact.'),
        ),
        migrations.AddField(
            model_name='project',
            name='role',
            field=models.CharField(blank=True, help_text='Your role or ownership in the project.', max_length=160),
        ),
        migrations.AddField(
            model_name='project',
            name='solution',
            field=models.TextField(blank=True, help_text='How the project solved the problem.'),
        ),
        migrations.AddField(
            model_name='project',
            name='summary',
            field=models.CharField(blank=True, help_text='Short portfolio-card summary.', max_length=280),
        ),
        migrations.AddField(
            model_name='project',
            name='timeline',
            field=models.CharField(blank=True, help_text='Project duration or date range.', max_length=120),
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-is_featured', '-created_at'], 'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
    ]
