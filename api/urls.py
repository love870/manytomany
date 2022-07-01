from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import (
    Register,
    Login,
    Logout,
    Dashboard,
    MyProfile,
    Avatar,
    ChangePassword,
    ForgotPassword,
    verify_email,
    ForgotPassword_addition
)
from api.courses.courses import (
    all_courses,
    confirmed_classes,
    teacher_available_classes,
    teacher_claim_class,
    teacher_claimed_classes,
    teacher_add_zoom_link,
    V2_teacher_available_classes,
    V2_teacher_claim_class,
)
from api.courses.orders import add_order
from api.payments.payments import add_payment, validate_promocode, payment_history


urlpatterns = [
    path("register/", Register),
    path("login/", Login),
    path("profile/", MyProfile),
    path("avatar/", Avatar),
    path("change-password/", ChangePassword),
    path("forgot-password/", ForgotPassword),
    path("forgot-password-addition/", ForgotPassword_addition),
    path("logout/", Logout),
    path("home/", Dashboard),
    path("all_courses/", all_courses),
    path("confirmed_classes/", confirmed_classes),
    path("teacher_available_classes/", teacher_available_classes),
    path("teacher_claim_class/", teacher_claim_class),
    path("teacher_claimed_classes/", teacher_claimed_classes),
    path("teacher_add_zoom_link/", teacher_add_zoom_link),
    path("add_order/", add_order),
    path("add_payment/", add_payment),
    path("validate_promocode/", validate_promocode),
    path("payment_history/", payment_history),
    path("verify_email/", verify_email),
    # v2
    path("v2/teacher_available_classes/", V2_teacher_available_classes),
    path("v2/teacher_claim_class/", V2_teacher_claim_class),
]
urlpatterns = format_suffix_patterns(urlpatterns)
