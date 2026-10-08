from datetime import datetime, time, timedelta
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from masterApp.models import GateMaster, softwareModule
from raiseTicketApp.models import RaiseTicket
# =========================================================
# GLOBAL SETTINGS
# =========================================================
WORKING_HOURS_PER_DAY = 8
WORKING_SECONDS_PER_DAY = WORKING_HOURS_PER_DAY * 60 * 60

def software_module_list(request):
    # =====================================================
    # TODAY
    # =====================================================
    today = timezone.localdate()
    # =====================================================
    # GET FILTER VALUES
    # =====================================================
    from_date_value = request.GET.get("from_date")
    to_date_value = request.GET.get("to_date")
    selected_module = request.GET.get("module","")

    selected_status = request.GET.get("status","all")


    # =====================================================
    # VALIDATE STATUS FILTER
    # =====================================================
    if selected_status not in {
        "all",
        "active",
        "inactive",
    }:
        selected_status = "all"


    # =====================================================
    # PARSE FROM DATE
    #
    # No date selected:
    # use today's date
    # =====================================================
    from_date = (
        parse_date(from_date_value)
        if from_date_value
        else today
    )

    if not from_date:
        from_date = today


    # =====================================================
    # PARSE TO DATE
    # =====================================================
    to_date = (
        parse_date(to_date_value)
        if to_date_value
        else today
    )

    if not to_date:
        to_date = today


    # =====================================================
    # FROM DATE > TO DATE
    #
    # Example:
    # From = 20 Sep
    # To   = 15 Sep
    #
    # Automatically swap
    # =====================================================
    if from_date > to_date:
        from_date, to_date = (
            to_date,
            from_date
        )


    # =====================================================
    # SELECTED DAYS
    #
    # 15 Sep -> 15 Sep = 1 day
    # 15 Sep -> 16 Sep = 2 days
    # =====================================================
    selected_days = (
        to_date - from_date
    ).days + 1


    # =====================================================
    # TOTAL WORKING TIME
    #
    # 1 day = 8 hours
    # 2 days = 16 hours
    # 3 days = 24 hours
    # =====================================================
    total_working_seconds = (selected_days * WORKING_SECONDS_PER_DAY)
    total_working_time = format_seconds(total_working_seconds)


    # =====================================================
    # DATE RANGE AS DATETIME
    #
    # Start:
    # selected from date 00:00:00
    #
    # End:
    # next date 00:00:00
    #
    # End is exclusive.
    # =====================================================
    current_timezone = (timezone.get_current_timezone())

    start_datetime = timezone.make_aware(
        datetime.combine(
            from_date,
            time.min
        ),
        current_timezone
    )

    end_datetime_exclusive = timezone.make_aware(
        datetime.combine(
            to_date + timedelta(days=1),
            time.min
        ),
        current_timezone
    )


    # =====================================================
    # CURRENT TIME
    # =====================================================
    current_time = timezone.now()


    # =====================================================
    # ALL MODULES
    #
    # Used in filter dropdown.
    # =====================================================
    all_modules = (
        softwareModule.objects
        .all()
        .order_by("moduleName")
    )


    # =====================================================
    # MODULE QUERYSET
    # =====================================================
    modules_queryset = (
        softwareModule.objects
        .all()
        .order_by("moduleName")
    )


    # =====================================================
    # MODULE FILTER
    # =====================================================
    if (selected_module and selected_module.isdigit()):
        modules_queryset = (
            modules_queryset.filter(
                id=int(selected_module)
            )
        )


    # =====================================================
    # ACTIVE / INACTIVE FILTER
    # =====================================================
    if selected_status == "active":
        modules_queryset = (
            modules_queryset.filter(
                is_active=True
            )
        )

    elif selected_status == "inactive":
        modules_queryset = (
            modules_queryset.filter(
                is_active=False
            )
        )


    # =====================================================
    # FINAL FILTERED MODULE LIST
    # =====================================================
    modules = list(modules_queryset)
    # =====================================================
    # SUMMARY COUNTS
    # =====================================================
    total_modules = len(modules)
    active_modules = 0
    for module in modules:
        if module.is_active:
            active_modules = active_modules + 1
        inactive_modules = total_modules - active_modules
    # =====================================================
    # CALCULATE EACH MODULE HEALTH
    # =====================================================
    for module in modules:
        # -------------------------------------------------
        # All tickets of current module
        # -------------------------------------------------
        base_tickets = (RaiseTicket.objects.filter(software_module=module))
        # =================================================
        # TOTAL TICKETS
        #
        # Count tickets created inside selected date range.
        # =================================================
        total_tickets = (base_tickets.filter(created_at__gte=start_datetime,created_at__lt=end_datetime_exclusive)
            .count()
        )
        # =================================================
        # DOWNTIME-ELIGIBLE TICKETS
        #
        # Conditions:
        # 1. Assignment approved
        # 2. Assignment response time exists
        # 3. Ticket started before selected range ended
        # 4. Ticket closed after selected range started
        #    OR is still open
        # =================================================
        downtime_tickets = list(base_tickets.filter(assignment_status="APPROVED",assignment_responded_at__isnull=False,assignment_responded_at__lt=(end_datetime_exclusive))
            .filter(Q(closed_at__gte=start_datetime) |Q(closed_at__isnull=True))
            .only(
                "id",
                "assignment_responded_at",
                "closed_at"
            )
        )


        # =================================================
        # TOTAL DOWNTIME
        #
        # - Maximum 8 hours/day
        # - Overlapping tickets not double-counted
        # =================================================
        total_downtime_seconds = (
            calculate_module_downtime_seconds(
                tickets=downtime_tickets,
                from_date=from_date,
                to_date=to_date,
                current_time=current_time
            )
        )


        # =================================================
        # FINAL SAFETY CAP
        #
        # Selected working capacity se downtime
        # kabhi bhi zyada nahi hoga.
        # =================================================
        total_downtime_seconds = min(
            total_downtime_seconds,
            total_working_seconds
        )


        # =================================================
        # DOWNTIME %
        # =================================================
        if total_working_seconds > 0:
            downtime_percentage = (
                total_downtime_seconds
                /
                total_working_seconds
            ) * 100
        else:
            downtime_percentage = 0


        # =================================================
        # UPTIME / AVAILABILITY %
        # =================================================
        uptime_percentage = max(
            0,
            100 - downtime_percentage
        )

        availability_percentage = (
            uptime_percentage
        )


        # =================================================
        # UPTIME SECONDS
        # =================================================
        uptime_seconds = max(0,total_working_seconds - total_downtime_seconds)
        # =================================================
        # FORMAT TIMES
        # =================================================
        downtime_time = format_seconds(total_downtime_seconds)
        uptime_time = format_seconds(uptime_seconds)


        # =================================================
        # TEMPORARY VALUES FOR TEMPLATE
        #
        # These are NOT saved in database.
        # =================================================
        module.total_tickets = (total_tickets)
        module.selected_days = (selected_days)
        module.total_working_time = (total_working_time)
        module.downtime_time = (downtime_time)

        module.downtime_percentage = round(
            downtime_percentage,
            2
        )

        module.uptime_time = (
            uptime_time
        )

        module.uptime_percentage = round(
            uptime_percentage,
            2
        )

        module.availability_percentage = round(
            availability_percentage,
            2
        )


    # =====================================================
    # CONTEXT
    # =====================================================
    context = {
        "modules": modules,
        "all_modules": all_modules,

        "total_modules": total_modules,
        "active_modules": active_modules,
        "inactive_modules": inactive_modules,

        "selected_days": selected_days,
        "total_working_time": total_working_time,

        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),

        "selected_module": selected_module,
        "selected_status": selected_status,
    }


    # =====================================================
    # RENDER
    # =====================================================
    return render(
        request,
        "software_module_list.html",
        context
    )

# =========================================================
# FORMAT SECONDS
#
# Examples:
# 28800 -> 08:00:00
# 57600 -> 16:00:00
# 86400 -> 24:00:00
# =========================================================
def format_seconds(total_seconds):
    total_seconds = int(max(0, total_seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# =========================================================
# MERGE OVERLAPPING TIME INTERVALS
#
# Example:
# Ticket 1 = 10:00 - 12:00
# Ticket 2 = 11:00 - 13:00
#
# Actual module downtime = 3 hours
# NOT 4 hours
# =========================================================
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals,key=lambda item: item[0])
    merged = [list(intervals[0])]
    for start_time, end_time in intervals[1:]:
        last_start, last_end = merged[-1]
        if start_time <= last_end:
            merged[-1][1] = max(last_end,end_time)
        else:
            merged.append([start_time, end_time])
    return merged


# =========================================================
# MODULE DOWNTIME FOR SELECTED DATE RANGE
#
# Rule:
# 1 Day = Maximum 8 Hours downtime
# 2 Days = Maximum 16 Hours downtime
# 3 Days = Maximum 24 Hours downtime
#
# Overlapping tickets are counted only once.
# =========================================================
def calculate_module_downtime_seconds(tickets,from_date,to_date,current_time):
    total_downtime_seconds = 0
    current_timezone = timezone.get_current_timezone()
    current_date = from_date
    while current_date <= to_date:
        # -------------------------------------------------
        # Current calendar day start
        # -------------------------------------------------
        day_start = timezone.make_aware(datetime.combine(current_date,time.min),
            current_timezone
        )

        # -------------------------------------------------
        # Next day start
        #
        # We use end-exclusive range:
        # day_start <= time < day_end
        # -------------------------------------------------
        day_end = timezone.make_aware(datetime.combine(current_date + timedelta(days=1),time.min),current_timezone)
        intervals = []
        for ticket in tickets:
            # ---------------------------------------------
            # Ticket must have accept/assignment response
            # ---------------------------------------------
            if not ticket.assignment_responded_at:
                continue
            ticket_start = (ticket.assignment_responded_at)
            # ---------------------------------------------
            # Closed ticket:
            # downtime ends at closed_at
            #
            # Open ticket:
            # downtime ends at current time
            # ---------------------------------------------
            if ticket.closed_at:
                ticket_end = ticket.closed_at
            else:
                ticket_end = current_time

            # ---------------------------------------------
            # Invalid timestamps safety
            # ---------------------------------------------
            if ticket_end <= ticket_start:
                continue

            # ---------------------------------------------
            # Find overlap between:
            #
            # Ticket interval
            # AND
            # Current selected day
            # ---------------------------------------------
            overlap_start = max(ticket_start,day_start)
            overlap_end = min(ticket_end,day_end)
            if overlap_end <= overlap_start:
                continue
            intervals.append((overlap_start,overlap_end))

        # -------------------------------------------------
        # Prevent overlapping tickets from double counting
        # -------------------------------------------------
        merged_intervals = merge_intervals(intervals)
        day_downtime_seconds = sum(
            (end_time - start_time).total_seconds()
            for start_time, end_time
            in merged_intervals
        )

        # -------------------------------------------------
        # Maximum downtime per selected day = 8 hours
        # -------------------------------------------------
        day_downtime_seconds = min(
            day_downtime_seconds,
            WORKING_SECONDS_PER_DAY
        )

        total_downtime_seconds += (day_downtime_seconds)
        current_date += timedelta(days=1)
    return total_downtime_seconds


# =========================================================
# SOFTWARE MODULE HEALTH
# =========================================================



# =========================================================
# HARDWARE / GATE HEALTH
# =========================================================
def gate_health(request):

    gates = (
        GateMaster.objects
        .select_related(
            "StateMaster",
            "district"
        )
        .all()
        .order_by(
            "gate_name"
        )
    )

    total_gates = gates.count()

    active_gates = (
        gates.filter(
            is_active=True
        ).count()
    )

    inactive_gates = (
        gates.filter(
            is_active=False
        ).count()
    )

    context = {
        "gates": gates,
        "total_gates": total_gates,
        "active_gates": active_gates,
        "inactive_gates": inactive_gates,
    }

    return render(
        request,
        "hardware_health.html",
        context
    )
