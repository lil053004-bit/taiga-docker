from django.core.management.base import BaseCommand
from taiga.users.models import User
from taiga.projects.userstories.models import UserStory
from taiga.projects.tasks.models import Task
from taiga.projects.issues.models import Issue
from taiga.projects.models import Membership

class Command(BaseCommand):
    help = 'Assign unassigned user stories, tasks, and issues to admin'

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
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'userstories', 'tasks', 'issues'],
            default='all',
            help='Type of items to process (default: all)'
        )

    def handle(self, *args, **options):
        username = options['username']
        dry_run = options['dry_run']
        item_type = options['type']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        try:
            admin_user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'Found admin user: {admin_user.username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Admin user "{username}" not found!'))
            return

        total_assigned = 0

        if item_type in ['all', 'userstories']:
            assigned = self.process_userstories(admin_user, dry_run)
            total_assigned += assigned

        if item_type in ['all', 'tasks']:
            assigned = self.process_tasks(admin_user, dry_run)
            total_assigned += assigned

        if item_type in ['all', 'issues']:
            assigned = self.process_issues(admin_user, dry_run)
            total_assigned += assigned

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'Total items processed: {total_assigned}'))
        self.stdout.write('=' * 60)

    def process_userstories(self, admin_user, dry_run):
        self.stdout.write('\n📖 Processing User Stories...')
        unassigned = UserStory.objects.filter(assigned_to__isnull=True)
        count = unassigned.count()
        self.stdout.write(f'Found {count} unassigned user stories')

        assigned_count = 0
        for story in unassigned:
            if Membership.objects.filter(project=story.project, user=admin_user).exists():
                if not dry_run:
                    story.assigned_to = admin_user
                    story.save(update_fields=['assigned_to'])
                self.stdout.write(f'  ✓ Assigned: {story.subject[:50]}...')
                assigned_count += 1
            else:
                self.stdout.write(f'  ⏭ Skipped (admin not member): {story.subject[:50]}...')

        return assigned_count

    def process_tasks(self, admin_user, dry_run):
        self.stdout.write('\n✅ Processing Tasks...')
        unassigned = Task.objects.filter(assigned_to__isnull=True)
        count = unassigned.count()
        self.stdout.write(f'Found {count} unassigned tasks')

        assigned_count = 0
        for task in unassigned:
            if Membership.objects.filter(project=task.project, user=admin_user).exists():
                if not dry_run:
                    task.assigned_to = admin_user
                    task.save(update_fields=['assigned_to'])
                self.stdout.write(f'  ✓ Assigned: {task.subject[:50]}...')
                assigned_count += 1
            else:
                self.stdout.write(f'  ⏭ Skipped (admin not member): {task.subject[:50]}...')

        return assigned_count

    def process_issues(self, admin_user, dry_run):
        self.stdout.write('\n🐛 Processing Issues...')
        unassigned = Issue.objects.filter(assigned_to__isnull=True)
        count = unassigned.count()
        self.stdout.write(f'Found {count} unassigned issues')

        assigned_count = 0
        for issue in unassigned:
            if Membership.objects.filter(project=issue.project, user=admin_user).exists():
                if not dry_run:
                    issue.assigned_to = admin_user
                    issue.save(update_fields=['assigned_to'])
                self.stdout.write(f'  ✓ Assigned: {issue.subject[:50]}...')
                assigned_count += 1
            else:
                self.stdout.write(f'  ⏭ Skipped (admin not member): {issue.subject[:50]}...')

        return assigned_count
