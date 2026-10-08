from django.db import models
# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from loginApp.models import *

# ==========================================================
# RAISE TICKET
# ==========================================================

class RaiseTicket(models.Model):

    # ==========================================
    # STATUS
    # OPEN / IN_PROGRESS / CLOSED
    # ==========================================

    status = models.CharField(
        max_length=30,
        default="OPEN",
        editable=False
    )


    # ==========================================
    # Ticket Number
    # ==========================================

    ticket_no = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )


    # ==========================================
    # Ticket Type Master
    # Software / Hardware
    # ==========================================

    ticket_type = models.ForeignKey(
        'masterApp.TicketTypeMaster',
        on_delete=models.PROTECT,
        related_name='tickets'
    )


    # ==========================================
    # Priority Master
    # Low / Medium / High / Critical
    # ==========================================

    priority = models.ForeignKey(
        'masterApp.PriorityMaster',
        on_delete=models.PROTECT,
        related_name='tickets'
    )


    # ==========================================
    # Software Module
    # ==========================================

    software_module = models.ForeignKey(
        'masterApp.softwareModule',
        on_delete=models.PROTECT,
        related_name='software_tickets',
        null=True,
        blank=True
    )


    # ==========================================
    # Hardware Module
    # ==========================================

    hardware_module = models.ForeignKey(
        'masterApp.hardwareModule',
        on_delete=models.PROTECT,
        related_name='hardware_tickets',
        null=True,
        blank=True
    )
    
    # ==========================================
        # Gate Relation
        # ==========================================
    gate = models.ForeignKey(
    'masterApp.GateMaster',
    on_delete=models.PROTECT,
    related_name='gate_tickets',
    null=True,
    blank=True
)


    # ==========================================
    # Subject
    # ==========================================

    subject = models.CharField(
        max_length=255
    )


    # ==========================================
    # Description
    # ==========================================

    description = models.TextField()


    # ==========================================
    # Attachment
    # ==========================================

    attachment = models.FileField(
        upload_to='ticket_attachments/',
        null=True,
        blank=True
    )


    # ==========================================
    # Created By
    # Reporter
    # ==========================================

    created_by = models.ForeignKey(
        Registeruse,
        on_delete=models.PROTECT,
        related_name='created_tickets'
    )


    # ==========================================
    # Assigned To
    # Assigner
    # ==========================================

    assigned_to = models.ForeignKey(
        Registeruse,
        on_delete=models.PROTECT,
        related_name="assigned_tickets",
        null=True,
        blank=True
    )


    # ==========================================
    # Assignment Status
    # PENDING / APPROVED / REJECTED
    # ==========================================

    assignment_status = models.CharField(
        max_length=20,
        default='PENDING'
    )


    # ==========================================
    # Assignment Response Date & Time
    # Accept / Reject kab kiya gaya
    # ==========================================

    assignment_responded_at = models.DateTimeField(
        null=True,
        blank=True
    )


    # ==========================================
    # Response Time In Minutes
    # ==========================================

    response_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False
    )
    
    resolution_time = models.DurationField(
    null=True,
    blank=True,
    editable=False
)


    # ==========================================
    # Rejection Reason
    # ==========================================

    rejection_reason = models.TextField(
        null=True,
        blank=True
    )


    # ==========================================
    # TICKET CLOSED BY
    # Sirf assigned user close karega
    # ==========================================

    closed_by = models.ForeignKey(
        Registeruse,
        on_delete=models.PROTECT,
        related_name="closed_tickets",
        null=True,
        blank=True
    )


    # ==========================================
    # TICKET CLOSED DATE & TIME
    # ==========================================

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )


    # ==========================================
    # CLOSE REMARK
    # Assigner close karte waqt remark de sakta hai
    # ==========================================

    close_remark = models.TextField(
        null=True,
        blank=True
    )


    # ==========================================
    # Dates
    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )
    


    # ==========================================
    # CHAT OPEN / CLOSE CHECK
    # ==========================================
    #
    # Chat tabhi chalegi jab:
    #
    # assignment_status = APPROVED
    #
    # AND
    #
    # ticket CLOSED nahi hai
    #
    # ==========================================

    @property
    def is_chat_open(self):

        return (
            self.assignment_status == "APPROVED"
            and self.status != "CLOSED"
        )


    # ==========================================
    # STRING
    # ==========================================

    def __str__(self):

        return self.ticket_no

    # ======================================================
    # STRING
    # ======================================================
    
class MaintenanceSchedule(models.Model):

    # ======================================================
    # APPLICATION TYPE
    # SOFTWARE / HARDWARE
    # ======================================================

    application_type = models.CharField(
        max_length=20
    )


    # ======================================================
    # SOFTWARE MODULE
    # IMPORTANT:
    # masterApp ke softwareModule ko point karega
    # ======================================================

    software_module = models.ForeignKey(
        "masterApp.softwareModule",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_schedules"
    )


    # ======================================================
    # HARDWARE MODULE
    # IMPORTANT:
    # masterApp ke hardwareModule ko point karega
    # ======================================================

    hardware_module = models.ForeignKey(
        "masterApp.hardwareModule",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="maintenance_schedules"
    )


    # ======================================================
    # SUBJECT
    # ======================================================

    subject = models.CharField(
        max_length=255
    )


    # ======================================================
    # DESCRIPTION
    # ======================================================

    description = models.TextField()


    # ======================================================
    # ATTACHMENT
    # ======================================================

    attachment = models.FileField(
        upload_to="maintenance_attachments/",
        null=True,
        blank=True
    )


    # ======================================================
    # SCHEDULE FROM
    # ======================================================

    schedule_from = models.DateTimeField()


    # ======================================================
    # SCHEDULE TO
    # ======================================================

    schedule_to = models.DateTimeField()


    # ======================================================
    # DURATION
    # Example:
    # 03:30:00
    # ======================================================

    duration = models.DurationField(
        null=True,
        blank=True,
        editable=False
    )


    # ======================================================
    # STATUS
    # ======================================================

    status = models.CharField(
        max_length=20,
        default="SCHEDULED"
    )


    # ======================================================
    # CREATED BY
    # ======================================================

    created_by = models.ForeignKey(
        "loginApp.Registeruse",
        on_delete=models.PROTECT,
        related_name="created_maintenance_schedules"
    )


    # ======================================================
    # CREATED DATE
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # ======================================================
    # UPDATED DATE
    # ======================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # ======================================================
    # SAVE
    # AUTOMATIC DURATION CALCULATION
    # ======================================================

# ==========================================================
# TICKET MESSAGE / CHAT MODEL
# ==========================================================

class TicketMessage(models.Model):

    # ==========================================
    # TICKET
    # Kis ticket ki chat hai
    # ==========================================

    ticket = models.ForeignKey(
        RaiseTicket,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )


    # ==========================================
    # SENDER
    # Reporter ya Assigner
    # ==========================================

    sender = models.ForeignKey(
        Registeruse,
        on_delete=models.PROTECT,
        related_name="sent_ticket_messages"
    )


    # ==========================================
    # MESSAGE
    # ==========================================

    message = models.TextField(
        null=True,
        blank=True
    )


    # ==========================================
    # ATTACHMENT
    # Optional file/image/document
    # ==========================================

    attachment = models.FileField(
        upload_to="ticket_chat_attachments/",
        null=True,
        blank=True
    )


    # ==========================================
    # READ STATUS
    # False = unread
    # True  = read
    # ==========================================

    is_read = models.BooleanField(
        default=False
    )


    # ==========================================
    # MESSAGE CREATED DATE & TIME
    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # ==========================================
    # STRING
    # ==========================================


