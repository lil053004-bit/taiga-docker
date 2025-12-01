from django.views import View
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
from taiga.users.models import User
from taiga.projects.models import Project, Membership
from taiga.projects.userstories.models import UserStory
from taiga.projects.tasks.models import Task
from taiga.projects.issues.models import Issue
from taiga.projects.custom_attributes.models import UserStoryCustomAttribute, TaskCustomAttribute, IssueCustomAttribute
import json
import zipfile
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name='dispatch')
class ExportConfigView(View):
    """Export Taiga configuration and data"""

    def get(self, request):
        context = {
            'title': 'Export Taiga Configuration',
            'projects_count': Project.objects.count(),
            'users_count': User.objects.count(),
            'userstories_count': UserStory.objects.count(),
            'tasks_count': Task.objects.count(),
            'issues_count': Issue.objects.count(),
        }
        return render(request, 'admin/custom/export.html', context)

    def post(self, request):
        """Generate and download export file"""
        export_options = {
            'projects': request.POST.get('export_projects') == 'on',
            'users': request.POST.get('export_users') == 'on',
            'memberships': request.POST.get('export_memberships') == 'on',
            'userstories': request.POST.get('export_userstories') == 'on',
            'tasks': request.POST.get('export_tasks') == 'on',
            'issues': request.POST.get('export_issues') == 'on',
            'custom_attributes': request.POST.get('export_custom_attributes') == 'on',
        }

        export_format = request.POST.get('format', 'json')

        try:
            export_data = self._generate_export_data(export_options)

            if export_format == 'zip':
                return self._create_zip_response(export_data)
            else:
                return self._create_json_response(export_data)

        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def _generate_export_data(self, options):
        """Generate export data based on selected options"""
        data = {
            'export_date': datetime.now().isoformat(),
            'export_version': '1.0',
        }

        if options['projects']:
            projects = Project.objects.all().values(
                'id', 'name', 'slug', 'description', 'created_date',
                'modified_date', 'owner_id', 'is_private'
            )
            data['projects'] = list(projects)
            logger.info(f"Exported {len(data['projects'])} projects")

        if options['users']:
            users = User.objects.all().values(
                'id', 'username', 'email', 'full_name', 'lang',
                'is_active', 'is_superuser', 'date_joined'
            )
            data['users'] = list(users)
            logger.info(f"Exported {len(data['users'])} users")

        if options['memberships']:
            memberships = Membership.objects.all().values(
                'id', 'user_id', 'project_id', 'role_id',
                'is_admin', 'email', 'created_at'
            )
            data['memberships'] = list(memberships)
            logger.info(f"Exported {len(data['memberships'])} memberships")

        if options['userstories']:
            userstories = UserStory.objects.all().values(
                'id', 'subject', 'description', 'project_id',
                'status_id', 'assigned_to_id', 'created_date',
                'modified_date', 'owner_id'
            )
            data['userstories'] = list(userstories)
            logger.info(f"Exported {len(data['userstories'])} user stories")

        if options['tasks']:
            tasks = Task.objects.all().values(
                'id', 'subject', 'description', 'project_id',
                'status_id', 'assigned_to_id', 'user_story_id',
                'created_date', 'modified_date', 'owner_id'
            )
            data['tasks'] = list(tasks)
            logger.info(f"Exported {len(data['tasks'])} tasks")

        if options['issues']:
            issues = Issue.objects.all().values(
                'id', 'subject', 'description', 'project_id',
                'status_id', 'assigned_to_id', 'severity_id',
                'priority_id', 'created_date', 'modified_date', 'owner_id'
            )
            data['issues'] = list(issues)
            logger.info(f"Exported {len(data['issues'])} issues")

        if options['custom_attributes']:
            us_attrs = UserStoryCustomAttribute.objects.all().values(
                'id', 'name', 'description', 'type', 'project_id', 'order'
            )
            task_attrs = TaskCustomAttribute.objects.all().values(
                'id', 'name', 'description', 'type', 'project_id', 'order'
            )
            issue_attrs = IssueCustomAttribute.objects.all().values(
                'id', 'name', 'description', 'type', 'project_id', 'order'
            )
            data['custom_attributes'] = {
                'userstory': list(us_attrs),
                'task': list(task_attrs),
                'issue': list(issue_attrs),
            }
            logger.info(f"Exported custom attributes")

        return data

    def _create_json_response(self, data):
        """Create JSON download response"""
        filename = f"taiga-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _create_zip_response(self, data):
        """Create ZIP download response"""
        filename = f"taiga-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('export.json', json.dumps(data, indent=2, default=str))
            zip_file.writestr('README.txt', 'Taiga Configuration Export\n\nImport this file in Admin > Import Configuration')

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@method_decorator(staff_member_required, name='dispatch')
class ImportConfigView(View):
    """Import Taiga configuration and data"""

    def get(self, request):
        context = {
            'title': 'Import Taiga Configuration',
        }
        return render(request, 'admin/custom/import.html', context)

    def post(self, request):
        """Process uploaded import file"""
        if 'import_file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        uploaded_file = request.FILES['import_file']
        import_mode = request.POST.get('import_mode', 'merge')

        try:
            if uploaded_file.name.endswith('.zip'):
                data = self._extract_zip(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                data = json.loads(uploaded_file.read().decode('utf-8'))
            else:
                return JsonResponse({'error': 'Invalid file format. Use .json or .zip'}, status=400)

            result = self._process_import(data, import_mode)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def _extract_zip(self, zip_file):
        """Extract JSON data from ZIP file"""
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            json_content = zip_ref.read('export.json').decode('utf-8')
            return json.loads(json_content)

    def _process_import(self, data, mode):
        """Process import data"""
        from .importers import TaigaImporter

        importer = TaigaImporter(mode=mode)
        result = importer.import_data(data)

        return result
