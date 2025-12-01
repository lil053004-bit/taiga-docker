from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Initialize Taiga on first startup - create superuser and run migrations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Taiga Initialization ==='))
        self.stdout.write('')

        admin_username = os.getenv('AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')
        admin_email = os.getenv('AUTO_ASSIGN_ADMIN_EMAIL', 'lhweave@gmail.com')
        admin_password = os.getenv('POSTGRES_PASSWORD', 'A52290120a')

        User = get_user_model()

        try:
            user = User.objects.get(username=admin_username)
            self.stdout.write(self.style.SUCCESS(f'✓ Superuser "{admin_username}" already exists'))

            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Updated superuser flags for "{admin_username}"'))

        except User.DoesNotExist:
            try:
                user = User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password
                )
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.lang = 'zh-Hans'
                user.save()

                self.stdout.write(self.style.SUCCESS(f'✓ Created superuser "{admin_username}"'))
                self.stdout.write(self.style.SUCCESS(f'  Email: {admin_email}'))
                self.stdout.write(self.style.SUCCESS(f'  Password: {admin_password}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to create superuser: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Initialization Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Login at /admin/ with username: {admin_username}'))
        self.stdout.write('')
