from __future__ import unicode_literals
import sys, os, json, io,  base64, hashlib,re
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from datetime import date

from api.serializers.classes import add_class_link_serializer
from api.serializers.orders import add_order_serializer,add_child_serializer
from api.models import Profile, Timezones,Roles
from secret.models  import Courses, Course_Classes, Course_Schedules,Orders,Order_Items

def checkAuth(request):
    if Token.objects.filter(key=request.META.get('HTTP_TOKEN')):
        return Token.objects.filter(key=request.META.get('HTTP_TOKEN')).values('user_id')[0]
    else:
        return 0

def checkTimezone(request):
    if Timezones.objects.filter(tz_name=request.META.get('HTTP_TIMEZONE')):
        return Timezones.objects.filter(tz_name=request.META.get('HTTP_TIMEZONE'))[0]
    else:
        return 0



@api_view(['POST'])
def add_order(request):
    print('hitting our add order api')
    token = checkAuth(request)
    if token == 0:
        data = {"status":403,"data":{"message":"Not Logged In!"}}
        return JsonResponse(data)
    
    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status":403,"data":{"message":"Please Check Timezone!"}}
        return JsonResponse(data)

    print(json.loads(request.body.decode('utf-8')))

    try:
        user_id=token['user_id']
        reqdata = json.loads(request.body.decode('utf-8'))
        print(user_id,reqdata)
        try:
            saved_order_id=None
            form = add_order_serializer(data=reqdata)
            print("Form without if condition",form)
            if form.is_valid():
                print('first form is valid')
                # creating order
                order = Orders.objects.create(
                    grand_total_amt=form.data['grand_total_amt'],
                    parent_id=User.objects.get(id=user_id),
                    selected_date=form.data['selected_date'],
                    is_active=0
                )
                saved_order_id=order.pk
                # hitting for loop om child info
                for child_info in reqdata['child_information']:
                    print("CHILD INFO",child_info)
                    form2= add_child_serializer(data=child_info)
                    if form2.is_valid():
                        print('second form is valid')
                        # creating order items
                        print(form.data)
                        print(form.data['course_id'])

                        print("saved",Courses.objects.filter(id=form.data['course_id']))

                        print("COUR",Courses.objects.get(id=form.data['course_id']))

                        Order_Items.objects.create(
                            order_id=Orders.objects.get(id=saved_order_id),
                            course_id=Courses.objects.get(id=form.data['course_id']),
                            course_price=form.data['course_price'],
                            course_duration=form.data['course_duration'],
                            child_name=form2.data['child_name'],
                            child_grade=form2.data['child_grade'],
                            child_interests=form2.data['child_interests'],
                            child_age=form2.data['child_age'],
                            is_active=0
                        )
                    else:
                        print(form.errors)
                        Order_Items.objects.filter(order_id=saved_order_id).delete()
                        Orders.objects.filter(id=saved_order_id).delete()
                        data  = {"status":400,"data":{"message":"Invalid or missing child_information params"}}
                        return JsonResponse(data)

                u = {}
                u['order_id']   = saved_order_id
                u['message']    ="Order added successfully"
                data  = {"status":200,"data":u}
                return JsonResponse(data)
            else:
                print(form.errors)
                data  = {"status":400,"data":{"message":"Invalid or missing params"}}
                return JsonResponse(data)
        except Exception as E:
            print('in exception 1')
            print(E) 
            data = {"status":500,"data":{"message":"Something went wrong!","trace":str(E)}}
            return JsonResponse(data)
    except Exception as E:
        print(E) 
        data = {"status":500,"data":{"message":"Something went wrong!","trace":str(E)}}
        return JsonResponse(data)

