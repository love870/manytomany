from __future__ import unicode_literals
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.models import User
import sys, os, json, io, base64, hashlib, re
from api.serializers.classes import add_class_link_serializer
from api.models import Profile, Timezones, Roles
from rest_framework.authtoken.models import Token
from secret.models import Courses, Course_Classes, Course_Schedules
from datetime import date, datetime
import pytz, datetime
from pytz import timezone
from dateutil import tz
from tzlocal import get_localzone


def checkAuth(request):
    if Token.objects.filter(key=request.META.get("HTTP_TOKEN")):
        return Token.objects.filter(key=request.META.get("HTTP_TOKEN")).values(
            "user_id"
        )
    else:
        return 0


def checkTimezone(request):
    if Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE")):
        return Timezones.objects.filter(
            tz_name=request.META.get("HTTP_TIMEZONE")
        ).values("tz_name")[0]
    else:
        return 0


@api_view(["GET"])
def all_courses(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:
        courses_list = {}
        courses_list = (
            Courses.objects.filter(is_active=1)
            .values(
                "id",
                "course_name",
                "duration_value",
                "level_id__level",
                "duration_period__duration",
                "course_description",
                "price_per_week",
                "price_per_month",
                "free_duration",
            )
            .order_by("level_id")
        )
        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(courses_list, 10)
            courses_list = paginator.page(page)
            if not courses_list:
                data = {
                    "status": 400,
                    "data": {
                        "courses_list": list(courses_list),
                        "message": "No courses found",
                    },
                }
                return JsonResponse(data)
        except PageNotAnInteger:
            courses_list = {}
            data = {
                "status": 400,
                "data": {
                    "courses_list": list(courses_list),
                    "message": "Invalid page number",
                },
            }
            return JsonResponse(data)
        except EmptyPage:
            courses_list = {}
            data = {
                "status": 400,
                "data": {"courses_list": list(courses_list), "message": "Empty Page"},
            }
            return JsonResponse(data)
        except Exception as e:
            print(e)
            data = {
                "status": 400,
                "data": {
                    "courses_list": list(courses_list),
                    "message": "Something went wrong!",
                    "trace": str(e),
                },
            }
            return JsonResponse(data)

        courses_list = list(courses_list)
        for x in courses_list:
            x["week_days"] = []
            course_id = x["id"]

            x["price_per_week_str"] = "{:.2f}".format(x["price_per_week"])
            x["price_per_month_str"] = "{:.2f}".format(x["price_per_month"])

            schedules = (
                Course_Schedules.objects.filter(course_id=course_id)
                .values("id", "course_id", "day_of_week")
                .order_by("day_of_week")
            )
            for y in schedules:
                day = y["day_of_week"]
                if not day in x["week_days"]:
                    x["week_days"].append(day)
        data = {
            "status": 200,
            "data": {"courses_list": courses_list, "message": "success"},
        }
        return JsonResponse(data)
    except Exception as E:
        print(E)
        data = {
            "status": 400,
            "data": {
                "courses_list": list(courses_list),
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["GET"])
def confirmed_classes(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:
        user_id = token[0]["user_id"]
        today = date.today()
        print(today)
        print(user_id)
        confirmed_classes = (
            Course_Classes.objects.filter(class_date__gte=today)
            .filter(class_students__order_id__parent_id_id=user_id)
            .values(
                "course_id__course_name",
                "class_date",
                "start_time",
                "day_of_week__day",
                "teacher_id",
                "class_link",
                "course_id__course_description",
                "end_time",
                "class_grade",
            )
            .order_by("class_date")
        )
        print("SEE", confirmed_classes)
        # confirmed_classes= Course_Classes.objects.filter(class_date__gte=today).values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id',"class_link","course_id__course_description")
        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(confirmed_classes, 10)
            confirmed_classes = paginator.page(page)
            if not confirmed_classes:
                data = {"status": 400, "data": {"message": "No class found"}}
                return JsonResponse(data)
        except PageNotAnInteger:
            confirmed_classes = {}
            data = {"status": 400, "data": {"message": "Invalid page number"}}
            return JsonResponse(data)
        except EmptyPage:
            confirmed_classes = {}
            data = {"status": 400, "data": {"message": "Empty Page"}}
            return JsonResponse(data)
        except Exception as e:
            print(e)
            data = {
                "status": 400,
                "data": {"message": "Something went wrong!", "trace": str(e)},
            }
            return JsonResponse(data)
        confirmed_classes = list(confirmed_classes)
        if confirmed_classes:
            for x in confirmed_classes:
                # converting time according to timezone
                current_tz = get_localzone()
                provided_tz = pytz.timezone(timezone["tz_name"])
                # making time to datetime
                datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["start_time"]
                )
                end_time_datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["end_time"]
                )

                # converting time from 1 timezone to another
                converted_datetime = current_tz.localize(datetime_obj).astimezone(
                    provided_tz
                )
                converted_end_datetime = current_tz.localize(
                    end_time_datetime_obj
                ).astimezone(provided_tz)

                x["start_time"] = converted_datetime.strftime("%H:%M:%S")
                x["end_time"] = converted_end_datetime.strftime("%H:%M:%S")
                if x["teacher_id"] == None or x["teacher_id"] == "":
                    x["teacher_id"] = 0
        data = {
            "status": 200,
            "data": {"confirmed_classes": confirmed_classes, "message": "success"},
        }
        return JsonResponse(data)

    except Exception as E:
        print(E)
        data = {
            "status": 403,
            "data": {"message": "Something went wrong!", "trace": str(E)},
        }
        return JsonResponse(data)


@api_view(["GET"])
def V2_teacher_available_classes(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:
        available_classes = None
        # user_id=token['user_id']
        today = date.today()

        available_classes = (
            Course_Classes.objects.filter(class_date__gte=today)
            .filter(teacher_id_id__is_active=True)
            .values("section")
            .distinct()
        )

        for one_class in available_classes:
            one_section = one_class["section"]
            first_class = Course_Classes.objects.filter(section=one_section).values(
                "id",
                "course_id__course_name",
                "class_date",
                "start_time",
                "end_time",
                "day_of_week",
                "day_of_week__day",
                "teacher_id",
                "course_id__level__level",
                "class_grade",
                "section",
            )[0]

            class_date = first_class["class_date"]
            monday_date = class_date - datetime.timedelta(days=class_date.weekday())
            first_class["monday_date"] = monday_date
            one_class["one_week"] = first_class
            one_class["class_date"] = first_class["class_date"]

        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(available_classes, 10)
            available_classes = paginator.page(page)
            if not available_classes:
                data = {
                    "status": 400,
                    "data": {
                        "available_classes": list(available_classes),
                        "message": "No class found",
                    },
                }
                return JsonResponse(data)
        except PageNotAnInteger:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Invalid page number",
                },
            }
            return JsonResponse(data)
        except EmptyPage:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Empty Page",
                },
            }
            return JsonResponse(data)
        except Exception as e:
            print(e)
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Something went wrong!",
                    "trace": str(e),
                },
            }

            return JsonResponse(data)

        available_classes = list(available_classes)
        if available_classes:
            for x in available_classes:
                print(x["one_week"]["start_time"], x["one_week"]["end_time"])
                # converting time according to timezone
                current_tz = get_localzone()
                provided_tz = pytz.timezone(timezone["tz_name"])
                # making time to datetime
                start_time_datetime_obj = datetime.datetime.combine(
                    x["one_week"]["class_date"], x["one_week"]["start_time"]
                )
                end_time_datetime_obj = datetime.datetime.combine(
                    x["one_week"]["class_date"], x["one_week"]["end_time"]
                )
                # converting time from 1 timezone to another
                converted_start_datetime = current_tz.localize(
                    start_time_datetime_obj
                ).astimezone(provided_tz)
                converted_end_datetime = current_tz.localize(
                    end_time_datetime_obj
                ).astimezone(provided_tz)

                x["one_week"]["start_time"] = converted_start_datetime.strftime(
                    "%H:%M:%S"
                )
                x["one_week"]["end_time"] = converted_end_datetime.strftime("%H:%M:%S")
                x["class_date"] = x["one_week"]["class_date"]
        data = {
            "status": 200,
            "data": {"available_classes": available_classes, "message": "success"},
        }

        return JsonResponse(data)

    except Exception as E:
        print(E)
        data = {
            "status": 400,
            "data": {
                "available_classes": list(available_classes),
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["POST"])
def V2_teacher_claim_class(request):
    class_info = []
    token = checkAuth(request)
    print("token", token)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:

        user_id = int(token.values()[0]["user_id"])
        reqdata = json.loads(request.body)
        print("here---------", reqdata)
        try:
            section = reqdata["section"].strip()
            if not section:
                print("yes exists")
                data = {
                    "status": 400,
                    "data": {
                        "class_info": class_info,
                        "message": "Section can not be empty!",
                    },
                }
                return JsonResponse(data)
        except Exception as E:
            print(E)
            data = {
                "status": 400,
                "data": {"class_info": class_info, "message": "Section is missing"},
            }
            return JsonResponse(data)
        if Course_Classes.objects.filter(section=section):
            Course_Classes.objects.filter(section=section).update(teacher_id_id=user_id)

            class_info = Course_Classes.objects.filter(section=section).values(
                "id",
                "course_id__course_name",
                "class_date",
                "start_time",
                "end_time",
                "day_of_week__day",
                "teacher_id__first_name",
                "teacher_id__last_name",
                "class_grade",
                "section",
            )
            class_info = list(class_info)
            if class_info:
                for one_class in class_info:
                    print(one_class["start_time"], one_class["end_time"])
                    # converting time according to timezone
                    current_tz = get_localzone()
                    provided_tz = pytz.timezone(timezone["tz_name"])
                    # making time to datetime
                    start_time_datetime_obj = datetime.datetime.combine(
                        one_class["class_date"], one_class["start_time"]
                    )
                    end_time_datetime_obj = datetime.datetime.combine(
                        one_class["class_date"], one_class["end_time"]
                    )
                    # converting time from 1 timezone to another
                    converted_start_datetime = current_tz.localize(
                        start_time_datetime_obj
                    ).astimezone(provided_tz)
                    converted_end_datetime = current_tz.localize(
                        end_time_datetime_obj
                    ).astimezone(provided_tz)

                    one_class["start_time"] = converted_start_datetime.strftime(
                        "%H:%M:%S"
                    )
                    one_class["end_time"] = converted_end_datetime.strftime("%H:%M:%S")
            print("sending data")
            data = {
                "status": 200,
                "data": {
                    "class_info": class_info,
                    "message": "Successfully claimed the week",
                },
            }
            return JsonResponse(data)
        else:
            data = {
                "status": 400,
                "data": {"class_info": class_info, "message": "No classes Found"},
            }
            return JsonResponse(data)
    except Exception as E:
        print("========================================")
        print(E)
        data = {
            "status": 400,
            "data": {
                "class_info": class_info,
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["GET"])
def teacher_available_classes(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:
        available_classes = None
        # user_id=token['user_id']
        today = date.today()

        available_classes = (
            Course_Classes.objects.filter(class_date__gte=today)
            .filter(teacher_id_id__isnull=True)
            .values(
                "id",
                "course_id__course_name",
                "class_date",
                "start_time",
                "end_time",
                "day_of_week__day",
                "teacher_id",
                "course_id__level__level",
                "class_grade",
            )
            .order_by("class_date")
        )
        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(available_classes, 10)
            available_classes = paginator.page(page)
            if not available_classes:
                data = {
                    "status": 400,
                    "data": {
                        "available_classes": list(available_classes),
                        "message": "No class found",
                    },
                }
                return JsonResponse(data)
        except PageNotAnInteger:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Invalid page number",
                },
            }
            return JsonResponse(data)
        except EmptyPage:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Empty Page",
                },
            }
            return JsonResponse(data)
        except Exception as e:
            print(e)
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Something went wrong!",
                    "trace": str(e),
                },
            }
            return JsonResponse(data)

        available_classes = list(available_classes)
        if available_classes:
            for x in available_classes:
                print(x["start_time"], x["end_time"])
                # converting time according to timezone
                current_tz = get_localzone()
                provided_tz = pytz.timezone(timezone["tz_name"])
                # making time to datetime
                start_time_datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["start_time"]
                )
                end_time_datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["end_time"]
                )
                # converting time from 1 timezone to another
                converted_start_datetime = current_tz.localize(
                    start_time_datetime_obj
                ).astimezone(provided_tz)
                converted_end_datetime = current_tz.localize(
                    end_time_datetime_obj
                ).astimezone(provided_tz)

                x["start_time"] = converted_start_datetime.strftime("%H:%M:%S")
                x["end_time"] = converted_end_datetime.strftime("%H:%M:%S")
        data = {
            "status": 200,
            "data": {"available_classes": available_classes, "message": "success"},
        }
        return JsonResponse(data)

    except Exception as E:
        print(E)
        data = {
            "status": 400,
            "data": {
                "available_classes": list(available_classes),
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["POST"])
def teacher_claim_class(request):
    class_info = []
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:

        user_id = token
        reqdata = json.loads(request.body.decode("utf-8"))
        try:
            class_id = reqdata["class_id"]
        except Exception as E:
            data = {
                "status": 400,
                "data": {"class_info": class_info, "message": "Class id is missing"},
            }
            return JsonResponse(data)
        if Course_Classes.objects.filter(id=class_id):
            Course_Classes.objects.filter(id=class_id).update(teacher_id_id=user_id)

            class_info = Course_Classes.objects.filter(id=class_id).values(
                "id",
                "course_id__course_name",
                "class_date",
                "start_time",
                "end_time",
                "day_of_week__day",
                "teacher_id__first_name",
                "teacher_id__last_name",
                "class_grade",
            )[0]
            if class_info:
                print(class_info["start_time"], class_info["end_time"])
                # converting time according to timezone
                current_tz = get_localzone()
                provided_tz = pytz.timezone(timezone["tz_name"])
                # making time to datetime
                start_time_datetime_obj = datetime.datetime.combine(
                    class_info["class_date"], class_info["start_time"]
                )
                end_time_datetime_obj = datetime.datetime.combine(
                    class_info["class_date"], class_info["end_time"]
                )
                # converting time from 1 timezone to another
                converted_start_datetime = current_tz.localize(
                    start_time_datetime_obj
                ).astimezone(provided_tz)
                converted_end_datetime = current_tz.localize(
                    end_time_datetime_obj
                ).astimezone(provided_tz)

                class_info["start_time"] = converted_start_datetime.strftime("%H:%M:%S")
                class_info["end_time"] = converted_end_datetime.strftime("%H:%M:%S")

            data = {
                "status": 200,
                "data": {
                    "class_info": class_info,
                    "message": "Successfully claimed the class",
                },
            }
            return JsonResponse(data)
        else:
            data = {
                "status": 400,
                "data": {"class_info": class_info, "message": "No class Found"},
            }
            return JsonResponse(data)
    except Exception as E:
        print("Last Exception")
        print(E)
        data = {
            "status": 400,
            "data": {
                "class_info": class_info,
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["GET"])
def teacher_claimed_classes(request):
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)
    try:
        available_classes = None
        user_id = token
        today = date.today()
        ob = Course_Classes.objects.all()
        available_classes = (
            Course_Classes.objects.filter(class_date__gte=today)
            .filter(teacher_id_id=token[0]["user_id"])
            .values(
                "id",
                "course_id__course_name",
                "class_date",
                "start_time",
                "end_time",
                "day_of_week__day",
                "teacher_id",
                "course_id__level__level",
                "class_link",
                "class_grade",
            )
            .order_by("class_date")
        )
        print(available_classes)
        try:
            page = request.GET.get("page", 1)
            paginator = Paginator(available_classes, 10)
            available_classes = paginator.page(page)
            if not available_classes:
                data = {
                    "status": 400,
                    "data": {
                        "available_classes": list(available_classes),
                        "message": "No class found",
                    },
                }
                return JsonResponse(data)
        except PageNotAnInteger:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Invalid page number",
                },
            }
            return JsonResponse(data)
        except EmptyPage:
            available_classes = {}
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Empty Page",
                },
            }
            return JsonResponse(data)
        except Exception as e:
            print(e)
            data = {
                "status": 400,
                "data": {
                    "available_classes": list(available_classes),
                    "message": "Something went wrong!",
                    "trace": str(e),
                },
            }
            return JsonResponse(data)

        available_classes = list(available_classes)
        if available_classes:
            for x in available_classes:
                print(x["start_time"], x["end_time"])
                # converting time according to timezone
                current_tz = get_localzone()
                provided_tz = pytz.timezone(timezone["tz_name"])
                # making time to datetime
                start_time_datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["start_time"]
                )
                end_time_datetime_obj = datetime.datetime.combine(
                    x["class_date"], x["end_time"]
                )
                # converting time from 1 timezone to another
                converted_start_datetime = current_tz.localize(
                    start_time_datetime_obj
                ).astimezone(provided_tz)
                converted_end_datetime = current_tz.localize(
                    end_time_datetime_obj
                ).astimezone(provided_tz)

                x["start_time"] = converted_start_datetime.strftime("%H:%M:%S")
                x["end_time"] = converted_end_datetime.strftime("%H:%M:%S")

        data = {
            "status": 200,
            "data": {"available_classes": available_classes, "message": "success"},
        }
        return JsonResponse(data)

    except Exception as E:
        print(E)
        data = {
            "status": 400,
            "data": {
                "available_classes": list(available_classes),
                "message": "Something went wrong!",
                "trace": str(E),
            },
        }
        return JsonResponse(data)


@api_view(["POST"])
def teacher_add_zoom_link(request):
    class_info = []
    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    try:

        user_id = token[0]["user_id"]

        reqdata = json.loads(request.body.decode("utf-8"))
        try:
            form = add_class_link_serializer(data=reqdata)
            if form.is_valid():
                print("valid")
                if Course_Classes.objects.filter(id=reqdata["class_id"]):
                    Course_Classes.objects.filter(id=reqdata["class_id"]).update(
                        class_link=reqdata["class_link"]
                    )
                    data = {
                        "status": 200,
                        "data": {"message": "Zoom link added successfully"},
                    }
                    return JsonResponse(data)
                else:
                    data = {"status": 404, "data": {"message": "Class not found"}}
                    return JsonResponse(data)
            else:
                data = {"status": 400, "data": {"message": "Invalid or missing params"}}
                return JsonResponse(data)
        except Exception as E:
            print(E)
            data = {
                "status": 500,
                "data": {"message": "Something went wrong!", "trace": str(E)},
            }
            return JsonResponse(data)
    except Exception as E:
        print(E)
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(E)},
        }
        return JsonResponse(data)
