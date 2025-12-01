from django.core.management.base import BaseCommand
from taiga.users.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Set all users language to Chinese (zh-Hans)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only-unset',
            action='store_true',
            help='Only update users who have no language set',
        )
        parser.add_argument(
            '--lang',
            type=str,
            default='zh-Hans',
            help='Language code to set (default: zh-Hans)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without actually updating',
        )

    def handle(self, *args, **options):
        only_unset = options['only_unset']
        language = options['lang']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Setting User Language to Chinese'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        if only_unset:
            users = User.objects.filter(lang__isnull=True) | User.objects.filter(lang='')
            self.stdout.write(f"Mode: Update only users without language set")
        else:
            users = User.objects.all()
            self.stdout.write(f"Mode: Update ALL users")

        self.stdout.write(f"Language: {language}")
        self.stdout.write(f"Total users to update: {users.count()}")
        self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('')

        updated_count = 0
        skipped_count = 0

        for user in users:
            current_lang = user.lang or 'not set'

            if not dry_run:
                user.lang = language
                user.save(update_fields=['lang'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ User '{user.username}' ({user.email}): {current_lang} → {language}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    f"  User '{user.username}' ({user.email}): {current_lang} → {language}"
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f"Total users processed: {updated_count}")
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"✓ Successfully updated {updated_count} users to {language}"))
        else:
            self.stdout.write(self.style.WARNING(f"DRY RUN: Would update {updated_count} users to {language}"))
            self.stdout.write('')
            self.stdout.write('Run without --dry-run to apply changes')
        self.stdout.write('')
