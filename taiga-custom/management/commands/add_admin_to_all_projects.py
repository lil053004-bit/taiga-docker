from django.core.management.base import BaseCommand
from django.conf import settings
from taiga.users.models import User
from taiga.projects.models import Project, Membership

class Command(BaseCommand):
    help = 'Add admin user to all projects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='adsadmin',
            help='Admin username (default: adsadmin)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        username = options['username']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        try:
            admin_user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'Found admin user: {admin_user.username} (ID: {admin_user.id})'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Admin user "{username}" not found!'))
            return

        projects = Project.objects.all()
        self.stdout.write(f'\nFound {projects.count()} projects')

        added_count = 0
        skipped_count = 0
        failed_count = 0

        for project in projects:
            is_member = Membership.objects.filter(
                project=project,
                user=admin_user
            ).exists()

            if is_member:
                self.stdout.write(f'  ⏭  {project.name} - Admin already member')
                skipped_count += 1
                continue

            role = None
            for role_obj in project.roles.all():
                if role_obj.name in ['Product Owner', 'Scrum Master', 'Owner']:
                    role = role_obj
                    break

            if not role:
                role = project.roles.first()

            if not role:
                self.stdout.write(self.style.ERROR(f'  ✗ {project.name} - No role found'))
                failed_count += 1
                continue

            if not dry_run:
                try:
                    Membership.objects.create(
                        user=admin_user,
                        project=project,
                        role=role,
                        is_admin=True,
                        email=admin_user.email,
                        invited_by=admin_user
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {project.name} - Admin added'))
                    added_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ {project.name} - Error: {str(e)}'))
                    failed_count += 1
            else:
                self.stdout.write(f'  → {project.name} - Would add admin with role: {role.name}')
                added_count += 1

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(f'  ✓ Added: {added_count}')
        self.stdout.write(f'  ⏭ Skipped (already member): {skipped_count}')
        self.stdout.write(f'  ✗ Failed: {failed_count}')
        self.stdout.write(f'  📁 Total: {projects.count()}')
        self.stdout.write('=' * 60)
