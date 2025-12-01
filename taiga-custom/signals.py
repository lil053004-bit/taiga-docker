import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

ADMIN_USERNAME = getattr(settings, 'AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')
AUTO_ASSIGN_ENABLED = getattr(settings, 'AUTO_ASSIGN_ENABLED', True)
DEFAULT_USER_LANGUAGE = getattr(settings, 'DEFAULT_USER_LANGUAGE', 'zh-Hans')

def get_admin_user():
    try:
        from taiga.users.models import User
        admin_user = User.objects.filter(username=ADMIN_USERNAME).first()
        if not admin_user:
            logger.warning(f"Admin user '{ADMIN_USERNAME}' not found for auto-assign")
        return admin_user
    except Exception as e:
        logger.error(f"Error getting admin user: {str(e)}")
        return None

def is_user_member_of_project(project, user):
    try:
        from taiga.projects.models import Membership
        return Membership.objects.filter(project=project, user=user).exists()
    except Exception as e:
        logger.error(f"Error checking membership: {str(e)}")
        return False

def add_admin_to_project(project, admin_user):
    try:
        from taiga.projects.models import Membership

        if is_user_member_of_project(project, admin_user):
            logger.info(f"Admin already member of project: {project.name}")
            return True

        role = None
        for role_obj in project.roles.all():
            if role_obj.name in ['Product Owner', 'Scrum Master', 'Owner']:
                role = role_obj
                break

        if not role:
            role = project.roles.first()

        if not role:
            logger.error(f"No role found for project: {project.name}")
            return False

        membership = Membership.objects.create(
            user=admin_user,
            project=project,
            role=role,
            is_admin=True,
            email=admin_user.email,
            invited_by=admin_user
        )

        logger.info(f"✓ Added admin to project: {project.name} (ID: {project.id})")
        return True

    except Exception as e:
        logger.error(f"Error adding admin to project {project.name}: {str(e)}")
        return False

@receiver(post_save, sender='projects.Project')
def auto_add_admin_to_new_project(sender, instance, created, **kwargs):
    if not AUTO_ASSIGN_ENABLED:
        return

    if created:
        logger.info(f"New project created: {instance.name} (ID: {instance.id})")
        admin_user = get_admin_user()

        if admin_user:
            add_admin_to_project(instance, admin_user)
        else:
            logger.warning(f"Could not auto-add admin to project {instance.name}: admin user not found")

@receiver(post_save, sender='userstories.UserStory')
def auto_assign_user_story(sender, instance, created, **kwargs):
    if not AUTO_ASSIGN_ENABLED:
        return

    if created and not instance.assigned_to:
        admin_user = get_admin_user()

        if admin_user and is_user_member_of_project(instance.project, admin_user):
            try:
                instance.assigned_to = admin_user
                instance.save(update_fields=['assigned_to'])
                logger.info(f"✓ Auto-assigned user story '{instance.subject}' to {ADMIN_USERNAME}")
            except Exception as e:
                logger.error(f"Error auto-assigning user story: {str(e)}")

@receiver(post_save, sender='tasks.Task')
def auto_assign_task(sender, instance, created, **kwargs):
    if not AUTO_ASSIGN_ENABLED:
        return

    if created and not instance.assigned_to:
        admin_user = get_admin_user()

        if admin_user and is_user_member_of_project(instance.project, admin_user):
            try:
                instance.assigned_to = admin_user
                instance.save(update_fields=['assigned_to'])
                logger.info(f"✓ Auto-assigned task '{instance.subject}' to {ADMIN_USERNAME}")
            except Exception as e:
                logger.error(f"Error auto-assigning task: {str(e)}")

@receiver(post_save, sender='issues.Issue')
def auto_assign_issue(sender, instance, created, **kwargs):
    if not AUTO_ASSIGN_ENABLED:
        return

    if created and not instance.assigned_to:
        admin_user = get_admin_user()

        if admin_user and is_user_member_of_project(instance.project, admin_user):
            try:
                instance.assigned_to = admin_user
                instance.save(update_fields=['assigned_to'])
                logger.info(f"✓ Auto-assigned issue '{instance.subject}' to {ADMIN_USERNAME}")
            except Exception as e:
                logger.error(f"Error auto-assigning issue: {str(e)}")

@receiver(post_save, sender='users.User')
def set_default_language_chinese(sender, instance, created, **kwargs):
    """Automatically set new users' language to Chinese"""
    if created and not instance.lang:
        try:
            instance.lang = DEFAULT_USER_LANGUAGE
            instance.save(update_fields=['lang'])
            logger.info(f"✓ Set language to {DEFAULT_USER_LANGUAGE} for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error setting default language for user {instance.username}: {str(e)}")

logger.info("Taiga Auto-Assign and Language signals loaded successfully")
