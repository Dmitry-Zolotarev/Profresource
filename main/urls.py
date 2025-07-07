from django.conf import settings
from django.conf.urls.static import static
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
    path('export_listeners_XLSX/', views.export_listeners_XLSX, name='export_listeners_XLSX'),
    path('export_groups_XLSX/', views.export_groups_XLSX, name='export_groups_XLSX'),
    path('export_courses_XLSX/', views.export_courses_XLSX, name='export_courses_XLSX'),
    path('export_organisations_XLSX/', views.export_organisations_XLSX, name='export_organisations_XLSX'),
    path('import_listeners_XLSX/', views.import_listeners_XLSX, name='import_listeners_XLSX'),
    path('import_groups_XLSX/', views.import_groups_XLSX, name='import_groups_XLSX'),
    path('import_courses_XLSX/', views.import_courses_XLSX, name='import_courses_XLSX'),
    path('import_organisations_XLSX/', views.import_organisations_XLSX, name='import_organisations_XLSX'),
    path('training_record/', views.training_record, name='training_record'),
    path('order/', views.order, name='order'),

    path('generate_certificates_zip/', views.generate_certificates_zip, name='generate_certificates_zip'),
<<<<<<< HEAD
=======

    path('ajax/regions/',  views.get_regions, name='get_regions'),
    path('ajax/districts/',  views.get_districts, name='get_districts'),
    path('ajax/places/',  views.get_places, name='get_places'),
    path('ajax/postcodes/',  views.get_postcodes, name='get_postcodes'),
    path('ajax/streets/',  views.get_streets, name='get_streets'),
    path('listener_addresses/',  views.адреса_слушателей_view, name='listener_addresses'),
    path('organisation_addresses/',  views.адреса_организаций_view, name='organisation_addresses'),
    path('delete_listener_address/<int:id>/', views.delete_listener_address, name = 'delete_listener_address'),
    path('delete_organisation_address/<int:id>/', views.delete_organisation_address, name = 'delete_organisation_address')
>>>>>>> 2889caa (07.07.2025)
]
