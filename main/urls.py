from django.urls import path
from . import views
urlpatterns = [
    path('', views.слушатели_view, name='student_list'),
    path('organisations/', views.организации_view, name='organisation_list'),
    path('groups/', views.группы_view, name='group_list'),
    path('courses/', views.курсы_view, name='course_list'),
    path('materials/', views.материалы_view, name='material_list'),
    path('countries/', views.страны_view, name='country_list'),
    path('delete_country/<int:id>/', views.delete_country, name='delete_country'),
    path('delete_listener/<int:id>/', views.delete_listener, name='delete_listener'),
    path('delete_group/<int:id>/', views.delete_group, name='delete_group'),
    path('delete_group_linking/<int:id>/', views.delete_group_linking, name='delete_group_linking'),
    path('delete_course/<int:id>/', views.delete_course, name='delete_course'),
    path('delete_material/<int:id>/', views.delete_material, name='delete_material'),
    path('delete_organisation/<int:id>/', views.delete_organisation, name='delete_organisation'),
    path('delete_org_linking/<int:id>/', views.delete_org_linking, name='delete_org_linking'),
    path('export_listeners/', views.export_listeners, name='export_listeners'),
    path('export_groups/', views.export_groups, name='export_groups'),
    path('export_courses/', views.export_courses, name='export_courses'),
    path('export_organisations/', views.export_organisations, name='export_organisations'),
]
