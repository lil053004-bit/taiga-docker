from django.urls import path
from . import views

app_name = 'custom'

urlpatterns = [
    path('export/', views.ExportConfigView.as_view(), name='export'),
    path('import/', views.ImportConfigView.as_view(), name='import'),
]
