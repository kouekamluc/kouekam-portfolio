# Generated manually for learning record expansion.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academic", "0002_alter_course_options_alter_flashcard_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="completion_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="course",
            name="effort_hours",
            field=models.PositiveIntegerField(default=0, help_text="Estimated total learning or practice hours"),
        ),
        migrations.AddField(
            model_name="course",
            name="learning_type",
            field=models.CharField(
                choices=[
                    ("course", "University Course"),
                    ("certification", "Certification"),
                    ("training", "Professional Training"),
                    ("self_study", "Self-Study"),
                    ("research", "Research / Thesis"),
                ],
                default="course",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="outcome",
            field=models.CharField(
                blank=True,
                help_text="Certificate earned, grade summary, promotion impact, etc.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="provider",
            field=models.CharField(blank=True, help_text="University, platform, or employer", max_length=255),
        ),
        migrations.AddField(
            model_name="course",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
