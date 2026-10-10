from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ticketProject.helper import get_logged_in_user, user_has_permission
from .models import *
import calendar
from datetime import date,datetime
from .models import WeekOffMaster,WorkingHoursMaster
import calendar
from django.utils import timezone



# ==========================================================
# WORKING HOURS MASTER
# ==========================================================

def working_hours_master(request):

    # ======================================================
    # CURRENT MONTH AND YEAR
    # ======================================================

    today = timezone.localdate()

    selected_month = today.month
    selected_year = today.year

    # ======================================================
    # MONTH LIST
    # ======================================================

    months = [
        {
            "id": month,
            "name": calendar.month_name[month]
        }
        for month in range(1, 13)
    ]

    # ======================================================
    # YEAR LIST
    # ======================================================

    years = range(
        today.year - 2,
        today.year + 6
    )

    # ======================================================
    # POST REQUEST
    # ======================================================

    if request.method == "POST":

        # ==================================================
        # GET FORM DATA
        # ==================================================

        month = request.POST.get("month")
        year = request.POST.get("year")

        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # ==================================================
        # REQUIRED FIELD VALIDATION
        # ==================================================

        if not all([month, year, start_time, end_time]):

            messages.error(
                request,
                "All fields are required."
            )

            return redirect("working_hours_master")

        # ==================================================
        # MONTH AND YEAR VALIDATION
        # ==================================================

        try:
            month = int(month)
            year = int(year)

            if not (1 <= month <= 12):
                raise ValueError()

            if not (2000 <= year <= 2100):
                raise ValueError()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please select a valid Month and Year."
            )

            return redirect("working_hours_master")

        # ==================================================
        # TIME CONVERSION
        # ==================================================

        try:

            start_time = datetime.strptime(
                start_time,
                "%H:%M"
            ).time()

            end_time = datetime.strptime(
                end_time,
                "%H:%M"
            ).time()

        except ValueError:

            messages.error(
                request,
                "Invalid Working Hours."
            )

            return redirect("working_hours_master")

        # ==================================================
        # START AND END TIME VALIDATION
        # ==================================================

        if end_time <= start_time:

            messages.error(
                request,
                "Ending Working Hours must be greater than Starting Working Hours."
            )

            return redirect("working_hours_master")

        # ==================================================
        # CHECK EXISTING MONTH AND YEAR
        # ==================================================

        existing_record = WorkingHoursMaster.objects.filter(
            month=month,
            year=year
        ).first()

        # ==================================================
        # UPDATE EXISTING RECORD
        # ==================================================

        if existing_record:

            existing_record.start_time = start_time
            existing_record.end_time = end_time

            existing_record.save()

            messages.success(
                request,
                "Working Hours updated successfully."
            )

        # ==================================================
        # CREATE NEW RECORD
        # ==================================================

        else:

            WorkingHoursMaster.objects.create(
                month=month,
                year=year,
                start_time=start_time,
                end_time=end_time
            )

            messages.success(
                request,
                "Working Hours created successfully."
            )

        return redirect("working_hours_master")

    # ======================================================
    # GET WORKING HOURS RECORDS
    # ======================================================

    records = list(
        WorkingHoursMaster.objects.all()
        .order_by("-year", "-month")
    )

    # ======================================================
    # CALCULATE TOTAL WORKING HOURS
    # ======================================================

    for record in records:

        start_datetime = datetime.combine(
            today,
            record.start_time
        )

        end_datetime = datetime.combine(
            today,
            record.end_time
        )

        duration = end_datetime - start_datetime

        total_minutes = max(
            0,
            int(duration.total_seconds() // 60)
        )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        record.duration_display = (
            f"{hours}h {minutes:02d}m"
        )

        record.month_name = calendar.month_name[
            record.month
        ]

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {
        "months": months,
        "years": years,
        "records": records,
        "selected_month": selected_month,
        "selected_year": selected_year
    }

    # ======================================================
    # RENDER TEMPLATE
    # ======================================================

    return render(
        request,
        "working_hours_master.html",
        context
    )



# ============================================================

# PERMISSION - LIST + CREATE

# ============================================================

def permission_list(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        description = request.POST.get("description")
        # Permission code duplicate check
        if Permission.objects.filter(code=code).exists():
            messages.error(request, "Permission code already exists.")
            return redirect("permission_list")
        Permission.objects.create(name=name,code=code,description=description)
        messages.success(request,"Permission created successfully.")
        return redirect("permission_list")
    # All permissions
    permissions = Permission.objects.all().order_by("-created_at")
    # Total permission count
    context = {"permissions": permissions,}
    return render(request,"permission.html",context)
# ============================================================
# PERMISSION - UPDATE
# ============================================================
def permission_update(request, id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    permission = get_object_or_404(Permission,id=id)
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        description = request.POST.get("description")
        # Same permission ko exclude karke duplicate check
        if Permission.objects.filter(code=code).exclude(id=id).exists():
            messages.error(request,"Permission code already exists.")
            return redirect("permission_update",id=id)
        permission.name = name
        permission.code = code
        permission.description = description
        permission.save()
        messages.success(request,"Permission updated successfully.")
        return redirect("permission_list")
    context = {"permission": permission}
    return render(request,"permission_update.html",context)





# ============================================================

# PERMISSION - DELETE

# ============================================================



def permission_delete(request, id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    permission = get_object_or_404(Permission,id=id)
    if request.method == "POST":
        permission.delete()
        messages.success(request,"Permission deleted successfully.")
    return redirect("permission_list")





# ============================================================

# ROLE - LIST + CREATE

# ============================================================



def role_list(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    if request.method == "POST":
        name = request.POST.get("name")
        if Role.objects.filter(name=name).exists():
            messages.error(request,"Role already exists.")
            return redirect("role_list")
        Role.objects.create(name=name)
        messages.success( request,"Role created successfully.")
        return redirect("role_list")
    roles = Role.objects.all().order_by("-created_at")
    context = {"roles": roles}
    return render(request,"role.html",context)
# ============================================================
# ROLE - UPDATE
# ============================================================

def role_update(request, id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    
    
    

    role = get_object_or_404(Role,id=id)
    if request.method == "POST":
        name = request.POST.get("name")
        if Role.objects.filter(name=name).exclude(id=id).exists():
            messages.error(request,"Role already exists.")
            return redirect("role_update",id=id)
        role.name = name
        role.save()
        messages.success(request,"Role updated successfully.")
        return redirect("role_list")
    context = {"role": role}
    return render(request,"role_update.html",context)





# ============================================================

# ROLE - DELETE

# ============================================================



def role_delete(request, id):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    role = get_object_or_404(

        Role,

        id=id

    )



    if request.method == "POST":



        role.delete()



        messages.success(

            request,

            "Role deleted successfully."

        )



    return redirect("role_list")





# ============================================================

# ROLE PERMISSION MAPPING - LIST + CREATE

# ============================================================



def role_permission_list(request):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    roles = Role.objects.filter(

        is_active=True

    )



    permissions = Permission.objects.filter(

        is_active=True

    )



    mappings = RolePermissionMapping.objects.select_related(

        "role",

        "permission"

    ).order_by("-created_at")



    if request.method == "POST":



        role_id = request.POST.get("role")

        permission_id = request.POST.get("permission")



        role = get_object_or_404(

            Role,

            id=role_id

        )



        permission = get_object_or_404(

            Permission,

            id=permission_id

        )



        # Duplicate mapping check

        if RolePermissionMapping.objects.filter(

            role=role,

            permission=permission

        ).exists():



            messages.error(

                request,

                "This permission is already assigned to this role."

            )



            return redirect(

                "role_permission_list"

            )



        RolePermissionMapping.objects.create(

            role=role,

            permission=permission

        )



        messages.success(

            request,

            "Permission assigned to role successfully."

        )



        return redirect(

            "role_permission_list"

        )



    context = {

        "roles": roles,

        "permissions": permissions,

        "mappings": mappings

    }



    return render(

        request,

        "role_per_mapping.html",

        context

    )





# ============================================================

# ROLE PERMISSION MAPPING - UPDATE

# ============================================================



def role_permission_update(request, id):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    mapping = get_object_or_404(

        RolePermissionMapping,

        id=id

    )



    roles = Role.objects.filter(

        is_active=True

    )



    permissions = Permission.objects.filter(

        is_active=True

    )



    if request.method == "POST":



        role_id = request.POST.get("role")

        permission_id = request.POST.get("permission")



        role = get_object_or_404(

            Role,

            id=role_id

        )



        permission = get_object_or_404(

            Permission,

            id=permission_id

        )



        # Duplicate mapping check

        if RolePermissionMapping.objects.filter(

            role=role,

            permission=permission

        ).exclude(id=id).exists():



            messages.error(

                request,

                "This permission is already assigned to this role."

            )



            return redirect(

                "role_permission_update",

                id=id

            )



        mapping.role = role

        mapping.permission = permission

        mapping.save()



        messages.success(

            request,

            "Role permission updated successfully."

        )



        return redirect(

            "role_permission_list"

        )



    context = {

        "mapping": mapping,

        "roles": roles,

        "permissions": permissions

    }



    return render(

        request,

        "role_permission_update.html",

        context

    )





# ============================================================

# ROLE PERMISSION MAPPING - DELETE

# ============================================================



def role_permission_delete(request, id):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    mapping = get_object_or_404(

        RolePermissionMapping,

        id=id

    )



    if request.method == "POST":



        mapping.delete()



        messages.success(

            request,

            "Role permission removed successfully."

        )



    return redirect(

        "role_permission_list"

    )



# views.py









# ==========================================================

# SOFTWARE MODULE - CREATE + LIST

# ==========================================================



def software_module_list(request):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    if request.method == "POST":



        module_name = request.POST.get(

            "moduleName",

            ""

        ).strip()



        description = request.POST.get(

            "description",

            ""

        ).strip()





        # ------------------------------------------

        # VALIDATION

        # ------------------------------------------



        if not module_name:



            messages.error(

                request,

                "Module Name is required."

            )



            return redirect(

                "software_module_list"

            )





        if not description:



            messages.error(

                request,

                "Description is required."

            )



            return redirect(

                "software_module_list"

            )





        # ------------------------------------------

        # MODULE NAME DUPLICATE CHECK

        # ------------------------------------------



        if softwareModule.objects.filter(

            moduleName=module_name

        ).exists():



            messages.error(

                request,

                "Software Module Name already exists."

            )



            return redirect(

                "software_module_list"

            )





        # ------------------------------------------

        # DESCRIPTION DUPLICATE CHECK

        # ------------------------------------------



        if softwareModule.objects.filter(

            description=description

        ).exists():



            messages.error(

                request,

                "Description already exists."

            )



            return redirect(

                "software_module_list"

            )





        # ------------------------------------------

        # CREATE

        # ------------------------------------------



        softwareModule.objects.create(



            moduleName=module_name,



            description=description,



            is_active=True

        )





        messages.success(

            request,

            "Software Module created successfully."

        )





        return redirect(

            "software_module_list"

        )





    # ----------------------------------------------

    # SOFTWARE MODULE LIST

    # ----------------------------------------------



    software_modules = softwareModule.objects.all().order_by(

        "-id"

    )





    context = {



        "software_modules": software_modules,



        "software_count": software_modules.count(),



    }





    return render(

        request,

        "software_module.html",

        context

    )







# ==========================================================

# SOFTWARE MODULE - UPDATE

# ==========================================================



def software_module_update(

    request,

    id

):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    software = get_object_or_404(

        softwareModule,

        id=id

    )





    if request.method == "POST":



        module_name = request.POST.get(

            "moduleName",

            ""

        ).strip()



        description = request.POST.get(

            "description",

            ""

        ).strip()





        # Checkbox

        is_active = (

            request.POST.get("is_active")

            == "on"

        )





        # ------------------------------------------

        # VALIDATION

        # ------------------------------------------



        if not module_name:



            messages.error(

                request,

                "Module Name is required."

            )



            return redirect(

                "software_module_update",

                id=id

            )





        if not description:



            messages.error(

                request,

                "Description is required."

            )



            return redirect(

                "software_module_update",

                id=id

            )





        # ------------------------------------------

        # DUPLICATE MODULE NAME CHECK

        # Current record ko exclude karenge

        # ------------------------------------------



        if softwareModule.objects.filter(

            moduleName=module_name

        ).exclude(

            id=id

        ).exists():



            messages.error(

                request,

                "Software Module Name already exists."

            )



            return redirect(

                "software_module_update",

                id=id

            )





        # ------------------------------------------

        # DUPLICATE DESCRIPTION

        # ------------------------------------------



        if softwareModule.objects.filter(

            description=description

        ).exclude(

            id=id

        ).exists():



            messages.error(

                request,

                "Description already exists."

            )



            return redirect(

                "software_module_update",

                id=id

            )





        # ------------------------------------------

        # UPDATE

        # ------------------------------------------



        software.moduleName = module_name



        software.description = description



        software.is_active = is_active



        software.save()





        messages.success(

            request,

            "Software Module updated successfully."

        )





        return redirect(

            "software_module_list"

        )





    context = {



        "software": software



    }





    return render(

        request,

        "software_module_update.html",

        context

    )







# ==========================================================

# SOFTWARE MODULE - DELETE

# ==========================================================



def software_module_delete(

    request,

    id

):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    software = get_object_or_404(

        softwareModule,

        id=id

    )





    if request.method == "POST":



        software.delete()





        messages.success(

            request,

            "Software Module deleted successfully."

        )





    return redirect(

        "software_module_list"

    )







# ==========================================================

# HARDWARE MODULE - CREATE + LIST

# ==========================================================



def hardware_module_list(request):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    if request.method == "POST":



        module_name = request.POST.get(

            "moduleName",

            ""

        ).strip()



        description = request.POST.get(

            "description",

            ""

        ).strip()





        # ------------------------------------------

        # VALIDATION

        # ------------------------------------------



        if not module_name:



            messages.error(

                request,

                "Module Name is required."

            )



            return redirect(

                "hardware_module_list"

            )





        if not description:



            messages.error(

                request,

                "Description is required."

            )



            return redirect(

                "hardware_module_list"

            )





        # ------------------------------------------

        # DUPLICATE MODULE NAME

        # ------------------------------------------



        if hardwareModule.objects.filter(

            moduleName=module_name

        ).exists():



            messages.error(

                request,

                "Hardware Module Name already exists."

            )



            return redirect(

                "hardware_module_list"

            )





        # ------------------------------------------

        # DUPLICATE DESCRIPTION

        # ------------------------------------------



        if hardwareModule.objects.filter(

            description=description

        ).exists():



            messages.error(

                request,

                "Description already exists."

            )



            return redirect(

                "hardware_module_list"

            )





        # ------------------------------------------

        # CREATE

        # ------------------------------------------



        hardwareModule.objects.create(



            moduleName=module_name,



            description=description,



            is_active=True

        )





        messages.success(

            request,

            "Hardware Module created successfully."

        )





        return redirect(

            "hardware_module_list"

        )





    # ----------------------------------------------

    # HARDWARE MODULE LIST

    # ----------------------------------------------



    hardware_modules = hardwareModule.objects.all().order_by(

        "-id"

    )





    context = {



        "hardware_modules": hardware_modules,



        "hardware_count": hardware_modules.count(),



    }





    return render(

        request,

        "hardware_module.html",

        context

    )







# ==========================================================

# HARDWARE MODULE - UPDATE

# ==========================================================



def hardware_module_update(

    request,

    id

):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    hardware = get_object_or_404(

        hardwareModule,

        id=id

    )





    if request.method == "POST":



        module_name = request.POST.get(

            "moduleName",

            ""

        ).strip()



        description = request.POST.get(

            "description",

            ""

        ).strip()





        is_active = (

            request.POST.get("is_active")

            == "on"

        )





        # ------------------------------------------

        # VALIDATION

        # ------------------------------------------



        if not module_name:



            messages.error(

                request,

                "Module Name is required."

            )



            return redirect(

                "hardware_module_update",

                id=id

            )





        if not description:



            messages.error(

                request,

                "Description is required."

            )



            return redirect(

                "hardware_module_update",

                id=id

            )





        # ------------------------------------------

        # DUPLICATE MODULE NAME

        # ------------------------------------------



        if hardwareModule.objects.filter(

            moduleName=module_name

        ).exclude(

            id=id

        ).exists():



            messages.error(

                request,

                "Hardware Module Name already exists."

            )



            return redirect(

                "hardware_module_update",

                id=id

            )





        # ------------------------------------------

        # DUPLICATE DESCRIPTION

        # ------------------------------------------



        if hardwareModule.objects.filter(

            description=description

        ).exclude(

            id=id

        ).exists():



            messages.error(

                request,

                "Description already exists."

            )



            return redirect(

                "hardware_module_update",

                id=id

            )





        # ------------------------------------------

        # UPDATE

        # ------------------------------------------



        hardware.moduleName = module_name



        hardware.description = description



        hardware.is_active = is_active



        hardware.save()





        messages.success(

            request,

            "Hardware Module updated successfully."

        )





        return redirect(

            "hardware_module_list"

        )





    context = {



        "hardware": hardware



    }





    return render(

        request,

        "hardware_module_update.html",

        context

    )







# ==========================================================

# HARDWARE MODULE - DELETE

# ==========================================================



def hardware_module_delete(

    request,

    id

):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    hardware = get_object_or_404(

        hardwareModule,

        id=id

    )





    if request.method == "POST":



        hardware.delete()





        messages.success(

            request,

            "Hardware Module deleted successfully."

        )





    return redirect(

        "hardware_module_list"

    )









def ticket_type_list(request):




    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    if request.method == "POST":

        name = request.POST.get("name")
        code = request.POST.get("code")
        description = request.POST.get("description")
        is_active = request.POST.get("is_active") == "1"
        # Name duplicate check
        if TicketTypeMaster.objects.filter(name__iexact=name).exists():
            messages.error(request,"Ticket Type Name already exists.")
            return redirect("ticket_type_list")
        # Code duplicate check
        if TicketTypeMaster.objects.filter(
            code__iexact=code
        ).exists():
            messages.error(request,"Ticket Type Code already exists.")
            return redirect("ticket_type_list")
        TicketTypeMaster.objects.create(name=name,code=code.upper(),description=description,is_active=is_active)
        messages.success(request,"Ticket Type created successfully.")
        return redirect("ticket_type_list")

    ticket_types = TicketTypeMaster.objects.all().order_by("-created_at")
    context = {"ticket_types": ticket_types}
    return render(request, "ticketTypemaster.html",context)

# ============================================================
# PRIORITY LIST + CREATE
# ============================================================
def priority_list(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "1"
        # Name required
        if not name:
            messages.error(request,"Priority Name is required.")
            return redirect("priority_list")

        # Code required

        if not code:
            messages.error(request,"Priority Code is required.")
            return redirect("priority_list")
        # Duplicate Name
        if PriorityMaster.objects.filter(name__iexact=name).exists():
            messages.error(request,"Priority Name already exists.")
            return redirect("priority_list")
        # Duplicate Code
        if PriorityMaster.objects.filter(code__iexact=code).exists():
            messages.error(request,"Priority Code already exists.")
            return redirect("priority_list")
        # Create
        PriorityMaster.objects.create(name=name,code=code.upper(),description=description, is_active=is_active)
        messages.success(request,"Priority created successfully.")
        return redirect("priority_list")
    priorities = PriorityMaster.objects.all().order_by("-created_at")
    context = {"priorities": priorities}
    return render(request,"priority_master.html",context)
# ============================================================
# PRIORITY UPDATE
# ============================================================
def priority_update(request, id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    priority = get_object_or_404(PriorityMaster,id=id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "1"
        # Duplicate Name
        if PriorityMaster.objects.filter(name__iexact=name).exclude( id=id).exists():
            messages.error(request,"Priority Name already exists.")
            return redirect("priority_list")
        # Duplicate Code
        if PriorityMaster.objects.filter(code__iexact=code).exclude(id=id).exists():
            messages.error(request,"Priority Code already exists.")
            return redirect("priority_list")
        priority.name = name
        priority.code = code.upper()
        priority.description = description
        priority.is_active = is_active
        priority.save()
        messages.success(request,"Priority updated successfully.")
    return redirect("priority_list")







# ============================================================
# PRIORITY DELETE
# ============================================================
def priority_delete(request, id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")
    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")
    priority = get_object_or_404(PriorityMaster,id=id)
    if request.method == "POST":
        priority.delete()
        messages.success(request,"Priority deleted successfully.")
    return redirect("priority_list")



# ==========================================================

# STATE MASTER

# ==========================================================

def state_master(request):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    # ------------------------------------------------------

    # ADD STATE

    # ------------------------------------------------------

    if request.method == "POST":



        name = request.POST.get("name", "").strip()

        code = request.POST.get("code", "").strip()

        description = request.POST.get("description", "").strip()



        # Validation

        if not name:

            messages.error(request, "State name is required.")

            return redirect("state_master")



        if not code:

            messages.error(request, "State code is required.")

            return redirect("state_master")





        # Check duplicate name

        if StateMaster.objects.filter(name__iexact=name).exists():

            messages.error(request, "State name already exists.")

            return redirect("state_master")





        # Check duplicate code

        if StateMaster.objects.filter(code__iexact=code).exists():

            messages.error(request, "State code already exists.")

            return redirect("/role/state_masters/")





        # Create State

        StateMaster.objects.create(

            name=name,

            code=code,

            description=description if description else None,

            is_active=True

        )



        messages.success(

            request,

            "State added successfully."

        )



        return redirect("/role/state_masters/")





    # ------------------------------------------------------

    # GET STATE LIST

    # ------------------------------------------------------

    states = StateMaster.objects.all().order_by("name")



    context = {

        "states": states

    }



    return render(

        request,

        "state_master.html",

        context

    )



# ==========================================================

# DISTRICT MASTER

# ==========================================================

def district_master(request):




    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    # ======================================================

    # CREATE DISTRICT

    # ======================================================

    if request.method == "POST":

        state_id = request.POST.get("state")

        name = request.POST.get("name", "").strip()

        code = request.POST.get("code", "").strip()

        description = request.POST.get("description", "").strip()

        is_active = request.POST.get("is_active", "1")



        # ==================================================

        # VALIDATION

        # ==================================================



        if not state_id:

            messages.error(

                request,

                "Please select a state."

            )

            return redirect("district_master")



        if not name:

            messages.error(

                request,

                "District name is required."

            )



            return redirect("district_master")



        if not code:

            messages.error(

                request,

                "District code is required."

            )



            return redirect("/role/district_masters/")





        # ==================================================

        # CHECK STATE

        # ==================================================



        try:



            state = StateMaster.objects.get(

                id=state_id,

                is_active=True

            )



        except StateMaster.DoesNotExist:



            messages.error(

                request,

                "Selected state is invalid."

            )

            return redirect("/role/district_masters/")



        # ==================================================

        # DUPLICATE DISTRICT NAME

        # Same district name in same state

        # ==================================================

        if DistrictMaster.objects.filter(

            state=state,

            name__iexact=name

        ).exists():



            messages.error(

                request,

                "This district already exists in the selected state."

            )



            return redirect("/role/district_masters/")





        # ==================================================

        # DUPLICATE CODE

        # ==================================================



        if DistrictMaster.objects.filter(

            code__iexact=code

        ).exists():



            messages.error(

                request,

                "District code already exists."

            )



            return redirect("/role/district_masters/")





        # ==================================================

        # CREATE DISTRICT

        # ==================================================



        DistrictMaster.objects.create(

            state=state,

            name=name,

            code=code,

            description=(

                description

                if description

                else None

            ),



            is_active=(

                True

                if is_active == "1"

                else False

            )

        )





        messages.success(

            request,

            "District created successfully."

        )



        return redirect("/role/district_masters/")





    # ======================================================

    # GET ACTIVE STATES

    # ======================================================



    states = StateMaster.objects.filter(

        is_active=True

    ).order_by("name")





    # ======================================================

    # GET DISTRICT LIST

    # ======================================================



    districts = DistrictMaster.objects.select_related(

        "state"

    ).order_by("state__name", "name")





    # ======================================================

    # CONTEXT

    # ======================================================



    context = {

        "states": states,

        "districts": districts,



    }





    return render(

        request,

        "district_master.html",

        context

    )

from django.shortcuts import render, redirect

from django.contrib import messages



from .models import StateMaster, DistrictMaster, GateMaster





# ==========================================================

# GATE MASTER

# ==========================================================

def gate_master(request):


    user = get_logged_in_user(request)

    if not user:
        messages.error(request,"Please login first.")
        return redirect("login")

    if user.role.name.strip().lower() != "admin" and not user_has_permission(request,"MASTER_ACCESS"):
        messages.error(request,"You are not authorized for this.")
        return redirect("/raise/index/")

    # ======================================================
    # CREATE GATE
    # ======================================================
    if request.method == "POST":
        gate_name = request.POST.get("gate_name", "").strip()
        state_id = request.POST.get("state")
        district_id = request.POST.get("district")
        latitude = request.POST.get("latitude","").strip()
        longitude = request.POST.get("longitude","").strip()
        is_electricity = request.POST.get("is_electricity")
        is_divider = request.POST.get("is_divider")
        lane = request.POST.get("lane","1")
        active_lanes = request.POST.get("active_lanes","1")
        installation_date = request.POST.get("installation_date","")
        is_active = request.POST.get("is_active","1")
        # ==================================================

        # BASIC VALIDATION

        # ==================================================



        if not gate_name:



            messages.error(

                request,

                "Gate name is required."

            )



            return redirect(

                "/role/gate_masters/"

            )





        if not state_id:



            messages.error(

                request,

                "Please select a state."

            )



            return redirect(

                "/role/gate_masters/"

            )





        if not district_id:



            messages.error(

                request,

                "Please select a district."

            )



            return redirect(

                "/role/gate_masters/"

            )





        # ==================================================

        # GATE NAME DUPLICATE CHECK

        # ==================================================



        if GateMaster.objects.filter(

            gate_name__iexact=gate_name

        ).exists():



            messages.error(

                request,

                "Gate name already exists."

            )



            return redirect(

                "/role/gate_masters/"

            )





        # ==================================================

        # GET STATE

        # ==================================================



        try:



            state = StateMaster.objects.get(

                id=state_id,

                is_active=True

            )



        except StateMaster.DoesNotExist:



            messages.error(

                request,

                "Selected state is invalid."

            )



            return redirect(

                "/role/gate_masters/"

            )





        # ==================================================

        # GET DISTRICT

        # Selected district must belong to selected state

        # ==================================================



        try:



            district = DistrictMaster.objects.get(

                id=district_id,

                state=state,

                is_active=True

            )



        except DistrictMaster.DoesNotExist:



            messages.error(

                request,

                "Selected district does not belong to the selected state."

            )



            return redirect(

                "/role/gate_masters/"

            )





        # ==================================================

        # LANE VALIDATION

        # ==================================================



        try:



            lane = int(lane)



            active_lanes = int(

                active_lanes

            )



        except (TypeError, ValueError):



            messages.error(

                request,

                "Lane values must be valid numbers."

            )



            return redirect(

                "/role/gate_masters/"

            )





        if lane < 1:



            messages.error(

                request,

                "Total lanes must be at least 1."

            )



            return redirect(

                "/role/gate_masters/"

            )





        if active_lanes < 0:



            messages.error(

                request,

                "Active lanes cannot be negative."

            )



            return redirect(

                "/role/gate_masters/"

            )





        if active_lanes > lane:



            messages.error(

                request,

                "Active lanes cannot be greater than total lanes."

            )



            return redirect(

                "/role/gate_masters/"

            )





        # ==================================================

        # CREATE GATE

        # ==================================================



        GateMaster.objects.create(



            gate_name=gate_name,



            StateMaster=state,



            district=district,



            latitude=(

                latitude

                if latitude

                else None

            ),



            longitude=(

                longitude

                if longitude

                else None

            ),



            is_electricity=(

                True

                if is_electricity == "1"

                else False

            ),



            is_divider=(

                True

                if is_divider == "1"

                else False

            ),



            lane=lane,



            active_lanes=active_lanes,



            installation_date=(

                installation_date

                if installation_date

                else None

            ),



            is_active=(

                True

                if is_active == "1"

                else False

            )



        )





        messages.success(

            request,

            "Gate created successfully."

        )





        return redirect(

            "/role/gate_masters/"

        )

    # ======================================================

    # GET ACTIVE STATES

    # ======================================================
    states = StateMaster.objects.filter(is_active=True).order_by("name")
    # ======================================================
    # GET ACTIVE DISTRICTS
    # ======================================================
    districts = DistrictMaster.objects.filter(is_active=True).select_related("state").order_by("state__name","name")
    # ======================================================
    # GET GATE LIST
    # ======================================================
    gates = GateMaster.objects.select_related("StateMaster","district").order_by("-created_at")
    # ======================================================
    # CONTEXT
    # ======================================================
    context = {"states": states,"districts": districts,"gates": gates,}
    return render(request,"gate_master.html",context)
def menu_create(request):
    menus = Menu.objects.select_related("parent").order_by("name")
    if request.method == "POST":
        name = request.POST.get("name")
        url_name = request.POST.get("url_name")
        parent_id = request.POST.get("parent")
        parent = None
        if parent_id:
            parent = Menu.objects.filter(id=parent_id).first()
        Menu.objects.create(name=name,url_name=url_name if url_name else None,parent=parent)
        return redirect("/master/meanu_master/")
    context = {"menus": menus}
    return render(request, "menu_create.html", context)

def submenuURL(request):
    parent_menus = Menu.objects.filter(
        parent_id__isnull=True
    ).order_by("name")
    submenus = []
    selected_parent_id = request.GET.get("parent_id")
    if selected_parent_id:
        submenus = Menu.objects.filter(
            parent_id=selected_parent_id
        ).order_by("name")

    if request.method == "POST":
        submenu_id = request.POST.get("submenu_id")
        url_name = request.POST.get("url_name")
        submenu = Menu.objects.filter(id=submenu_id).first()
        if submenu:
            submenu.url_name = url_name
            submenu.save()
            messages.success(request,"Submenu URL saved successfully.")
        else:
            messages.error(request,"Submenu not found.")
        return redirect("/masters/sub-menu-create/")
    context = {"parent_menus": parent_menus,"submenus": submenus,"selected_parent_id": selected_parent_id}
    return render(request,"submenu_url.html",context)

def week_off_master(request):

    today = date.today()

    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    if request.method == "POST":

        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        weekly_days = request.POST.getlist("weekly_days")
        saturday_weeks = request.POST.getlist("saturday_weeks")

        total_days = calendar.monthrange(year, month)[1]

        saturday_count = 0
        created_count = 0

        for day in range(1, total_days + 1):

            current_date = date(year, month, day)

            weekday = current_date.weekday()

            day_name = current_date.strftime("%A")

            off_type = None
            description = ""

            # Weekly Off: Sunday, Monday etc.
            if str(weekday) in weekly_days:

                off_type = "WEEKLY"
                description = "Weekly " + day_name

            # Saturday Off: 2nd, 4th etc.
            if weekday == 5:
                saturday_count += 1
                if str(saturday_count) in saturday_weeks:
                    off_type = "MONTHLY"
                    description = str(saturday_count) + " Saturday"
            # Database mein save
            if off_type:
                if not WeekOffMaster.objects.filter(
                    off_date=current_date
                ).exists():
                    WeekOffMaster.objects.create(
                        off_date=current_date,
                        day_name=day_name,
                        off_type=off_type,
                        description=description,
                        is_active=True
                    )
                    created_count += 1

        messages.success(
            request,
            f"{created_count} Week Off created successfully.")
        return redirect(f"/role/week-off-master/?month={month}&year={year}")
    week_offs = WeekOffMaster.objects.filter(
        off_date__month=month,
        off_date__year=year
    ).order_by("off_date")

    months = []

    for i in range(1, 13):
        months.append((i, calendar.month_name[i]))

    context = {
        "week_offs": week_offs,
        "months": months,
        "selected_month": month,
        "selected_year": year,
        "total_week_offs": week_offs.count()
    }

    return render(request, "week_off_master.html", context)


def week_off_delete(request, id):

    if request.method == "POST":

        week_off = WeekOffMaster.objects.filter(id=id).first()

        if week_off:

            month = week_off.off_date.month
            year = week_off.off_date.year

            week_off.delete()

            messages.success(
                request,
                "Week Off deleted successfully."
            )

            return redirect(
                f"/role/week-off-master/?month={month}&year={year}"
            )

    return redirect("week_off_master")





# ==========================================================
# WORKING HOURS MASTER
# ==========================================================

def working_hours_master(request):

    # ======================================================
    # CURRENT MONTH AND YEAR
    # ======================================================

    today = timezone.localdate()

    selected_month = today.month
    selected_year = today.year

    # ======================================================
    # MONTH LIST
    # ======================================================

    months = [
        {
            "id": month,
            "name": calendar.month_name[month]
        }
        for month in range(1, 13)
    ]

    # ======================================================
    # YEAR LIST
    # ======================================================

    years = range(
        today.year - 2,
        today.year + 6
    )

    # ======================================================
    # POST REQUEST
    # ======================================================

    if request.method == "POST":

        # ==================================================
        # GET FORM DATA
        # ==================================================

        month = request.POST.get("month")
        year = request.POST.get("year")

        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # ==================================================
        # REQUIRED FIELD VALIDATION
        # ==================================================

        if not all([month, year, start_time, end_time]):

            messages.error(
                request,
                "All fields are required."
            )

            return redirect("working_hours_master")

        # ==================================================
        # MONTH AND YEAR VALIDATION
        # ==================================================

        try:
            month = int(month)
            year = int(year)

            if not (1 <= month <= 12):
                raise ValueError()

            if not (2000 <= year <= 2100):
                raise ValueError()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please select a valid Month and Year."
            )

            return redirect("working_hours_master")

        # ==================================================
        # TIME CONVERSION
        # ==================================================

        try:

            start_time = datetime.strptime(
                start_time,
                "%H:%M"
            ).time()

            end_time = datetime.strptime(
                end_time,
                "%H:%M"
            ).time()

        except ValueError:
            messages.error(request,"Invalid Working Hours.")
            return redirect("working_hours_master")

        # ==================================================
        # START AND END TIME VALIDATION
        # ==================================================

        if end_time <= start_time:

            messages.error(
                request,
                "Ending Working Hours must be greater than Starting Working Hours."
            )

            return redirect("working_hours_master")

        # ==================================================
        # CHECK EXISTING MONTH AND YEAR
        # ==================================================

        existing_record = WorkingHoursMaster.objects.filter(
            month=month,
            year=year
        ).first()

        # ==================================================
        # UPDATE EXISTING RECORD
        # ==================================================

        if existing_record:

            existing_record.start_time = start_time
            existing_record.end_time = end_time

            existing_record.save()

            messages.success(
                request,
                "Working Hours updated successfully."
            )

        # ==================================================
        # CREATE NEW RECORD
        # ==================================================

        else:

            WorkingHoursMaster.objects.create(
                month=month,
                year=year,
                start_time=start_time,
                end_time=end_time
            )

            messages.success(
                request,
                "Working Hours created successfully."
            )

        return redirect("working_hours_master")

    # ======================================================
    # GET WORKING HOURS RECORDS
    # ======================================================

    records = list(
        WorkingHoursMaster.objects.all()
        .order_by("-year", "-month")
    )

    # ======================================================
    # CALCULATE TOTAL WORKING HOURS
    # ======================================================

    for record in records:

        start_datetime = datetime.combine(
            today,
            record.start_time
        )

        end_datetime = datetime.combine(
            today,
            record.end_time
        )

        duration = end_datetime - start_datetime

        total_minutes = max(
            0,
            int(duration.total_seconds() // 60)
        )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        record.duration_display = (
            f"{hours}h {minutes:02d}m"
        )

        record.month_name = calendar.month_name[
            record.month
        ]

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {
        "months": months,
        "years": years,
        "records": records,
        "selected_month": selected_month,
        "selected_year": selected_year
    }

    # ======================================================
    # RENDER TEMPLATE
    # ======================================================

    return render(
        request,
        "working_hours_master.html",
        context
    )