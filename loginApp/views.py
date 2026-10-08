
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from .models import Registeruse
from masterApp.models import *


def user_list(request):
    # ==========================================
    # CREATE USER
    # ==========================================
    if request.method == "POST":
        role_id = request.POST.get("role")
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        # --------------------------------------
        # Basic validation
        # --------------------------------------
        if not role_id:
            messages.error(request, "Please select a role.")
            return redirect("user_list")

        if not name:
            messages.error(request, "Name is required.")
            return redirect("user_list")

        if not email:
            messages.error(request, "Email is required.")
            return redirect("user_list")

        if not mobile:
            messages.error(request, "Mobile number is required.")
            return redirect("user_list")

        if not password:
            messages.error(request, "Password is required.")
            return redirect("user_list")

        # --------------------------------------
        # Email duplicate check
        # --------------------------------------
        if Registeruse.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("user_list")

        # --------------------------------------
        # Mobile duplicate check
        # --------------------------------------
        if Registeruse.objects.filter(mobile=mobile).exists():

            messages.error(
                request,
                "Mobile number already exists."
            )

            return redirect("user_list")

        # --------------------------------------
        # Role get
        # --------------------------------------
        try:

            role = Role.objects.get(
                id=role_id
            )

        except Role.DoesNotExist:

            messages.error(
                request,
                "Selected role does not exist."
            )

            return redirect("user_list")

        # --------------------------------------
        # Create User
        # --------------------------------------
        Registeruse.objects.create(

            role=role,

            name=name,

            email=email,

            mobile=mobile,

            # Password hash karke save hoga
            password=make_password(password),

            is_active=True
        )

        messages.success(
            request,
            "User created successfully."
        )

        return redirect("user_list")

    # ==========================================
    # GET REQUEST
    # ==========================================

    users = Registeruse.objects.select_related(
        "role"
    ).order_by("-created_at")
    roles = Role.objects.filter(
        is_active=True
    ).order_by("name")
    context = {

        "users": users,
        "roles": roles,
        "user_count": users.count(),

    }
    return render( request,"user_cretate.html",context)

# authApp/views.py






def login_view(request):
    # ==========================================
    # ALREADY LOGGED IN
    # ==========================================
    if request.session.get("user_id"):
        return redirect("/raise/index/")
    # ==========================================
    # LOGIN POST REQUEST
    # ==========================================
    if request.method == "POST":
        email = request.POST.get(
            "email",
            ""
        ).strip()
        password = request.POST.get(
            "password",
            ""
        )
        # ======================================
        # VALIDATION
        # ======================================

        if not email:
            messages.error(
                request,
                "Email is required."
            )
            return redirect("/")
        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return redirect("/")


        # ======================================
        # USER FIND BY EMAIL
        # ======================================

        try:

            user = Registeruse.objects.select_related(
                "role"
            ).get(
                email=email
            )


        except Registeruse.DoesNotExist:

            messages.error(
                request,
                "Invalid email or password."
            )

            return redirect("/")


        # ======================================
        # ACTIVE USER CHECK
        # ======================================

        if not user.is_active:

            messages.error(
                request,
                "Your account is inactive."
            )

            return redirect("/")


        # ======================================
        # PASSWORD CHECK
        # ======================================

        if not check_password(
            password,
            user.password
        ):

            messages.error(
                request,
                "Invalid email or password."
            )

            return redirect("/")


        # ======================================
        # LOGIN SUCCESS - SESSION CREATE
        # ======================================

        request.session["user_id"] = user.id
        request.session["name"] = user.name
        request.session["email"] = user.email
        request.session["role_id"] = user.role.id
        request.session["role_name"] = user.role.name


        # ======================================
        # SUCCESS MESSAGE
        # ======================================

        messages.success(
            request,
            f"Welcome {user.name}"
        )


        return render(request,"index.html")


    # ==========================================
    # GET REQUEST
    # ==========================================

    return render(
        request,
        "login.html"
    )
    
def logout_view(request):
    # Complete session clear
    request.session.flush()
    messages.success(request,
"You have been logged out successfully."
    )
    return redirect("/")