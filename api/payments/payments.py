from __future__ import unicode_literals
import sys, os, json, io, base64, hashlib, re
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F

from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from datetime import date, datetime

from api.serializers.classes import add_class_link_serializer
from api.serializers.orders import add_order_serializer, add_child_serializer
from api.models import Profile, Timezones, Roles
from secret.models import (
    Courses,
    Course_Classes,
    Course_Schedules,
    Orders,
    Order_Items,
    Payments,
    Promocodes,
)
from django.conf import settings
from django.core.mail import send_mail

def checkAuth(request):
    if Token.objects.filter(key=request.META.get("HTTP_TOKEN")):
        return Token.objects.filter(key=request.META.get("HTTP_TOKEN")).values(
            "user_id"
        )[0]
    else:
        return 0


def checkTimezone(request):
    if Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE")):
        return Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE"))[0]
    else:
        return 0


@api_view(["POST"])
def validate_promocode(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)
    try:
        user_id = token["user_id"]
        reqdata = json.loads(request.body.decode("utf-8"))

        # updating inactive objects
        Promocodes.objects.filter(end_date__lt=datetime.now()).update(is_active=0)

        if reqdata["code"] and reqdata["course_duration"] and reqdata["course_id"]:
            code = reqdata["code"]
            course_duration = reqdata["course_duration"]
            course_id = reqdata["course_id"]
            promocode_obj = (
                Promocodes.objects.filter(course_id=course_id)
                .filter(course_duration=course_duration, code=code)
                .values("id", "discount_percentage", "is_active")
            )
            if promocode_obj:
                code_obj = promocode_obj[0]
                if code_obj["is_active"] == True:
                    discount_percentage = code_obj["discount_percentage"]
                    promocode_id = code_obj["id"]
                    data = {
                        "status": 200,
                        "data": {
                            "message": "Promocode applied successfully!",
                            "discount_percentage": discount_percentage,
                            "promocode_id": promocode_id,
                        },
                    }
                    return JsonResponse(data)
                else:
                    data = {
                        "status": 204,
                        "data": {"message": "Expired or Inactive Promocode!"},
                    }
                    return JsonResponse(data)

            else:
                data = {"status": 204, "data": {"message": "Invalid Promocode!"}}
                return JsonResponse(data)

        else:
            data = {"status": 204, "data": {"message": "Missing params!"}}
            return JsonResponse(data)
    except Exception as E:
        print(E)
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(E)},
        }
        return JsonResponse(data)


@api_view(["POST"])
def add_payment(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)
    try:
        
        user_id = token["user_id"]
        reqdata = json.loads(request.body.decode("utf-8"))
        order_id = reqdata["order_id"]
        course_id = reqdata["course_id"]
        email = reqdata["email"]
        print("course_id", course_id)
        # checking if order_id is present in body
       
        if course_id:
            course = Course_Classes.objects.filter(course_id=course_id)[0] 
            print(course, "course")
        if order_id:
            try:
                if not reqdata["promocode_id"]:
                    promocode_id = None
                    
                else:
                    promocode_id = reqdata["promocode_id"]
            except Exception as E:
                print(E, 'ee')
                promocode_id = None
            # checking existence of order id in orders table
            if Orders.objects.filter(id=order_id):
                # checking existence of order id in payments table
                if Payments.objects.filter(order_id=order_id):
                    data = {"status": 400, "data": {"message": "Payment already Done"}}
                    return JsonResponse(data)
                else:
                    # creating payment
                    Payments.objects.create(
                        order_id=Orders.objects.get(id=order_id),
                        transaction_amt=reqdata["transaction_amt"],
                        transaction_id=reqdata["transaction_id"],
                        transaction_mode="Online",
                        transaction_platform="Paypal",
                        transaction_status="Success",
                        transaction_date=datetime.now(),
                        promocode_id_id=promocode_id
                    )
                    subject ="Payment Details..."
                    message = f"Payment Sucessfull for class scheduled on{course.day_of_week.day} having class of grade {course.class_grade} with instructor named {course.teacher_id.username} for course section named {course.section} with class link {course.class_link} and record link {course.recorded_link}"
                    
                    from_email = settings.EMAIL_HOST_USER
              
                    send_mail(subject, message, from_email,[email])
                    # updating order and order items
                    Orders.objects.filter(id=order_id).update(is_active=1)
                    Order_Items.objects.filter(order_id=order_id).update(is_active=1)
                    try:
                        # Increment coupon used_count
                        Promocodes.objects.filter(id=promocode_id).update(
                            used_count=F("used_count") + 1
                        )
                    except Exception as E:
                        print(E)

                    data = {
                        "status": 200,
                        "data": {"message": "Payment Done successfully"},
                    }
                    return JsonResponse(data)
            else:
                data = {"status": 400, "data": {"message": "Order Id not present"}}
                return JsonResponse(data)
        else:
            data = {"status": 400, "data": {"message": "order id is missing"}}
            return JsonResponse(data)

    except Exception as E:
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(E)},
        }
        return JsonResponse(data)


@api_view(["GET"])
def payment_history(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)
    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)
    try:
        payment_list = {}
        user_id = int(token["user_id"])
        payment_list = (
            Payments.objects.filter(order_id__parent_id=user_id)
            .values(
                "id",
                "transaction_id",
                "transaction_amt",
                "promocode_id__code",
                "promocode_id__discount_percentage",
                "transaction_date",
                "order_id__selected_date",
                "order_id",
            )
            .order_by("-id")
        )
        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(payment_list, 10)
            payment_list = paginator.page(page)
            if not payment_list:
                data = {
                    "status": 400,
                    "data": {
                        "payment_list": list(payment_list),
                        "message": "No Payments found",
                    },
                }
                return JsonResponse(data)
        except PageNotAnInteger:
            payment_list = {}
            data = {
                "status": 400,
                "data": {
                    "payment_list": list(payment_list),
                    "message": "Invalid page number",
                },
            }
            return JsonResponse(data)
        except EmptyPage:
            payment_list = {}
            data = {
                "status": 400,
                "data": {"payment_list": list(payment_list), "message": "Empty Page"},
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                "status": 400,
                "data": {
                    "payment_list": list(payment_list),
                    "message": "Something went wrong!",
                    "trace": str(e),
                },
            }
            return JsonResponse(data)

        payment_list = list(payment_list)
        for payment in payment_list:
            if payment["promocode_id__discount_percentage"] == None:
                payment["promocode_id__discount_percentage"] = 0
            payment["order_items"] = []
            order_id = payment["order_id"]
            order_items = Order_Items.objects.filter(order_id=order_id).values(
                "child_name",
                "child_grade",
                "course_duration",
                "course_id__course_name",
                "course_id__level__level",
            )
            for x in order_items:
                payment["order_items"].append(x)
        data = {
            "status": 200,
            "data": {"payment_list": payment_list, "message": "success"},
        }
        return JsonResponse(data)
    except Exception as E:
        print(E)
        data = {
            "status": 400,
            "data": {
                "payment_list": list(payment_list),
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)
