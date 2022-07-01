from __future__ import unicode_literals
from optparse import Values
from pickle import GET
from django.contrib import auth
from django.template.loader import render_to_string
from django.http import JsonResponse
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

from sympy import true
from secret.serializers.users import add_user_serializer
from secret.serializers.courses import  add_course_serializer, course_fk_check,edit_course_serializer
from secret.serializers.schedules import add_class_schedule_serializer
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from secret.models  import Courses, CourseLevels, TimePeriods, Course_Classes, Class_Students, Order_Items, Class_Schedules
from django.db.models import Count, Sum
from datetime import date
import datetime


@login_required
def list_classes(request):
    x=""
    print("-------8888888-----")
    # print(search_date)
    products = ""
    # print(products)
    print("hellooo")
    sort_parameter = request.GET.get('result')
    print(sort_parameter)

    if sort_parameter == 'desc':
        products = Course_Classes.objects.all().order_by('id')[::-1]
        html = render_to_string(
            template_name="classes/sort.html", context = {'products': products}
        )
        return JsonResponse({'html':html})
        print(products)
    elif sort_parameter =="asc":
        products=Course_Classes.objects.all().order_by('id')
        html = render_to_string(
            template_name="classes/sort.html", context = {'products': products}
        )
        return JsonResponse({'html':html})

    result=bool(request.GET.get('home'))
    print(type(result))
    result_one=request.GET.get('get_id')
    print(result_one,type(result_one))
    print(request.GET.values)
    print(result)
    
    search_date=request.GET.get('result')
    if search_date:
        x=Course_Classes.objects.filter(class_date=search_date)
        html = render_to_string(
            template_name="classes/date_filter.html", context = {'x': x}
        )
        return JsonResponse({'html':html})

    if result_one:
        obj=Course_Classes.objects.get(id=int(result_one))
        
        obj.status=result
        obj.save()
        

               


  
       
        # output=Course_Classes.objects.get(id=result_one).update(status=result)
        # print(output,"-------======-------")
    
    obj=""
    msg=''
    err_msg=''
    try:
        data=request.POST['search']
        data=data.strip()
        if len(data)==0:
            data=""
        else:
            print("Found data POST")
            print(data)
    except Exception as E:
        print(E)
        print("------------")
        try:
            data=request.GET.get('search_string')
            if data:
                data=data.strip()
                if len(data)==0:
                    data=""
                    print("Found but  GET None")
                else:
                    print("Found data GET")
                    print(data)
            else:
                print("GET NO NO DATA")
                data=""
        except Exception as E:
            print(E)
            print("===========")
    if data:
        c = data.split()  # splitting search paramenter for improving search power
        if not 1 in c:
            c.append(c[0])

    if request.method=="GET" :
        if data:
            print("*************GET DATA***********")
            classes= Course_Classes.objects.filter(Q(course_id__course_name__istartswith=c[0]) |  Q(course_id__course_name__icontains=c[0])).values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id','end_time','teacher_id__first_name','teacher_id__last_name','id','class_grade','section').annotate(reserved_seats=Sum("class_students__number_of_seats")).order_by('class_date')
            for m in classes:
                print("here",m)
        else:
            print("*************GET NO DATA***********")
            classes= Course_Classes.objects.filter().values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id','end_time','teacher_id__first_name','teacher_id__last_name','id','class_grade','section','status').annotate(reserved_seats=Sum("class_students__number_of_seats")).order_by('class_date')
            
    else:
        if data:
            print("*************POST  DATA***********")
            classes= Course_Classes.objects.filter(Q(course_id__course_name__istartswith=c[0]) |  Q(course_id__course_name__icontains=c[0]) ).values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id','end_time','teacher_id__first_name','teacher_id__last_name','id','class_grade','section').annotate(reserved_seats=Sum("class_students__number_of_seats")).order_by('class_date')
        else:
            print("*************POST No DATA***********")
            classes= Course_Classes.objects.filter().values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id','end_time','teacher_id__first_name','teacher_id__last_name','id','class_grade','section').annotate(reserved_seats=Sum("class_students__number_of_seats")).order_by('class_date')

    try:
        page       = request.GET.get('page', 1)
        paginator  = Paginator(classes, 10)
        classes = paginator.page(page)
        if not classes:
            classes = {}
            err_msg="No classes found"
    except PageNotAnInteger:
        classes = {}
        err_msg="Invalid Page Number"
    except EmptyPage:
        classes = {}
        err_msg="Empty Page"
    except Exception as e :
        print(e)
        err_msg="Something went wrong"

    return render(request,'classes/list_classes.html',{'msg':msg,'err_msg':err_msg,"classes":classes,"data":data,"obj":obj,"products":products})


@login_required
def class_details(request,id):
    msg,err_msg="",""
    try:
        course_class = Course_Classes.objects.filter(id=id).values('course_id__course_name','class_date',"start_time",'day_of_week__day','teacher_id','end_time','teacher_id__first_name','teacher_id__last_name','id','class_grade',"course_id__level_id__level")
        class_students_objects = Class_Students.objects.filter(course_class_id=id).values('order_id')
        children = Order_Items.objects.none().values('course_duration',"child_name","child_grade","child_age","child_interests")
        for x in class_students_objects:
            new_chil_obj=  Order_Items.objects.filter(order_id=x['order_id']).values('course_duration',"child_name","child_grade","child_age","child_interests")
            children = children | new_chil_obj
        return render(request,'classes/class_details.html',{'msg':msg,'err_msg':err_msg,"course_class":course_class,"children":children})
    except Exception as E:
        print(E)
        err_msg="Something went wrong"
    return render(request,'classes/class_details.html',{'msg':msg,'err_msg':err_msg})

@login_required
def class_edit(request, id):
    msg,err_msg="",""
    try:
        if request.method=="GET":
            print("get")
            print(id,"id")
            all_courses=Course_Classes.objects.filter(is_active=1).filter(id=id).values('id','course_id__course_name')
            print(all_courses, "allcources")
            if not all_courses:
                err_msg="Course is not active!"
            all_schedules= Class_Schedules.objects.filter(class_id__id=id).values('id','day_of_week__day',"start_time","end_time").order_by("day_of_week")
            print(all_schedules, "all_schedules")
            return render(request,'classes/edit_classes.html',{'msg':msg,'err_msg':err_msg,'all_courses':all_courses,"all_schedules":all_schedules})
    except Exception as E:
        print(E)
        err_msg="Something went wrong"
        return render(request,'classes/edit_classes.html',{'msg':msg,'err_msg':err_msg})

@api_view(['POST'])
def add_class_schedule(request):
    if request.method=="POST":
        print(request.POST.values, "values")
        try:
            print("try")
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
            print("done am pm")
            form =add_class_schedule_serializer(data=data)     
            print("form")
            if form.is_valid():
                print("valid")
                already_exist = Class_Schedules.objects.filter(class_id=request.POST['class_id'],day_of_week=request.POST['day_of_week'],start_time=request.POST['start_time'],end_time=request.POST['end_time'])
                if already_exist:
                    duplicay_msg="Schedule already exists"
                    return Response({'status': 500, 'message': duplicay_msg})
                else:
                    print("else,jdsdks")
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
                    print(new_start_time, "st")
                    print(new_end_time, "et")
                    print(c.id, "cid")
                    Class_Schedules.objects.filter(id=c.id).update(start_time=new_start_time,end_time=new_end_time)
                    return Response({'status': 200, 'message': 'Schedule added successfully'})
            else:
                print("else par")
                for key, value in form.errors.items() :
                    error_msg[key] = value[0]
                return Response({'status': 500, 'message': 'error',"error_msg":error_msg})
            
        except Exception as E:
           print(E, "e")
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