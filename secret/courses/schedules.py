from __future__ import unicode_literals
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.models import User
import sys, os, json, io,  base64, hashlib,re
from secret.serializers.users import add_user_serializer
from secret.serializers.courses import  add_course_serializer, course_fk_check,edit_course_serializer
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from secret.models  import Courses, CourseLevels, TimePeriods, Course_Schedules, Class_Schedules

from secret.serializers.schedules import add_course_schedule_serializer
import time

@login_required
def add_schedule(request):
    msg=""
    err_msg=""
    error_msg={}
    all_courses=Courses.objects.filter(is_active=1).values('id','course_name')
    return render(request,'schedules/add_schedule.html',{'error_msg':error_msg,'msg':msg, 'err_msg':err_msg,'all_courses':all_courses})

@api_view(['POST'])
def add_schedule_ajax(request):
    if request.method=="POST":
        try:
            error_msg=[]
            duplicay_msg=""
         
            data = request.POST 
            data._mutable = True
            if 'PM' in  request.POST['start_time']:
                data['start_time']=convert24(request.POST['start_time'])
            if 'PM' in  request.POST['end_time']:
                data['end_time']= convert24(request.POST['end_time'])

            if 'AM' in request.POST['start_time']:
                print("Am")
                data['start_time']=convert24AM(request.POST['start_time'])
            if 'AM' in request.POST['end_time']:
                data['end_time']=convert24AM(request.POST['end_time'])
           
            form =add_course_schedule_serializer(data=data)     

            if form.is_valid():
                already_exist = Course_Schedules.objects.filter(course_id=request.POST['course_id'],day_of_week_id=request.POST['day_of_week'],start_time=request.POST['start_time'],end_time=request.POST['end_time'])
                if already_exist:
                    duplicay_msg="Schedule already exists"
                    return Response({'status': 500, 'message': duplicay_msg})
                else:
                    new_start_time=request.POST['start_time']
                    new_end_time=request.POST['end_time']
                    if 'PM' in  request.POST['start_time']:
                        new_start_time=convert24(request.POST['start_time'])
                    if 'PM' in  request.POST['end_time']:
                        new_end_time= convert24(request.POST['end_time'])

                    if 'AM' in request.POST['start_time']:
                        print("Am")
                        new_start_time=convert24AM(request.POST['start_time'])
                    if 'AM' in request.POST['end_time']:
                        new_end_time=convert24AM(request.POST['end_time']) 

                    c=form.save()
                    print(new_start_time)
                    print(new_end_time)
                    Course_Schedules.objects.filter(id=c.id).update(start_time=new_start_time,end_time=new_end_time)
                    return Response({'status': 200, 'message': 'Schedule added successfully'})
            else:
                
                for key, value in form.errors.items() :
                    error_msg[key] = value[0]
                return Response({'status': 500, 'message': 'success',"error_msg":error_msg})
            
        except Exception as E:
           
            return Response({'status': 500, 'message': 'Something went wrong'})

# convert to 24 hr format
def convert24(str1):
    if str1[-2:] == "PM" and str1[:2] == "12": 
        return str1.replace('PM',":00").replace(" ", "")
    else:
        if(str1[1]==":"):
            a = str(int(str1[:1]) + 12) + str1[1:8] 
            return a.replace('PM',":00").replace(" ", "")
        else:
            b = str(int(str1[:2]) + 12) + str1[2:8] 
            return b.replace('PM',":00").replace(" ", "")
    

# convert to 24 hr format
def convert24AM(str1):
    if str1[-2:] == "AM": 
        return str1.replace('AM',":00").replace(" ", "")
    else:
        if(str1[1]==":"):
            a = str(int(str1[:1]) + 12) + str1[1:8] 
            return a.replace('AM',":00").replace(" ", "")
        else:
            b = str(int(str1[:2]) + 12) + str1[2:8] 
            return b.replace('AM',":00").replace(" ", "")
    

@login_required
def edit_schedule(request,id):
    msg=''
    err_msg=''
    try:
        if request.method=="GET":
            all_courses=Courses.objects.filter(is_active=1).filter(id=id).values('id','course_name')
            if not all_courses:
                err_msg="Course is not active!"
            all_schedules= Course_Schedules.objects.filter(course_id_id=id).values('id','day_of_week__day',"start_time","end_time").order_by("day_of_week")
            return render(request,'schedules/edit_schedules.html',{'msg':msg,'err_msg':err_msg,'all_courses':all_courses,"all_schedules":all_schedules})
    except Exception as E:
        print(E)
        err_msg="Something went wrong"
        return render(request,'schedules/edit_schedules.html',{'msg':msg,'err_msg':err_msg})


# @api_view(['POST'])
# def delete_schedule(request):
#     msg=''
#     try:
#         if request.method=="POST":
#             try:
#                 id=int(request.POST['id'])
#                 Course_Schedules.objects.get(id=id).delete()
#                 return Response({'status': 200, 'message': 'Schedule deleted Successfully'})
#             except Exception as E:
#                 print(E)
#                 err_msg="Something went wrong"
#                 return Response({'status': 500, 'message': E})
#         else:
#             return Response({'status': 500, 'message': 'Bad Request'})
#     except Exception as E:
#         print(E)
#         return Response({'status': 500, 'message': 'Something went wrong'})



 
def record_delete(request, id):
    member =  Class_Schedules.objects.get(id=id)
    member.delete()
    return redirect('/')

