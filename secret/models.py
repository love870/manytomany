from tkinter.tix import Tree
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager
from datetime import datetime
from django.utils import timezone


# Create your models here.

class CourseLevels(models.Model):
    class Meta:
        db_table = "course_levels"

    id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=15, blank=False, null=False, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(('active'), default=True)
    def __str__(self):
        return self.level

class TimePeriods(models.Model):
    class Meta:
        db_table = "time_periods"

    id = models.AutoField(primary_key=True)
    duration = models.CharField(max_length=50, blank=False, null=False, unique=True)
    is_active = models.BooleanField(('active'), default=True)


class Weekdays(models.Model):
    class Meta:
        db_table = "weekdays"

    id = models.AutoField(primary_key=True)
    day = models.CharField(max_length=15, blank=False, null=False, unique=True)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.day


class Courses(models.Model):
    class Meta:
        db_table = "courses"

    id = models.AutoField(primary_key=True)
    course_name = models.CharField(blank=False, null=False, max_length=50, default=None, unique=True)
    duration_value = models.IntegerField(blank=True, null=True, default=None)
    duration_period = models.ForeignKey(TimePeriods, on_delete=models.PROTECT, blank=True, null=True, default=None)
    level = models.ForeignKey(CourseLevels, on_delete=models.PROTECT, blank=False, null=True, default=None)
    course_description = models.CharField(blank=False, null=False, max_length=10000, default=None)
    price_per_week = models.FloatField(blank=False, null=False, default=None)
    price_per_month = models.FloatField(blank=False, null=False, default=None)
    free_duration = models.CharField(blank=False, null=False, max_length=100, default="None")
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
         return self.course_name

class Course_Schedules(models.Model):
    class Meta:
        db_table = "course_schedules"

    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Courses, on_delete=models.PROTECT, blank=False, null=False, default=None)
    day_of_week = models.ForeignKey(Weekdays, on_delete=models.PROTECT, blank=False, null=False, default=None)
    start_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    end_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)



class Course_Classes(models.Model):
    class Meta:
        db_table = "course_classes"

    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Courses, on_delete=models.PROTECT, blank=False, null=False, default=None)
    day_of_week = models.ForeignKey(Weekdays, on_delete=models.PROTECT, blank=False, null=False, default=None)
    start_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    end_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    class_date = models.DateField(blank=False, null=False, default=None)
    class_grade = models.CharField(max_length=20, blank=False, null=False, default=None)
    teacher_id = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, default=None)
    class_link = models.TextField(max_length=1000, blank=True, null=True, default=None)
    recorded_link = models.TextField(max_length=1000, blank=True, null=True, default=None)
    address=models.TextField(max_length=120, blank=True, null=True,default=None)
    class_type = models.CharField(max_length=140, blank=True, default='') #new field
    section = models.CharField(max_length=20, blank=True, null=True, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status=models.BooleanField(('status'),default=False)

    
def __str__(self):
   return self.course_id

class Class_Schedules(models.Model):
    class Meta:
        db_table = "class_Schedules"

    id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Course_Classes, on_delete=models.PROTECT, blank=False, null=False, default=None)
    day_of_week = models.ForeignKey(Weekdays, on_delete=models.PROTECT, blank=False, null=False, default=None)
    start_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    end_time = models.TimeField(auto_now=False, auto_now_add=False, blank=False, null=False, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Promocodes(models.Model):
    class Meta:
        db_table = "promocodes"

    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Courses, on_delete=models.PROTECT, blank=False, null=False, default=None)
    course_duration = models.CharField(max_length=20, blank=False, null=False, default=None)
    code = models.CharField(max_length=20, blank=False, null=False, unique=True)
    discount_percentage = models.IntegerField(blank=False, null=False, default=None)
    start_date = models.DateField(blank=False, null=False, default=None)
    end_date = models.DateField(blank=False, null=False, default=None)
    used_count = models.IntegerField(blank=True, null=True, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Orders(models.Model):
    class Meta:
        db_table = "orders"

    id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False, default=None)
    billing_address = models.CharField(max_length=255, blank=True, null=True, default=None)
    grand_total_amt = models.FloatField(blank=False, null=False, default=None)
    is_active = models.BooleanField(('active'), default=True)
    selected_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Class_Students(models.Model):
    class Meta:
        db_table = "class_students"

    id = models.AutoField(primary_key=True)
    course_class_id = models.ForeignKey(Course_Classes, on_delete=models.PROTECT, blank=False, null=False, default=None)
    order_id = models.ForeignKey(Orders, on_delete=models.PROTECT, blank=False, null=False, default=None)
    number_of_seats = models.IntegerField(blank=False, null=False, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Payments(models.Model):
    class Meta:
        db_table = "payments"

    transaction_mode_choices = (
        ('Online', 'Online'),
    )

    transaction_platform_choices = (
        ('Paypal', 'Paypal'),
    )

    transaction_status_choices = (
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    )

    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, on_delete=models.PROTECT, blank=False, null=False, default=None, unique=False)
    promocode_id = models.ForeignKey(Promocodes, on_delete=models.PROTECT, blank=False, null=True, default=None)
    transaction_amt = models.FloatField(blank=False, null=False, default=None)
    transaction_id = models.TextField(max_length=1000, blank=True, null=True)
    transaction_mode = models.CharField(max_length=50, choices=transaction_mode_choices, blank=False, null=False)
    transaction_platform = models.CharField(max_length=50, choices=transaction_platform_choices, blank=False,
                                            null=False)
    transaction_status = models.CharField(max_length=50, choices=transaction_status_choices, blank=False, null=False)
    transaction_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Order_Items(models.Model):
    class Meta:
        db_table = "order_items"

    course_duration_choices = (
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    )

    id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, on_delete=models.PROTECT, blank=False, null=False, default=None)
    course_id = models.ForeignKey(Courses, on_delete=models.PROTECT, blank=False, null=False, default=None)
    course_price = models.FloatField(blank=False, null=False, default=None)
    course_duration = models.CharField(max_length=50, choices=course_duration_choices, blank=False, null=False)
    # number_of_seats = models.IntegerField(blank=False,null=False, default=None)
    child_name = models.CharField(max_length=50, blank=False, null=False, default=None)
    child_grade = models.CharField(max_length=50, blank=False, null=False, default=None)
    child_interests = models.CharField(max_length=100, blank=False, null=False, default=None)
    child_age = models.IntegerField(blank=False, null=False, default=None)
    is_active = models.BooleanField(('active'), default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class classs(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)

    def __str__(self):
        return self.name

class AddStudent(models.Model):
    id = models.AutoField(primary_key=True)
    username=models.ForeignKey(User, related_name='usernames',on_delete=models.CASCADE)
    first_name=models.CharField(max_length=30, null=True)
    last_name=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    image_upload= models.FileField(upload_to = 'images',max_length=100,null=True,default=None)
    students=models.ManyToManyField(classs)

def __str__(self):
   return self.first_name



