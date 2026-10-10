from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RaiseTicket
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.paginator import Paginator
from django.db.models import Q
from masterApp.models import (TicketTypeMaster,PriorityMaster,softwareModule,hardwareModule,GateMaster)
from masterApp.models import (
    TicketTypeMaster,
    PriorityMaster
)
from loginApp.models import(
    Registeruse
)
from raiseTicketApp.models import *
from masterApp.models import WeekOffMaster






# Create your views here.
def index(request):
    return render(request,"index.html")

# ==========================================================
# RAISE TICKET
# ==========================================================

def raise_ticket(request):
    # ======================================================
    # CHECK LOGIN USER
    # ======================================================
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(
            request,"Please login first.")
        return redirect("login")
    # ======================================================
    # MASTER DATA
    # ======================================================
    ticket_types = (
        TicketTypeMaster.objects
        .filter(is_active=True)
        .order_by("name")
    )
    priorities = (
        PriorityMaster.objects
        .filter(is_active=True)
        .order_by("name")
    )
    software_modules = (
        softwareModule.objects
        .filter(is_active=True)
        .order_by("moduleName")
    )
    hardware_modules = (
        hardwareModule.objects
        .filter(is_active=True)
        .order_by("moduleName")
    )
    # ======================================================
    # GATE MASTER
    # Hardware Ticket ke liye
    # ======================================================
    gates = (
        GateMaster.objects
        .filter(is_active=True)
        .order_by("gate_name")
    )
    # ======================================================
    # ASSIGNED USERS
    # ======================================================
    assigned_users = (
        Registeruse.objects
        .filter(is_active=True)
        .order_by("name")
    )

    # ======================================================
    # POST REQUEST
    # ======================================================
    if request.method == "POST":
        # ==================================================
        # WEEK OFF DATE CHECK
        # ==================================================
        current_date = timezone.localdate()

        week_off = WeekOffMaster.objects.filter(
            off_date=current_date
        ).first()

        if week_off:
            messages.error(
                request,
                (
                    f"Ticket cannot be generated on "
                    f"{current_date.strftime('%d-%m-%Y (%A)')}. "
                    f"This date is marked as a Week Off."
                )
            )
            return redirect("/raise/genrate-ticket/")

        # ==================================================
        # GET FORM DATA
        # ==================================================

        ticket_type_id = request.POST.get("ticket_type")
        priority_id = request.POST.get("priority")
        software_module_id = request.POST.get( "software_module")
        hardware_module_id = request.POST.get("hardware_module")


        # ==================================================
        # GATE ID
        # Hardware Ticket ke liye
        # ==================================================

        gate_id = request.POST.get(
            "gate"
        )
        assigned_to_id = request.POST.get(
            "assigned_to"
        )
        subject = request.POST.get(
            "subject",
            ""
        ).strip()
        description = request.POST.get(
            "description",
            ""
        ).strip()
        attachment = request.FILES.get(
            "attachment"
        )
        # ==================================================
        # TICKET TYPE VALIDATION
        # ==================================================

        if not ticket_type_id:

            messages.error(request,"Please select Ticket Type.")
            return redirect("/raise/genrate-ticket/")


        # ==================================================
        # PRIORITY VALIDATION
        # ==================================================

        if not priority_id:

            messages.error(request,"Please select Priority.")
            return redirect("/raise/genrate-ticket/")


        # ==================================================
        # ASSIGNED TO VALIDATION
        # ==================================================

        if not assigned_to_id:

            messages.error(request,"Please select Assigned To.")

            return redirect("/raise/genrate-ticket/")


        # ==================================================
        # SUBJECT VALIDATION
        # ==================================================

        if not subject:

            messages.error(
                request,
                "Subject is required."
            )

            return redirect(
                "/raise/genrate-ticket/"
            )


        # ==================================================
        # DESCRIPTION VALIDATION
        # ==================================================

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return redirect(
                "/raise/genrate-ticket/"
            )


        # ==================================================
        # GET TICKET TYPE
        # ==================================================

        ticket_type = get_object_or_404(
            TicketTypeMaster,
            id=ticket_type_id,
            is_active=True
        )


        # ==================================================
        # GET PRIORITY
        # ==================================================

        priority = get_object_or_404(
            PriorityMaster,
            id=priority_id,
            is_active=True
        )


        # ==================================================
        # GET ASSIGNED USER
        # ==================================================

        assigned_to = get_object_or_404(
            Registeruse,
            id=assigned_to_id,
            is_active=True
        )


        # ==================================================
        # TICKET TYPE CODE
        # ==================================================

        ticket_type_code = (
            ticket_type.code
            .strip()
            .upper()
        )


        # ==================================================
        # MODULE / GATE VARIABLES
        # ==================================================

        selected_software_module = None
        selected_hardware_module = None
        selected_gate = None


        # ==================================================
        # SOFTWARE TICKET
        # ==================================================

        if ticket_type_code == "SOFTWARE":
            if not software_module_id:
                messages.error(request,"Please select Software Module.")
                return redirect("/raise/genrate-ticket/")
            selected_software_module = (
                get_object_or_404(
                    softwareModule,
                    id=software_module_id,
                    is_active=True
                )
            )
        # ==================================================
        # HARDWARE TICKET
        # ==================================================
        elif ticket_type_code == "HARDWARE":
            # ==============================================
            # GATE REQUIRED
            # ==============================================

            if not gate_id:
                messages.error(request,"Please select Gate.")
                return redirect(
                    "/raise/genrate-ticket/"
                )


            # ==============================================
            # HARDWARE MODULE REQUIRED
            # ==============================================

            if not hardware_module_id:

                messages.error(
                    request,
                    "Please select Hardware Module."
                )

                return redirect(
                    "/raise/genrate-ticket/"
                )


            # ==============================================
            # GET SELECTED GATE
            # ==============================================

            selected_gate = (
                get_object_or_404(
                    GateMaster,
                    id=gate_id,
                    is_active=True
                )
            )


            # ==============================================
            # GET SELECTED HARDWARE MODULE
            # ==============================================

            selected_hardware_module = (
                get_object_or_404(
                    hardwareModule,
                    id=hardware_module_id,
                    is_active=True
                )
            )


        # ==================================================
        # CHECK MAINTENANCE SCHEDULE
        # ==================================================

        current_time = timezone.now()


        maintenance_query = (
            MaintenanceSchedule.objects
            .filter(

                status__in=[
                    "SCHEDULED",
                    "IN_PROGRESS"
                ],

                schedule_to__gte=current_time

            )
        )


        # ==================================================
        # SOFTWARE MAINTENANCE CHECK
        # ==================================================

        if ticket_type_code == "SOFTWARE":

            maintenance_query = (
                maintenance_query.filter(
                    software_module=selected_software_module
                )
            )


        # ==================================================
        # HARDWARE MAINTENANCE CHECK
        # ==================================================

        elif ticket_type_code == "HARDWARE":

            maintenance_query = (
                maintenance_query.filter(
                    hardware_module=selected_hardware_module
                )
            )


        # ==================================================
        # GET MAINTENANCE
        # ==================================================

        maintenance = (
            maintenance_query
            .order_by("schedule_from")
            .first()
        )


        # ==================================================
        # MAINTENANCE EXISTS
        # STOP TICKET CREATION
        # ==================================================

        if maintenance:

            maintenance_from = (
                timezone.localtime(
                    maintenance.schedule_from
                )
                .strftime(
                    "%d-%m-%Y %I:%M %p"
                )
            )


            maintenance_to = (
                timezone.localtime(
                    maintenance.schedule_to
                )
                .strftime(
                    "%d-%m-%Y %I:%M %p"
                )
            )


            # ==============================================
            # MODULE NAME
            # ==============================================

            if ticket_type_code == "SOFTWARE":

                module_name = (
                    selected_software_module.moduleName
                )


            elif ticket_type_code == "HARDWARE":
                module_name = (
                    selected_hardware_module.moduleName
                )
            else:

                module_name = "Selected Module"
            # ==============================================
            # ERROR MESSAGE
            # ============================================== 
            messages.error(
                request,
                (
                    f"Ticket cannot be raised for "
                    f"{module_name}. "
                    f"This module is under scheduled "
                    f"maintenance from "
                    f"{maintenance_from} "
                    f"to "
                    f"{maintenance_to}."
                )
            )


            return redirect(
                "/raise/genrate-ticket/"
            )


        # ==================================================
        # CREATED BY USER
        # ==================================================

        created_by = get_object_or_404(
            Registeruse,
            id=user_id,
            is_active=True
        )


        # ==================================================
        # CURRENT DATE
        # ==================================================

        current_date = timezone.localdate()


        # ==================================================
        # DATE STRING
        # ==================================================

        date_string = (
            current_date.strftime(
                "%d%m%Y"
            )
        )


        # ==================================================
        # TICKET PREFIX
        # ==================================================

        if ticket_type_code == "HARDWARE":
            prefix = "MSTPL-HRD-"
        elif ticket_type_code == "SOFTWARE":

            prefix = "MSTPL-SOFT-"
        else:
            prefix = "MSTPL-OTH-"

        # ==================================================
        # FULL PREFIX
        # ==================================================

        full_prefix = (
            f"{prefix}"
            f"{date_string}"
        )


        # ==================================================
        # FIND TODAY LAST TICKET
        # ==================================================

        last_ticket = (
            RaiseTicket.objects

            .filter(
                ticket_no__startswith=full_prefix
            )

            .order_by(
                "-ticket_no"
            )

            .first()
        )


        # ==================================================
        # NEXT SERIAL NUMBER
        # ==================================================

        if last_ticket:

            last_sequence = int(
                last_ticket.ticket_no[-4:]
            )


            next_sequence = (
                last_sequence + 1
            )


        else:

            next_sequence = 1


        # ==================================================
        # 4 DIGIT SEQUENCE
        # ==================================================

        sequence = str(
            next_sequence
        ).zfill(4)


        # ==================================================
        # FINAL TICKET NUMBER
        # ==================================================

        ticket_no = (
            f"{full_prefix}"
            f"{sequence}"
        )


        # ==================================================
        # CREATE TICKET
        # ==================================================

        ticket = RaiseTicket.objects.create(

            ticket_no=ticket_no,
            ticket_type=ticket_type,
            priority=priority,
            software_module=selected_software_module,
            # ==============================================
            # GATE
            # Software Ticket me None rahega
            # Hardware Ticket me selected Gate save hoga
            # ==============================================
            gate=selected_gate,
            hardware_module=selected_hardware_module,

            subject=subject,

            description=description,

            attachment=attachment,

            status="OPEN",

            created_by=created_by,

            assigned_to=assigned_to

        )


        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        messages.success(
            request,
            (
                f"Ticket {ticket.ticket_no} "
                f"raised successfully and "
                f"assigned to "
                f"{assigned_to.name}."
            )
        )


        # ==================================================
        # REDIRECT
        # ==================================================

        return redirect(
            "/raise/genrate-ticket/"
        )


    # ======================================================
    # GET REQUEST CONTEXT
    # ======================================================

    context = {

        "ticket_types": ticket_types,

        "priorities": priorities,

        "software_modules": software_modules,

        "hardware_modules": hardware_modules,

        # Gate dropdown ke liye
        "gates": gates,

        "assigned_users": assigned_users,

    }


    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "raise_ticket.html",
        context
    )





# ==========================================================
# TICKET REPORT
# ==========================================================

def ticket_report(request):

    # ======================================================
    # BASE QUERY
    # ======================================================
    
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    tickets = (
    RaiseTicket.objects
    .select_related(
        "ticket_type",
        "priority",
        "software_module",
        "hardware_module",
        "gate",
        "created_by",
        "assigned_to"
    )
    .filter(
        Q(created_by_id=user_id) |
        Q(assigned_to_id=user_id)
    )
    .order_by("-created_at")
)

    # ======================================================
    # GET FILTER VALUES
    # ======================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    ticket_type_id = request.GET.get(
        "ticket_type",
        ""
    )

    priority_id = request.GET.get(
        "priority",
        ""
    )

    status = request.GET.get(
        "status",
        ""
    )

    from_date = request.GET.get(
        "from_date",
        ""
    )

    to_date = request.GET.get(
        "to_date",
        ""
    )


    # ======================================================
    # SEARCH
    # ======================================================

    if search:
        tickets = tickets.filter(
            Q(
                ticket_no__icontains=search
            )

            |

            Q(
                subject__icontains=search
            )

            |

            Q(
                description__icontains=search
            )

            |

            Q(
                created_by__name__icontains=search
            )

            |

            # ==================================================
            # HARDWARE GATE SEARCH
            # ==================================================

            Q(
                gate__gate_name__icontains=search
            )

            |

            # ==================================================
            # SOFTWARE MODULE SEARCH
            # ==================================================

            Q(software_module__moduleName__icontains=search)|

            # ==================================================
            # HARDWARE MODULE SEARCH
            # ==================================================

            Q(hardware_module__moduleName__icontains=search)

        )


    # ======================================================
    # TICKET TYPE FILTER
    # ======================================================

    if ticket_type_id:

        tickets = tickets.filter(
            ticket_type_id=ticket_type_id
        )


    # ======================================================
    # PRIORITY FILTER
    # ======================================================

    if priority_id:

        tickets = tickets.filter(
            priority_id=priority_id
        )


    # ======================================================
    # STATUS FILTER
    # ======================================================

    if status:

        tickets = tickets.filter(
            status=status
        )


    # ======================================================
    # FROM DATE FILTER
    # ======================================================

    if from_date:

        tickets = tickets.filter(
            created_at__date__gte=from_date
        )


    # ======================================================
    # TO DATE FILTER
    # ======================================================

    if to_date:

        tickets = tickets.filter(
            created_at__date__lte=to_date
        )


    # ======================================================
    # REPORT COUNTS
    # ======================================================

    total_tickets = (
        tickets.count()
    )


    open_count = (
        tickets
        .filter(
            status="OPEN"
        )
        .count()
    )


    in_progress_count = (
        tickets
        .filter(
            status="IN_PROGRESS"
        )
        .count()
    )


    resolved_count = (
        tickets
        .filter(
            status="RESOLVED"
        )
        .count()
    )


    closed_count = (
        tickets
        .filter(
            status="CLOSED"
        )
        .count()
    )


    # ======================================================
    # MASTER DATA FOR FILTER DROPDOWNS
    # ======================================================

    ticket_types = (
        TicketTypeMaster.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )


    priorities = (
        PriorityMaster.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )


    # ======================================================
    # PAGINATION
    # ======================================================

    paginator = Paginator(
        tickets,
        20
    )


    page_number = request.GET.get(
        "page"
    )


    page_obj = paginator.get_page(
        page_number
    )


    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        # ==================================================
        # TICKET DATA
        # ==================================================

        "tickets": page_obj,
        "page_obj": page_obj,


        # ==================================================
        # MASTER DATA
        # ==================================================

        "ticket_types": ticket_types,
        "priorities": priorities,


        # ==================================================
        # COUNTS
        # ==================================================

        "total_tickets": total_tickets,
        "open_count": open_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,
        "closed_count": closed_count,
        # ==================================================
        # SELECTED FILTERS
        # ==================================================

        "search": search,
        "selected_ticket_type": ticket_type_id,
        "selected_priority": priority_id,
        "selected_status": status,
        "from_date": from_date,
        "to_date": to_date,
    }


    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "ticket_report.html",
        context
    )

# ==========================================================
# ASSIGNED TICKET LIST
# ==========================================================
def assigned_ticket_list(request):

    # ======================================================
    # LOGIN USER
    # ======================================================
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")


    # ======================================================
    # GET ASSIGNED TICKETS
    # ======================================================
    tickets = RaiseTicket.objects.filter(
        assigned_to_id=user_id
    ).select_related(
        "ticket_type",
        "priority",
        "software_module",
        "hardware_module",
        "created_by",
        "assigned_to"
    ).order_by("-created_at")


    # ======================================================
    # FORMAT RESPONSE TIME
    # HOURS / MINUTES / SECONDS
    # ======================================================
    for ticket in tickets:

        # ==============================================
        # RESPONSE AVAILABLE
        # ==============================================
        if ticket.response_time:

            # ------------------------------------------
            # TOTAL RESPONSE TIME IN SECONDS
            # ------------------------------------------
            total_seconds = int(
                ticket.response_time.total_seconds()
            )


            # ------------------------------------------
            # HOURS
            # ------------------------------------------
            hours = total_seconds // 3600


            # ------------------------------------------
            # MINUTES
            # ------------------------------------------
            minutes = (
                total_seconds % 3600
            ) // 60


            # ------------------------------------------
            # SECONDS
            # ------------------------------------------
            seconds = total_seconds % 60


            # ------------------------------------------
            # FORMAT RESPONSE TIME
            # Example: 01h 12m 30s
            # ------------------------------------------
            ticket.formatted_response_time = (
                f"{hours:02d}h "
                f"{minutes:02d}m "
                f"{seconds:02d}s"
            )


        # ==============================================
        # RESPONSE NOT GIVEN
        # ==============================================
        else:

            ticket.formatted_response_time = "Pending"


    # ======================================================
    # CONTEXT
    # ======================================================
    context = {
        "tickets": tickets
    }


    # ======================================================
    # RENDER
    # ======================================================
    return render(
        request,
        "assigned_ticket_list.html",
        context
    )



# ==========================================================
# ASSIGNER ACTION
# ACCEPT / REJECT
# ==========================================================



# ==========================================================
# ASSIGNED TICKET LIST
# ==========================================================
def assigned_ticket_list(request):

    # ======================================================
    # LOGIN USER
    # ======================================================
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    # ======================================================
    # GET ASSIGNED TICKETS
    # ======================================================
    tickets = RaiseTicket.objects.filter(
        assigned_to_id=user_id
    ).select_related(
        "ticket_type",
        "priority",
        "software_module",
        "hardware_module",
        "created_by",
        "assigned_to"
    ).order_by("-created_at")


    # ======================================================
    # CALCULATE RESPONSE TIME
    # HOURS / MINUTES / SECONDS
    # ======================================================
    for ticket in tickets:

        # Response diya ja chuka hai
        if ticket.assignment_responded_at:

            # ==============================================
            # RESPONSE TIME DIFFERENCE
            # ==============================================
            time_difference = (
                ticket.assignment_responded_at
                - ticket.created_at
            )


            # ==============================================
            # TOTAL SECONDS
            # ==============================================
            total_seconds = int(
                time_difference.total_seconds()
            )


            # Negative value protection
            if total_seconds < 0:
                total_seconds = 0


            # ==============================================
            # HOURS
            # ==============================================
            hours = total_seconds // 3600


            # ==============================================
            # MINUTES
            # ==============================================
            minutes = (
                total_seconds % 3600
            ) // 60


            # ==============================================
            # SECONDS
            # ==============================================
            seconds = total_seconds % 60


            # ==============================================
            # FORMATTED RESPONSE TIME
            # Example: 01h 12m 30s
            # ==============================================
            ticket.formatted_response_time = (
                f"{hours:02d}h "
                f"{minutes:02d}m "
                f"{seconds:02d}s"
            )


        # ==================================================
        # RESPONSE NOT GIVEN
        # ==================================================
        else:

            ticket.formatted_response_time = "Pending"


    # ======================================================
    # CONTEXT
    # ======================================================
    context = {
        "tickets": tickets
    }


    # ======================================================
    # RENDER
    # ======================================================
    return render(
        request,
        "assigned_ticket_list.html",
        context
    )



# ==========================================================
# ASSIGNER ACTION
# ACCEPT / REJECT
# ==========================================================


# ==========================================================
# ASSIGNED TICKET LIST
# ==========================================================
def assigned_ticket_list(request):

    # ======================================================
    # LOGIN USER
    # ======================================================
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    # ======================================================
    # GET ASSIGNED TICKETS
    # ======================================================
    tickets = RaiseTicket.objects.filter(
        assigned_to_id=user_id
    ).select_related(
        "ticket_type",
        "priority",
        "software_module",
        "hardware_module",
        "created_by",
        "assigned_to"
    ).order_by("-created_at")


    # ======================================================
    # CALCULATE RESPONSE TIME
    # ======================================================
    for ticket in tickets:

        # ==================================================
        # CHECK RESPONSE GIVEN OR NOT
        # ==================================================
        if ticket.assignment_responded_at:

            # ==============================================
            # RESPONSE TIME DIFFERENCE
            # ==============================================
            time_difference = (
                ticket.assignment_responded_at
                - ticket.created_at
            )


            # ==============================================
            # TOTAL SECONDS
            # ==============================================
            total_seconds = int(
                time_difference.total_seconds()
            )


            # ==============================================
            # NEGATIVE TIME PROTECTION
            # ==============================================
            if total_seconds < 0:
                total_seconds = 0


            # ==============================================
            # DAYS
            # ==============================================
            days = total_seconds // 86400


            # ==============================================
            # HOURS
            # ==============================================
            hours = (
                total_seconds % 86400
            ) // 3600


            # ==============================================
            # MINUTES
            # ==============================================
            minutes = (
                total_seconds % 3600
            ) // 60


            # ==============================================
            # SECONDS
            # ==============================================
            seconds = total_seconds % 60


            # ==============================================
            # FORMAT RESPONSE TIME
            # ==============================================

            # Example:
            # 2d 05h 10m 30s
            if days > 0:

                ticket.formatted_response_time = (
                    f"{days}d "
                    f"{hours:02d}h "
                    f"{minutes:02d}m "
                    f"{seconds:02d}s"
                )


            # Example:
            # 1h 10m 30s
            elif hours > 0:

                ticket.formatted_response_time = (
                    f"{hours}h "
                    f"{minutes:02d}m "
                    f"{seconds:02d}s"
                )


            # Example:
            # 10m 30s
            elif minutes > 0:

                ticket.formatted_response_time = (
                    f"{minutes}m "
                    f"{seconds:02d}s"
                )


            # Example:
            # 25s
            else:

                ticket.formatted_response_time = (
                    f"{seconds}s"
                )


        # ==================================================
        # RESPONSE NOT GIVEN
        # ==================================================
        else:

            ticket.formatted_response_time = "Pending"


    # ======================================================
    # CONTEXT
    # ======================================================
    context = {
        "tickets": tickets
    }


    # ======================================================
    # RENDER
    # ======================================================
    return render(
        request,
        "assigned_ticket_list.html",
        context
    )



# ==========================================================
# ASSIGNER ACTION
# ACCEPT / REJECT
# ==========================================================
# ==========================================================
# ASSIGNER ACTION
# ACCEPT / REJECT TICKET
# ==========================================================

def assigner_action(request, ticket_id):

    # ======================================================
    # LOGIN USER
    # ======================================================

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect(
            "login"
        )


    # ======================================================
    # GET TICKET
    # Ticket sirf assigned user ko milega
    # ======================================================

    ticket = get_object_or_404(

        RaiseTicket,

        id=ticket_id,

        assigned_to_id=user_id

    )


    # ======================================================
    # ONLY POST REQUEST
    # ======================================================

    if request.method != "POST":

        return redirect(
            "/raise/assined_ticket/"
        )


    # ======================================================
    # GET ACTION
    # ======================================================

    action = request.POST.get(
        "action",
        ""
    ).strip().lower()


    # ======================================================
    # CHECK CURRENT ASSIGNMENT STATUS
    # ======================================================

    if ticket.assignment_status != "PENDING":

        messages.warning(
            request,
            "You have already taken action on this ticket."
        )

        return redirect(
            "/raise/assined_ticket/"
        )


    # ======================================================
    # ACCEPT TICKET
    # ======================================================

    if action == "accept":

        # ==================================================
        # RESPONSE DATE TIME
        # ==================================================

        responded_at = timezone.now()


        # ==================================================
        # CALCULATE RESPONSE TIME
        # ==================================================
        #
        # Example:
        #
        # Ticket raised : 10:00 AM
        # Accepted      : 10:15 AM
        #
        # Response Time = 15 Minutes
        #
        # ==================================================

        time_difference = (responded_at- ticket.created_at
        )


        response_minutes = int(
            time_difference.total_seconds()
            / 60
        )


        if response_minutes < 0:

            response_minutes = 0


        # ==================================================
        # UPDATE ASSIGNMENT
        # ==================================================

        ticket.assignment_status = (
            "APPROVED"
        )


        ticket.assignment_responded_at = (
            responded_at
        )


        ticket.response_time_minutes = (
            response_minutes
        )


        ticket.rejection_reason = None


        # ==================================================
        # UPDATE MAIN TICKET STATUS
        # ==================================================
        #
        # Ticket accept hote hi:
        #
        # OPEN
        #   ↓
        # IN_PROGRESS
        #
        # Chat bhi ab open ho jayegi
        #
        # ==================================================

        ticket.status = "IN_PROGRESS"


        # ==================================================
        # SAVE
        # ==================================================

        ticket.save(

            update_fields=[

                "assignment_status",

                "assignment_responded_at",

                "response_time_minutes",

                "rejection_reason",

                "status",

                "updated_at",

            ]

        )


        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        messages.success(
            request,
            (
                f"Ticket {ticket.ticket_no} "
                f"accepted successfully. "
                f"Chat is now available."
            )
        )


        # ==================================================
        # DIRECT OPEN CHAT
        # ==================================================

        return redirect(
            "ticket_chat",
            ticket_id=ticket.id
        )


    # ======================================================
    # REJECT TICKET
    # ======================================================

    elif action == "reject":

        # ==================================================
        # GET REJECTION REASON
        # ==================================================

        rejection_reason = request.POST.get(
            "rejection_reason",
            ""
        ).strip()


        # ==================================================
        # VALIDATE REJECTION REASON
        # ==================================================

        if not rejection_reason:

            messages.error(
                request,
                "Please enter rejection reason."
            )

            return redirect(
                "/raise/assined_ticket/"
            )


        # ==================================================
        # RESPONSE DATE TIME
        # ==================================================

        responded_at = timezone.now()


        # ==================================================
        # CALCULATE RESPONSE TIME
        # ==================================================

        time_difference = (
            responded_at
            - ticket.created_at
        )


        response_minutes = int(
            time_difference.total_seconds()
            / 60
        )


        if response_minutes < 0:

            response_minutes = 0


        # ==================================================
        # UPDATE ASSIGNMENT
        # ==================================================

        ticket.assignment_status = (
            "REJECTED"
        )


        ticket.assignment_responded_at = (
            responded_at
        )


        ticket.response_time_minutes = (
            response_minutes
        )


        ticket.rejection_reason = (
            rejection_reason
        )


        # ==================================================
        # MAIN STATUS
        # ==================================================

        ticket.status = "REJECTED"


        # ==================================================
        # SAVE
        # ==================================================

        ticket.save(

            update_fields=[

                "assignment_status",

                "assignment_responded_at",

                "response_time_minutes",

                "rejection_reason",

                "status",

                "updated_at",

            ]

        )


        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        messages.success(
            request,
            (
                f"Ticket {ticket.ticket_no} "
                f"rejected successfully."
            )
        )


        return redirect(
            "/raise/assined_ticket/"
        )


    # ======================================================
    # INVALID ACTION
    # ======================================================

    else:

        messages.error(
            request,
            "Invalid ticket action."
        )


        return redirect(
            "/raise/assined_ticket/"
        )


def schedule_maintenance(request):

    # ======================================================
    # LOGIN USER CHECK
    # ======================================================

    user_id = request.session.get("user_id")

    if not user_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect("login")


    # ======================================================
    # LOGGED-IN USER
    # ======================================================

    created_by = get_object_or_404(
        Registeruse,
        id=user_id,
        is_active=True
    )


    # ======================================================
    # SOFTWARE MODULES
    # ======================================================

    software_modules = (
        softwareModule.objects
        .filter(is_active=True)
        .order_by("moduleName")
    )


    # ======================================================
    # HARDWARE MODULES
    # ======================================================

    hardware_modules = (
        hardwareModule.objects
        .filter(is_active=True)
        .order_by("moduleName")
    )


    # ======================================================
    # POST REQUEST
    # ======================================================

    if request.method == "POST":

        # ==================================================
        # GET FORM DATA
        # ==================================================

        application_type = request.POST.get(
            "application_type",
            ""
        ).strip().upper()


        software_module_id = request.POST.get(
            "software_module"
        )


        hardware_module_id = request.POST.get(
            "hardware_module"
        )


        subject = request.POST.get(
            "subject",
            ""
        ).strip()


        description = request.POST.get(
            "description",
            ""
        ).strip()


        attachment = request.FILES.get(
            "attachment"
        )


        schedule_from_value = request.POST.get(
            "schedule_from"
        )


        schedule_to_value = request.POST.get(
            "schedule_to"
        )


        # ==================================================
        # APPLICATION TYPE VALIDATION
        # ==================================================

        if application_type not in [
            "SOFTWARE",
            "HARDWARE"
        ]:

            messages.error(
                request,
                "Please select Software or Hardware."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # SUBJECT VALIDATION
        # ==================================================

        if not subject:

            messages.error(
                request,
                "Subject is required."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # DESCRIPTION VALIDATION
        # ==================================================

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # FROM DATE VALIDATION
        # ==================================================

        if not schedule_from_value:

            messages.error(
                request,
                "Please select Schedule From date and time."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # TO DATE VALIDATION
        # ==================================================

        if not schedule_to_value:

            messages.error(
                request,
                "Please select Schedule To date and time."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # CONVERT STRING TO DATETIME
        # ==================================================

        schedule_from = parse_datetime(
            schedule_from_value
        )

        schedule_to = parse_datetime(
            schedule_to_value
        )


        # ==================================================
        # DATETIME VALIDATION
        # ==================================================

        if not schedule_from or not schedule_to:

            messages.error(
                request,
                "Invalid Schedule From or Schedule To."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # MAKE TIMEZONE AWARE
        # ==================================================

        if timezone.is_naive(schedule_from):

            schedule_from = timezone.make_aware(
                schedule_from,
                timezone.get_current_timezone()
            )


        if timezone.is_naive(schedule_to):

            schedule_to = timezone.make_aware(
                schedule_to,
                timezone.get_current_timezone()
            )


        # ==================================================
        # CHECK FROM / TO
        # ==================================================

        if schedule_to <= schedule_from:

            messages.error(
                request,
                "Schedule To must be greater than Schedule From."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # PAST DATE CHECK
        # ==================================================

        if schedule_from < timezone.now():

            messages.error(
                request,
                "Maintenance cannot be scheduled in the past."
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # MODULE VARIABLES
        # ==================================================

        selected_software_module = None

        selected_hardware_module = None


        # ==================================================
        # SOFTWARE MODULE
        # ==================================================

        if application_type == "SOFTWARE":

            if not software_module_id:

                messages.error(
                    request,
                    "Please select Software Module."
                )

                return redirect(
                    "schedule_maintenance"
                )


            selected_software_module = get_object_or_404(
                softwareModule,
                id=software_module_id,
                is_active=True
            )


        # ==================================================
        # HARDWARE MODULE
        # ==================================================

        elif application_type == "HARDWARE":

            if not hardware_module_id:

                messages.error(
                    request,
                    "Please select Hardware Module."
                )

                return redirect(
                    "schedule_maintenance"
                )


            selected_hardware_module = get_object_or_404(
                hardwareModule,
                id=hardware_module_id,
                is_active=True
            )


        # ==================================================
        # CALCULATE DURATION
        # ==================================================
        #
        # Example:
        #
        # From = 10:00 AM
        # To   = 01:30 PM
        #
        # Duration = 03:30:00
        #
        # ==================================================

        duration = (
            schedule_to
            - schedule_from
        )


        # ==================================================
        # CHECK EXISTING SCHEDULE CONFLICT
        # ==================================================

        conflict_query = (
            MaintenanceSchedule.objects
            .filter(
                status__in=[
                    "SCHEDULED",
                    "IN_PROGRESS"
                ],

                schedule_from__lt=schedule_to,

                schedule_to__gt=schedule_from
            )
        )


        # ==================================================
        # SOFTWARE CONFLICT
        # ==================================================

        if application_type == "SOFTWARE":

            conflict_query = conflict_query.filter(
                software_module_id=software_module_id
            )


        # ==================================================
        # HARDWARE CONFLICT
        # ==================================================

        elif application_type == "HARDWARE":

            conflict_query = conflict_query.filter(
                hardware_module_id=hardware_module_id
            )


        # ==================================================
        # IF CONFLICT EXISTS
        # ==================================================

        if conflict_query.exists():

            existing_schedule = (
                conflict_query
                .order_by("schedule_from")
                .first()
            )


            existing_from = timezone.localtime(
                existing_schedule.schedule_from
            ).strftime(
                "%d-%m-%Y %I:%M %p"
            )


            existing_to = timezone.localtime(
                existing_schedule.schedule_to
            ).strftime(
                "%d-%m-%Y %I:%M %p"
            )


            messages.error(
                request,
                (
                    "Maintenance is already scheduled "
                    "for this module from "
                    f"{existing_from} "
                    "to "
                    f"{existing_to}."
                )
            )

            return redirect(
                "schedule_maintenance"
            )


        # ==================================================
        # CREATE MAINTENANCE SCHEDULE
        # ==================================================

        maintenance = MaintenanceSchedule.objects.create(

            application_type=application_type,


            # Software
            software_module=(
                selected_software_module
                if application_type == "SOFTWARE"
                else None
            ),


            # Hardware
            hardware_module=(
                selected_hardware_module
                if application_type == "HARDWARE"
                else None
            ),


            subject=subject,


            description=description,


            attachment=attachment,


            schedule_from=schedule_from,


            schedule_to=schedule_to,


            # Duration calculated in VIEW
            duration=duration,


            status="SCHEDULED",


            created_by=created_by
        )


        # ==================================================
        # DURATION DISPLAY FORMAT
        # ==================================================

        total_seconds = int(
            duration.total_seconds()
        )


        days = (
            total_seconds // 86400
        )


        hours = (
            total_seconds % 86400
        ) // 3600


        minutes = (
            total_seconds % 3600
        ) // 60


        # ==================================================
        # DURATION TEXT
        # ==================================================

        duration_parts = []


        if days > 0:

            duration_parts.append(
                f"{days} "
                f"{'Day' if days == 1 else 'Days'}"
            )


        if hours > 0:

            duration_parts.append(
                f"{hours} "
                f"{'Hour' if hours == 1 else 'Hours'}"
            )


        if minutes > 0:

            duration_parts.append(
                f"{minutes} "
                f"{'Minute' if minutes == 1 else 'Minutes'}"
            )


        if not duration_parts:

            duration_parts.append(
                "Less than 1 Minute"
            )


        duration_text = " ".join(
            duration_parts
        )


        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        messages.success(
            request,
            (
                "Maintenance scheduled successfully. "
                f"Duration: {duration_text}"
            )
        )


        # ==================================================
        # REDIRECT
        # ==================================================

        return redirect(
            "schedule_maintenance"
        )


    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        "software_modules": software_modules,

        "hardware_modules": hardware_modules,

    }


    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "schedule_maintenance.html",
        context
    )
    
# ==========================================================
# MAINTENANCE SCHEDULE REPORT
# ==========================================================

def maintenance_schedule_report(request):

    # ======================================================
    # LOGIN CHECK
    # ======================================================

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    # ======================================================
    # BASE QUERY
    # ======================================================

    schedules = (
        MaintenanceSchedule.objects
        .select_related(
            "software_module",
            "hardware_module",
            "created_by"
        )
        .all()
        .order_by("-created_at")
    )


    # ======================================================
    # GET FILTERS
    # ======================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()


    application_type = request.GET.get(
        "application_type",
        ""
    ).strip()


    status = request.GET.get(
        "status",
        ""
    ).strip()


    from_date = request.GET.get(
        "from_date",
        ""
    ).strip()


    to_date = request.GET.get(
        "to_date",
        ""
    ).strip()


    # ======================================================
    # SEARCH
    # ======================================================

    if search:

        schedules = schedules.filter(
            Q(subject__icontains=search)
            |
            Q(description__icontains=search)
            |
            Q(created_by__name__icontains=search)

            |
            Q(
                software_module__moduleName__icontains=search
            )
            |
            Q(
                hardware_module__moduleName__icontains=search
            )
        )


    # ======================================================
    # APPLICATION TYPE FILTER
    # ======================================================

    if application_type:

        schedules = schedules.filter(
            application_type=application_type
        )


    # ======================================================
    # STATUS FILTER
    # ======================================================

    if status:

        schedules = schedules.filter(
            status=status
        )


    # ======================================================
    # FROM DATE FILTER
    # ======================================================

    if from_date:

        schedules = schedules.filter(
            schedule_from__date__gte=from_date
        )


    # ======================================================
    # TO DATE FILTER
    # ======================================================

    if to_date:

        schedules = schedules.filter(
            schedule_to__date__lte=to_date
        )


    # ======================================================
    # COUNTS
    # ======================================================

    total_count = schedules.count()


    scheduled_count = schedules.filter(
        status="SCHEDULED"
    ).count()


    in_progress_count = schedules.filter(
        status="IN_PROGRESS"
    ).count()


    completed_count = schedules.filter(
        status="COMPLETED"
    ).count()


    cancelled_count = schedules.filter(
        status="CANCELLED"
    ).count()


    # ======================================================
    # FORMAT DURATION
    # ======================================================

    for schedule in schedules:

        if schedule.duration:

            total_seconds = int(
                schedule.duration.total_seconds()
            )


            days = total_seconds // 86400


            hours = (
                total_seconds % 86400
            ) // 3600


            minutes = (
                total_seconds % 3600
            ) // 60


            duration_parts = []


            if days > 0:

                duration_parts.append(
                    f"{days}d"
                )


            if hours > 0:

                duration_parts.append(
                    f"{hours}h"
                )


            if minutes > 0:

                duration_parts.append(
                    f"{minutes}m"
                )


            if not duration_parts:

                duration_parts.append(
                    "0m"
                )


            schedule.formatted_duration = " ".join(
                duration_parts
            )


        else:

            schedule.formatted_duration = "-"


    # ======================================================
    # PAGINATION
    # ======================================================

    paginator = Paginator(
        schedules,
        20
    )


    page_number = request.GET.get(
        "page"
    )


    page_obj = paginator.get_page(
        page_number
    )


    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        "schedules": page_obj,

        "page_obj": page_obj,

        "total_count": total_count,

        "scheduled_count": scheduled_count,

        "in_progress_count": in_progress_count,

        "completed_count": completed_count,

        "cancelled_count": cancelled_count,

        "search": search,

        "selected_application_type": application_type,

        "selected_status": status,

        "from_date": from_date,

        "to_date": to_date,
    }


    # ======================================================
    # RENDER
    # ======================================================

    return render(
        request,
        "maintenance_schedule_report.html",
        context
    )
    
# ==========================================================
# TICKET CHAT
# REPORTER <-> ASSIGNER
# ==========================================================

def ticket_chat(request, ticket_id):

    # ======================================================
    # LOGIN USER
    # ======================================================

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect(
            "login"
        )


    # ======================================================
    # CURRENT USER
    # ======================================================

    current_user = get_object_or_404(

        Registeruse,

        id=user_id,

        is_active=True

    )


    # ======================================================
    # GET TICKET
    # ======================================================

    ticket = RaiseTicket.objects.select_related(
    "created_by",
    "assigned_to",
    "ticket_type",
    "priority",
    "software_module",
    "hardware_module",
    "closed_by"
).get(id=ticket_id)


    # ======================================================
    # ACCESS SECURITY
    # ======================================================
    #
    # Sirf:
    #
    # Reporter
    # created_by
    #
    # OR
    #
    # Assigner
    # assigned_to
    # ======================================================
    reporter_id = (ticket.created_by_id)
    assigner_id = (ticket.assigned_to_id)
    allowed_users = [reporter_id,assigner_id]
    if user_id not in allowed_users:
        messages.error(
            request,
            "You are not authorized to access this ticket chat."
        )
        return redirect(
            "/raise/index/"
        )


    # ======================================================
    # CHAT AVAILABLE ONLY AFTER ACCEPT
    # ======================================================

    if ticket.assignment_status != "APPROVED":

        messages.warning(
            request,
            "Chat will be available after the ticket is accepted."
        )


        # ==================================================
        # ASSIGNER
        # ==================================================

        if user_id == ticket.assigned_to_id:
            return redirect(
                "/raise/assined_ticket/"
            )
        # ==================================================
        # REPORTER
        # ==================================================
        return redirect(
            "/raise/Viewticket_report/"
        )


    # ======================================================
    # GET CHAT MESSAGES
    # ======================================================

    chat_messages = (TicketMessage.objects.filter(ticket=ticket)

        .select_related(
            "sender"
        )

        .order_by(
            "created_at"
        )

    )


    # ======================================================
    # POST MESSAGE
    # ======================================================

    if request.method == "POST":

        # ==================================================
        # CHECK TICKET CLOSED
        # ==================================================
        #
        # Ticket CLOSED hote hi
        # message send nahi ho sakta.
        #
        # ==================================================

        if ticket.status == "CLOSED":
            messages.error(
                request,
                "This ticket is closed. Chat is no longer available."
            )
            return redirect("ticket_chat",ticket_id=ticket.id)
        # ==================================================
        # GET MESSAGE
        # ==================================================
        message_text = request.POST.get( "message", "").strip()
        # ==================================================
        # GET ATTACHMENT
        # ==================================================
        attachment = request.FILES.get("attachment")


        # ==================================================
        # VALIDATION
        # ==================================================
        #
        # Message ya attachment me se
        # kam se kam ek hona chahiye
        #
        # ==================================================

        if not message_text and not attachment:

            messages.error(request,"Please enter a message or attach a file.")


            return redirect(
                "ticket_chat",
                ticket_id=ticket.id
            )


        # ==================================================
        # CREATE CHAT MESSAGE
        # ==================================================

        TicketMessage.objects.create(
            ticket=ticket,
            sender=current_user,
            message=message_text,
            attachment=attachment,
            is_read=False

        )


        # ==================================================
        # REDIRECT
        # ==================================================

        return redirect(
            "ticket_chat",
            ticket_id=ticket.id
        )


    # ======================================================
    # MARK OTHER USER MESSAGES AS READ
    # ======================================================

    TicketMessage.objects.filter(

        ticket=ticket,

        is_read=False

    ).exclude(

        sender_id=user_id

    ).update(

        is_read=True

    )


    # ======================================================
    # CHECK CHAT ACTIVE
    # ======================================================
    #
    # assignment_status = APPROVED
    #
    # AND
    #
    # status != CLOSED
    #
    # ======================================================

    chat_active = (

        ticket.assignment_status == "APPROVED"

        and

        ticket.status != "CLOSED"

    )


    # ======================================================
    # CHECK CURRENT USER IS REPORTER
    # ======================================================

    is_reporter = (

        user_id
        == ticket.created_by_id

    )


    # ======================================================
    # CHECK CURRENT USER IS ASSIGNER
    # ======================================================

    is_assigner = (

        user_id
        == ticket.assigned_to_id

    )


    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        # Ticket
        "ticket": ticket,

        # All messages
        "chat_messages": chat_messages,

        # Logged user
        "current_user": current_user,

        # True / False
        "chat_active": chat_active,

        # Reporter check
        "is_reporter": is_reporter,

        # Assigner check
        "is_assigner": is_assigner,

    }


    # ======================================================
    # RENDER
    # ======================================================

    return render(

        request,

        "ticket_chat.html",

        context

    )

# ==========================================================
# CLOSE TICKET
# ONLY ASSIGNER CAN CLOSE
# ==========================================================

def close_ticket(request, ticket_id):

    # ======================================================
    # LOGIN USER
    # ======================================================

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please login first."
        )

        return redirect(
            "login"
        )


    # ======================================================
    # GET ASSIGNED TICKET
    # ======================================================

    ticket = RaiseTicket.objects.filter(
    id=ticket_id,
    assigned_to_id=user_id
).first()


    # ======================================================
    # ONLY POST
    # ======================================================

    if request.method != "POST":

        return redirect(
            "ticket_chat",
            ticket_id=ticket.id
        )


    # ======================================================
    # CHECK ACCEPTED
    # ======================================================

    if ticket.assignment_status != "APPROVED":

        messages.error(
            request,
            "Ticket must be accepted before closing."
        )

        return redirect(
            "/raise/assined_ticket/"
        )


    # ======================================================
    # ALREADY CLOSED
    # ======================================================

    if ticket.status == "CLOSED":

        messages.warning(
            request,
            "Ticket is already closed."
        )

        return redirect(
            "ticket_chat",
            ticket_id=ticket.id
        )


    # ======================================================
    # CLOSE REMARK
    # ======================================================

    close_remark = request.POST.get(
        "close_remark",
        ""
    ).strip()


    if not close_remark:

        messages.error(
            request,
            "Please enter close remark."
        )

        return redirect(
            "ticket_chat",
            ticket_id=ticket.id
        )


    # ======================================================
    # CLOSED BY USER
    # ======================================================
    closed_by = Registeruse.objects.filter(
    id=user_id,
    is_active=True
).first()


    
    
  
    # ======================================================
        # CLOSE TICKET
        # ======================================================

    ticket.status = "CLOSED"
    ticket.closed_by = closed_by
    ticket.closed_at = timezone.now()
    ticket.close_remark = close_remark
    # ======================================================
            # Resolution Time
            # ======================================================
            
    ticket.resolution_time = (
    ticket.closed_at
    - ticket.created_at
)


    # ======================================================
    # SAVE
    # ======================================================

    ticket.save(
        update_fields=[
            "status",
            "closed_by",
            "closed_at",
            "close_remark",
            "resolution_time",
            "updated_at",
        ]
    )


    # ======================================================
    # SUCCESS MESSAGE
    # ======================================================

    messages.success(
        request,
        (
            f"Ticket {ticket.ticket_no} "
            f"closed successfully. "
            f"Chat is now closed."
        )
    )


    return redirect(
        "ticket_chat",
        ticket_id=ticket.id
    )