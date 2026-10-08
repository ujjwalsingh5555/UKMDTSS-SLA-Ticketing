from django.urls import path
from raiseTicketApp import views


urlpatterns = [
    path("index/", views.index),
    path("genrate-ticket/",views.raise_ticket),
    path("Viewticket_report/",views.ticket_report),
    path("assined_ticket/",views.assigned_ticket_list),
    # ==========================================================
# ASSIGNER ACTION
# ==========================================================
    path("assigner_actions/<int:ticket_id>/",views.assigner_action,name="assigner_action"),

# ==========================================================
# TICKET CHAT
# ==========================================================
    path("ticket-chat/<int:ticket_id>/",views.ticket_chat,name="ticket_chat"),


# ==========================================================
# CLOSE TICKET
# ==========================================================

    path("close-ticket/<int:ticket_id>/",views.close_ticket,name="close_ticket"),
    path("schedule-maintenance/",views.schedule_maintenance,name="schedule_maintenance"),
    path("maintenance-report/",views.maintenance_schedule_report, name="maintenance_schedule_report"),

]


