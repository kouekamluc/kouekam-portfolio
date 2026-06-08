from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_alter_businessidea_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessidea',
            name='execution_fit_score',
            field=models.PositiveSmallIntegerField(default=3, help_text='1-5 score for your ability to execute', validators=[MinValueValidator(1), MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='businessidea',
            name='market_demand_score',
            field=models.PositiveSmallIntegerField(default=3, help_text='1-5 score for market demand', validators=[MinValueValidator(1), MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='businessidea',
            name='revenue_potential_score',
            field=models.PositiveSmallIntegerField(default=3, help_text='1-5 score for revenue potential', validators=[MinValueValidator(1), MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='businessidea',
            name='risk_level_score',
            field=models.PositiveSmallIntegerField(default=3, help_text='1-5 risk score where 5 is highest risk', validators=[MinValueValidator(1), MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='businessidea',
            name='strategic_fit_score',
            field=models.PositiveSmallIntegerField(default=3, help_text='1-5 score for alignment with your goals', validators=[MinValueValidator(1), MaxValueValidator(5)]),
        ),
    ]
