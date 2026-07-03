import sys
import threading
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        if 'runserver' in sys.argv:
            def run_check():
                from django.core.management import call_command
                call_command('check_birthday_notifications', verbosity=0)

            threading.Thread(target=run_check, daemon=True).start()
