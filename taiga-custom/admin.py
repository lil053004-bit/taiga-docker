from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from taiga.users.models import User
from taiga.projects.models import Project, Membership
from taiga.projects.userstories.models import UserStory
from taiga.projects.tasks.models import Task
from taiga.projects.issues.models import Issue
import logging

logger = logging.getLogger(__name__)


class TaigaConfigAdmin(admin.ModelAdmin):
    """
    Custom Admin for Taiga configuration export/import
    """

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_view), name='custom_export'),
            path('import/', self.admin_site.admin_view(self.import_view), name='custom_import'),
            path('language-stats/', self.admin_site.admin_view(self.language_stats_view), name='language_stats'),
        ]
        return custom_urls + urls

    def export_view(self, request):
        """Export configuration view"""
        from .views import ExportConfigView
        return ExportConfigView.as_view()(request)

    def import_view(self, request):
        """Import configuration view"""
        from .views import ImportConfigView
        return ImportConfigView.as_view()(request)

    def language_stats_view(self, request):
        """Show language statistics"""
        from django.db.models import Count

        language_stats = User.objects.values('lang').annotate(count=Count('id')).order_by('-count')
        total_users = User.objects.count()
        users_without_lang = User.objects.filter(lang__isnull=True).count() + User.objects.filter(lang='').count()

        context = {
            'title': 'User Language Statistics',
            'language_stats': language_stats,
            'total_users': total_users,
            'users_without_lang': users_without_lang,
        }

        return render(request, 'admin/custom/language_stats.html', context)


class UserLanguageAdmin(admin.ModelAdmin):
    """Admin actions for user language management"""

    list_display = ['username', 'email', 'full_name', 'lang', 'is_active']
    list_filter = ['lang', 'is_active']
    search_fields = ['username', 'email', 'full_name']
    actions = ['set_language_chinese', 'set_language_english']

    def set_language_chinese(self, request, queryset):
        updated = queryset.update(lang='zh-Hans')
        self.message_user(request, f'Successfully set {updated} users to Chinese (zh-Hans)')
    set_language_chinese.short_description = 'Set language to Chinese (简体中文)'

    def set_language_english(self, request, queryset):
        updated = queryset.update(lang='en')
        self.message_user(request, f'Successfully set {updated} users to English')
    set_language_english.short_description = 'Set language to English'


admin.site.register(User, UserLanguageAdmin)
