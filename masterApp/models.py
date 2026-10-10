from django.db import models


class Permission(models.Model):
    name = models.CharField( max_length=100 )
    code = models.CharField( max_length=100, unique=True )
    description = models.TextField( blank=True, null=True )
    is_active = models.BooleanField( default=True )
    created_at = models.DateTimeField( auto_now_add=True )

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, through="RolePermissionMapping", related_name="roles", blank=True)
    is_active = models.BooleanField( default=True )
    created_at = models.DateTimeField( auto_now_add=True)

class RolePermissionMapping(models.Model):
    role = models.ForeignKey(Role,on_delete=models.CASCADE,related_name="permission_mappings")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE,related_name="role_mappings")
    is_active = models.BooleanField( default=True )
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True )

class softwareModule(models.Model):
    moduleName = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField( default=True )
    
class hardwareModule(models.Model):
    moduleName = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField( default=True )

class TicketTypeMaster(models.Model):
    name = models.CharField(max_length=100,unique=True)
    code = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=255,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class PriorityMaster(models.Model):
    name = models.CharField(max_length=100,unique=True)
    code = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=255,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StateMaster(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )
    code = models.CharField(
        max_length=50,
        unique=True
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

class DistrictMaster(models.Model):

    state = models.ForeignKey(StateMaster,on_delete=models.PROTECT,related_name="districts")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=255,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GateMaster(models.Model):
    gate_name = models.CharField(max_length=150,unique=True)
    StateMaster = models.ForeignKey("StateMaster" , related_name="gate_sate", on_delete=models.PROTECT)
    district = models.ForeignKey("DistrictMaster",on_delete=models.PROTECT,related_name="gates")
    latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    is_electricity = models.BooleanField(default=False)
    is_divider = models.BooleanField(default=False)
    lane = models.PositiveIntegerField(default=1)
    active_lanes = models.PositiveIntegerField(default=1)
    installation_date = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Menu(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=100,blank=True,null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,blank=True,null=True,related_name="submenus")
        


from django.db import models


class WeekOffMaster(models.Model):
    off_date = models.DateField(unique=True)
    day_name = models.CharField(max_length=15)
    off_type = models.CharField(max_length=20)
    description = models.CharField(max_length=150,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["off_date"]

from django.db import models


class WorkingHoursMaster(models.Model):

    month = models.PositiveSmallIntegerField(unique=True)
    year = models.PositiveSmallIntegerField(unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-year", "-month"]
        