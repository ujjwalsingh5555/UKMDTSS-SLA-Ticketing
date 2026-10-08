from django.urls import path
from . import views

urlpatterns = [

    path("software_module_list/",views.software_module_list),
    path("hardware-health/",views.gate_health,name="gate_health"),
]


