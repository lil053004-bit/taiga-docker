from taiga.projects.userstories.serializers import UserStorySerializer
from taiga.projects.tasks.serializers import TaskSerializer
from taiga.projects.issues.serializers import IssueSerializer


class EnhancedUserStorySerializer(UserStorySerializer):
    """Enhanced UserStory serializer with custom fields in list view"""

    def to_representation(self, obj):
        data = super().to_representation(obj)

        if hasattr(obj, 'custom_attributes_values') and obj.custom_attributes_values:
            try:
                custom_fields = {}
                if hasattr(obj.custom_attributes_values, 'attributes_values'):
                    custom_fields = obj.custom_attributes_values.attributes_values or {}
                data['custom_fields_display'] = custom_fields
            except Exception:
                data['custom_fields_display'] = {}
        else:
            data['custom_fields_display'] = {}

        return data


class EnhancedTaskSerializer(TaskSerializer):
    """Enhanced Task serializer with custom fields in list view"""

    def to_representation(self, obj):
        data = super().to_representation(obj)

        if hasattr(obj, 'custom_attributes_values') and obj.custom_attributes_values:
            try:
                custom_fields = {}
                if hasattr(obj.custom_attributes_values, 'attributes_values'):
                    custom_fields = obj.custom_attributes_values.attributes_values or {}
                data['custom_fields_display'] = custom_fields
            except Exception:
                data['custom_fields_display'] = {}
        else:
            data['custom_fields_display'] = {}

        return data


class EnhancedIssueSerializer(IssueSerializer):
    """Enhanced Issue serializer with custom fields in list view"""

    def to_representation(self, obj):
        data = super().to_representation(obj)

        if hasattr(obj, 'custom_attributes_values') and obj.custom_attributes_values:
            try:
                custom_fields = {}
                if hasattr(obj.custom_attributes_values, 'attributes_values'):
                    custom_fields = obj.custom_attributes_values.attributes_values or {}
                data['custom_fields_display'] = custom_fields
            except Exception:
                data['custom_fields_display'] = {}
        else:
            data['custom_fields_display'] = {}

        return data
