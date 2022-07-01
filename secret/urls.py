from ast import If
from django.urls import path
from requests import delete
from rest_framework.urlpatterns import format_suffix_patterns
from secret.views import (
    Dashboard,
    Login,
    Register,
    ForgotPassword,
    SampleReports,
    SampleListing,
    Logout,
    Settings,
    ChangePassword,
    Profile,
    
)
from django.conf import settings
from django.conf.urls.static import static
from secret.courses.courses import addstudent,view_image

from secret.users.users import add_user, list_users, delete_user, edit_user
from secret.courses.courses import add_course, list_courses, delete_course, edit_course, course_class
from secret.courses.schedules import (
    add_schedule,
    add_schedule_ajax,
    edit_schedule,
    record_delete,
)
from django.conf.urls.static import static
from secret.classes.classes import list_classes, class_details, class_edit, add_class_schedule
from secret.payments.payments import order_items, list_payments
from secret.promocodes.promocodes import (
    list_promocodes,
    delete_promocode,
    add_promocode,
    edit_promocode,
)

urlpatterns = [
    path("", Dashboard),
    path("login/", Login, name="secretLogin"),
    path("register/", Register),
    path("forgot-password/", ForgotPassword),
    path("sample-listing/", SampleListing),
    path("sample-reports/", SampleReports),
    path("settings/", Settings),
    path("profile/", Profile),
    path("change-password/", ChangePassword),
    path("logout/", Logout),
    # users
    path("add_user/", add_user),
    path("list_users/", list_users),
    path("delete_user/", delete_user),
    path("edit_user/<int:id>/", edit_user),
    # Courses
    path("add_course/", add_course, name='add_course'),
    path("list_courses/", list_courses),
    path("course_class/", course_class),
    path("add_student/",addstudent),
    path("view_image/",view_image),

    # class
    path("delete_course/", delete_course),
    path("edit_course/<int:id>/", edit_course),
    # Schedules
    path("add_schedule/", add_schedule, name='add_schedule'),
    path("add_schedule_ajax/", add_schedule_ajax),
    path("edit_schedule/<int:id>/", edit_schedule, name="edit"),
    # path("delete_schedule/", delete_schedule),
    # classes
    path("list_classes/", list_classes),
    path("class_details/<int:id>/", class_details),
    path("class_edit/<int:id>/", class_edit),
    path("add_class_schedule/", add_class_schedule),
    # payments
    path("order_items/<int:id>/", order_items),
    path("list_payments/", list_payments),
    # promocodes
    path("add_promocode/", add_promocode),
    path("list_promocodes/", list_promocodes),
    path("delete_promocode/", delete_promocode),
    path("edit_promocode/<int:id>/", edit_promocode),
    path('delete/<int:id>',record_delete,name='delete'),

 
     
    
]+ static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)
 
