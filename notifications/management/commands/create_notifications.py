from django.core.management.base import BaseCommand
from notifications.services import create_all_notifications


class Command(BaseCommand):
    help = 'Create notifications for tasks, habits, goals, and study reminders'

    def handle(self, *args, **options):
        self.stdout.write('Creating notifications...')
        create_all_notifications()
        self.stdout.write(self.style.SUCCESS('Successfully created notifications'))

