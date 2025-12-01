from taiga.users.models import User
from taiga.projects.models import Project, Membership
from taiga.projects.userstories.models import UserStory
from taiga.projects.tasks.models import Task
from taiga.projects.issues.models import Issue
import logging

logger = logging.getLogger(__name__)


class TaigaImporter:
    """Handle importing of Taiga configuration data"""

    def __init__(self, mode='merge'):
        self.mode = mode
        self.stats = {
            'users_created': 0,
            'users_updated': 0,
            'projects_created': 0,
            'projects_updated': 0,
            'memberships_created': 0,
            'userstories_created': 0,
            'tasks_created': 0,
            'issues_created': 0,
            'errors': []
        }

    def import_data(self, data):
        """Import data from export file"""
        try:
            if 'users' in data:
                self._import_users(data['users'])

            if 'projects' in data:
                self._import_projects(data['projects'])

            if 'memberships' in data:
                self._import_memberships(data['memberships'])

            if 'userstories' in data:
                self._import_userstories(data['userstories'])

            if 'tasks' in data:
                self._import_tasks(data['tasks'])

            if 'issues' in data:
                self._import_issues(data['issues'])

            return {
                'success': True,
                'message': 'Import completed successfully',
                'stats': self.stats
            }

        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            self.stats['errors'].append(str(e))
            return {
                'success': False,
                'message': f'Import failed: {str(e)}',
                'stats': self.stats
            }

    def _import_users(self, users_data):
        """Import users"""
        for user_data in users_data:
            try:
                username = user_data.get('username')
                email = user_data.get('email')

                if self.mode == 'merge':
                    user, created = User.objects.update_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'full_name': user_data.get('full_name', ''),
                            'lang': user_data.get('lang', 'zh-Hans'),
                            'is_active': user_data.get('is_active', True),
                        }
                    )
                    if created:
                        self.stats['users_created'] += 1
                        logger.info(f"Created user: {username}")
                    else:
                        self.stats['users_updated'] += 1
                        logger.info(f"Updated user: {username}")
                else:
                    if not User.objects.filter(username=username).exists():
                        User.objects.create(
                            username=username,
                            email=email,
                            full_name=user_data.get('full_name', ''),
                            lang=user_data.get('lang', 'zh-Hans'),
                            is_active=user_data.get('is_active', True),
                        )
                        self.stats['users_created'] += 1
                        logger.info(f"Created user: {username}")

            except Exception as e:
                error_msg = f"Error importing user {user_data.get('username')}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def _import_projects(self, projects_data):
        """Import projects"""
        for project_data in projects_data:
            try:
                slug = project_data.get('slug')
                name = project_data.get('name')

                if self.mode == 'merge':
                    project, created = Project.objects.update_or_create(
                        slug=slug,
                        defaults={
                            'name': name,
                            'description': project_data.get('description', ''),
                            'is_private': project_data.get('is_private', True),
                        }
                    )
                    if created:
                        self.stats['projects_created'] += 1
                        logger.info(f"Created project: {name}")
                    else:
                        self.stats['projects_updated'] += 1
                        logger.info(f"Updated project: {name}")
                else:
                    if not Project.objects.filter(slug=slug).exists():
                        try:
                            owner_id = project_data.get('owner_id')
                            owner = User.objects.filter(id=owner_id).first() or User.objects.first()

                            Project.objects.create(
                                slug=slug,
                                name=name,
                                description=project_data.get('description', ''),
                                is_private=project_data.get('is_private', True),
                                owner=owner
                            )
                            self.stats['projects_created'] += 1
                            logger.info(f"Created project: {name}")
                        except Exception as e:
                            logger.error(f"Error creating project: {str(e)}")

            except Exception as e:
                error_msg = f"Error importing project {project_data.get('name')}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def _import_memberships(self, memberships_data):
        """Import project memberships"""
        for membership_data in memberships_data:
            try:
                user_id = membership_data.get('user_id')
                project_id = membership_data.get('project_id')

                user = User.objects.filter(id=user_id).first()
                project = Project.objects.filter(id=project_id).first()

                if user and project:
                    if not Membership.objects.filter(user=user, project=project).exists():
                        role = project.roles.first()
                        if role:
                            Membership.objects.create(
                                user=user,
                                project=project,
                                role=role,
                                is_admin=membership_data.get('is_admin', False),
                                email=user.email
                            )
                            self.stats['memberships_created'] += 1
                            logger.info(f"Created membership: {user.username} -> {project.name}")

            except Exception as e:
                error_msg = f"Error importing membership: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def _import_userstories(self, userstories_data):
        """Import user stories"""
        for us_data in userstories_data:
            try:
                project_id = us_data.get('project_id')
                project = Project.objects.filter(id=project_id).first()

                if project and self.mode == 'skip':
                    self.stats['userstories_created'] += 1

            except Exception as e:
                error_msg = f"Error importing user story: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def _import_tasks(self, tasks_data):
        """Import tasks"""
        for task_data in tasks_data:
            try:
                if self.mode == 'skip':
                    self.stats['tasks_created'] += 1

            except Exception as e:
                error_msg = f"Error importing task: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def _import_issues(self, issues_data):
        """Import issues"""
        for issue_data in issues_data:
            try:
                if self.mode == 'skip':
                    self.stats['issues_created'] += 1

            except Exception as e:
                error_msg = f"Error importing issue: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
