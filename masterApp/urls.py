from django.urls import path
from loginApp.views import *
from . import views


urlpatterns = [

    # =========================================================
    # PERMISSION URLS
    # =========================================================

    # Permission List + Create
    path('permissions/',views.permission_list,name='permission_list'),
    # Permission Update
    path('permissions/update/<int:id>/',views.permission_update,name='permission_update'),
    # Permission Delete
    path('permissions/delete/<int:id>/',views.permission_delete,name='permission_delete'),
    # =========================================================
    # ROLE URLS
    # =========================================================

    # Role List + Create
    path('roles/',views.role_list,name='role_list'),

    # Role Update
    path(
        'roles/update/<int:id>/',
        views.role_update,
        name='role_update'
    ),

    # Role Delete
    path(
        'roles/delete/<int:id>/',
        views.role_delete,
        name='role_delete'
    ),


    # =========================================================
    # ROLE PERMISSION MAPPING URLS
    # =========================================================

    # Role Permission List + Create
    path(
        'role-permissions/',
        views.role_permission_list,
        name='role_permission_list'
    ),

    # Role Permission Update
    path(
        'role-permissions/update/<int:id>/',
        views.role_permission_update,
        name='role_permission_update'
    ),

    # Role Permission Delete
    path(
        'role-permissions/delete/<int:id>/',
        views.role_permission_delete,
        name='role_permission_delete'
    ),
path(
        "users/",
        user_list,
        name="user_list"
    ),
    # ==========================================
    # SOFTWARE MODULE
    # ==========================================

    path(
        "software-modules/",
        views.software_module_list,
        name="software_module_list"
    ),

    path(
        "software-modules/update/<int:id>/",
        views.software_module_update,
        name="software_module_update"
    ),

    path(
        "software-modules/delete/<int:id>/",
        views.software_module_delete,
        name="software_module_delete"
    ),


    # ==========================================
    # HARDWARE MODULE
    # ==========================================

    path(
        "hardware-modules/",
        views.hardware_module_list,
        name="hardware_module_list"
    ),

    path(
        "hardware-modules/update/<int:id>/",
        views.hardware_module_update,
        name="hardware_module_update"
    ),

    path(
        "hardware-modules/delete/<int:id>/",
        views.hardware_module_delete,
        name="hardware_module_delete"
    ),
    path(
            "ticket_master/",
            views.ticket_type_list,
            
        ),
    path(
        "priority_list/",
        views.priority_list,
        name="priority_list"
    ),


    # Priority Update
    path(
        "priority_update/<int:id>/",
        views.priority_update,
        name="priority_update"
    ),


    # Priority Delete
    path("priority_delete/<int:id>/",views.priority_delete,name="priority_delete"),
    # Priority Delete
    path("state_masters/",views.state_master),
    path("district_masters/",views.district_master),
    path("gate_masters/",views.gate_master),
    path("meanu_master/",views.menu_create),
    path("sub-menu-create/",views.submenuURL),
    path("week_off_master/",views. week_off_master),
    path("working_hours_master/",views.working_hours_master),
    
]

