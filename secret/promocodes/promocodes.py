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
from secret.models  import Courses, CourseLevels, TimePeriods, Course_Classes, Class_Students, Order_Items ,Promocodes
from django.db.models import Count, Sum

from secret.serializers.promocodes import add_promocodes_serializer,edit_half_promocodes_serializer, edit_full_promocodes_serializer
import datetime

@login_required
def add_promocode(request):
    msg=''
    err_msg=''
    error_msg={}
    all_courses = Courses.objects.filter(is_active=1).values('id','course_name','level','level__level').order_by("level")
    # updating inactive objects 
    Promocodes.objects.filter(end_date__lt=datetime.datetime.now()).update(is_active=0)
    if request.method =="POST":
        try:
            course_id           = request.POST['course_id'].strip()
            course_duration     = request.POST['course_duration'].strip()
            code                = request.POST['code'].strip()
            discount_percentage =   request.POST['discount_percentage'].strip()
            start_date          = request.POST['start_date'].strip()
            end_date            = request.POST['end_date'].strip()
            form = add_promocodes_serializer(data=request.POST)
            course_id=int(course_id)
            if form.is_valid():
                course_id=int(course_id)
                try:
                    print("valid")
                    if Promocodes.objects.filter(code=code):
                        err_msg= "Promocode must be unique"
                        return render(request, 'promocodes/add_promocode.html',locals())
                    if Promocodes.objects.filter(is_active=1).filter(course_id=course_id,course_duration=course_duration,discount_percentage=discount_percentage):
                        err_msg= "A Promocode already exist for this course with same discount percentage "
                        return render(request, 'promocodes/add_promocode.html',locals())
                    formatted_start_date= datetime.datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
                    formatted_end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d") 
                    print(type(end_date))
                    print(type(formatted_end_date))

                    comparison_start_date =datetime.datetime.strptime(formatted_start_date, "%Y-%m-%d")
                    comparison_end_date = datetime.datetime.strptime(formatted_end_date, "%Y-%m-%d")

                    todays_date=datetime.datetime.today()
                    today_date_string = todays_date.strftime("%Y-%m-%d")
                    today_date = datetime.datetime.strptime(today_date_string, "%Y-%m-%d")


                    if comparison_start_date < today_date  or comparison_end_date <  today_date:
                        print("end date is in past")
                        err_msg= "Start and End dates must be of future!"
                        return render(request, 'promocodes/add_promocode.html',locals())
                    
                    if comparison_start_date > comparison_end_date:
                        err_msg= "Start date should be less than end date !"
                        return render(request, 'promocodes/add_promocode.html',locals())


                    print("Saving")
                    Promocodes.objects.create(code=code,course_id_id=course_id,course_duration=course_duration,discount_percentage=discount_percentage,start_date=formatted_start_date,end_date=formatted_end_date,used_count=0)
                    return redirect('/secret/add_promocode/?msg='+'Promocode added successfully')
                except Exception as E:
                    print(E)
                    err_msg= "Something went wrong"
                    return render(request, 'promocodes/add_promocode.html',locals())
            else:
                print("================errrrrrrrrooooooorrrrrrrrrrrrrrrrr================")
                print(form.errors)
                for key, value in form.errors.items() :
                    error_msg[key] = value[0]
                return render(request, 'promocodes/add_promocode.html',locals()) 
        except Exception as E:
            print(E)
            err_msg= "Something went wrong"
            return render(request,'promocodes/add_promocode.html',{'msg':msg,'err_msg':err_msg,"all_courses":all_courses}) 
    else:
        return render(request,'promocodes/add_promocode.html',{'msg':msg,'err_msg':err_msg,"all_courses":all_courses}) 



def edit_promocode(request,id):
    msg=''
    err_msg=''
    error_msg={}
    all_courses = Courses.objects.filter(is_active=1).values('id','course_name','level','level__level').order_by("level")
    # updating inactive objects 
    Promocodes.objects.filter(end_date__lt=datetime.datetime.now()).update(is_active=0)   
    try:
        success=1
        promocode_object = Promocodes.objects.filter(id=id).values('id','code','discount_percentage','start_date','end_date','course_id','course_id__course_name','course_id__level__level','course_duration','used_count','is_active')[0]
        print(promocode_object)
        promocode_object['start_date']= promocode_object['start_date'].strftime("%m/%d/%Y")
        promocode_object['end_date']= promocode_object['end_date'].strftime("%m/%d/%Y")
        if request.method=="POST":
            print("POST")
            if promocode_object['used_count'] == 0:
                try:
                    course_id           = request.POST['course_id'].strip()
                    course_duration     = request.POST['course_duration'].strip()
                    code                = request.POST['code'].strip()
                    discount_percentage =   request.POST['discount_percentage'].strip()
                    start_date          = request.POST['start_date'].strip()
                    end_date            = request.POST['end_date'].strip()
                    form = edit_full_promocodes_serializer(data= request.POST)
                    is_active          =        request.POST['is_active']
                    is_active =int(is_active)
                    course_id=int(course_id)
                    if  form.is_valid():
                        success=0
                        print("valid Form full editing")
                        if Promocodes.objects.filter(code=code).exclude(id=id):
                            err_msg= "Promocode must be unique"
                            return render(request, 'promocodes/edit_promocode.html',locals())
                        if Promocodes.objects.filter(is_active=1).filter(course_id=course_id,course_duration=course_duration,discount_percentage=discount_percentage).exclude(id=id):
                            err_msg= "A Promocode already exist for this course with same discount percentage "  
                            return render(request, 'promocodes/edit_promocode.html',locals())
                        # print(request.POST['is_active'])
                        formatted_start_date= datetime.datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
                        formatted_end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")

                        comparison_start_date =datetime.datetime.strptime(formatted_start_date, "%Y-%m-%d")
                        comparison_end_date = datetime.datetime.strptime(formatted_end_date, "%Y-%m-%d")

                        todays_date=datetime.datetime.today()
                        today_date_string = todays_date.strftime("%Y-%m-%d")
                        today_date = datetime.datetime.strptime(today_date_string, "%Y-%m-%d")


                        if  comparison_end_date <  today_date:
                            print("end date is in past")
                            err_msg= " End date must be of future!"
                            return render(request, 'promocodes/edit_promocode.html',locals())

                        if comparison_start_date > comparison_end_date:
                            err_msg= "Start date should be less than end date !"
                            return render(request, 'promocodes/edit_promocode.html',locals())

                        Promocodes.objects.filter(id=id).update(code=code,course_id_id=course_id,course_duration=course_duration,discount_percentage=discount_percentage,start_date=formatted_start_date,end_date=formatted_end_date,is_active=request.POST['is_active'])  
                        return redirect('/secret/list_promocodes/?msg='+'Promocode edited successfully')
                    else:
                        success=0
                        print("Invalid Form")
                        err_msg="Something went wrong"
                        print(form.errors)
                        for key, value in form.errors.items() :
                            error_msg[key] = value[0]
                        return render(request, 'promocodes/edit_promocode.html',locals()) 
                except Exception as E:
                    print(E)
                    err_msg="Something went wrong"
                    return render(request, 'promocodes/edit_promocode.html',locals()) 
            else:
                try:
                    form = edit_half_promocodes_serializer(data= request.POST)
                    start_date          = request.POST['start_date'].strip()
                    end_date            = request.POST['end_date'].strip()
                    is_active          =        request.POST['is_active']
                    is_active =int(is_active)
                    print(is_active)
                    if  form.is_valid():
                        success=0
                        print("valid Form half editing")
                        start_date          = request.POST['start_date'].strip()
                        end_date            = request.POST['end_date'].strip()
                        is_active          =        request.POST['is_active']
                        formatted_start_date= datetime.datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
                        formatted_end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")

                        comparison_start_date =datetime.datetime.strptime(formatted_start_date, "%Y-%m-%d")
                        comparison_end_date = datetime.datetime.strptime(formatted_end_date, "%Y-%m-%d")

                        todays_date=datetime.datetime.today()
                        today_date_string = todays_date.strftime("%Y-%m-%d")
                        today_date = datetime.datetime.strptime(today_date_string, "%Y-%m-%d")


                        if  comparison_end_date <  today_date:
                            print("end date is in past")
                            err_msg= " End date must be of future!"
                            return render(request, 'promocodes/edit_promocode.html',locals())

                        if comparison_start_date > comparison_end_date:
                            err_msg= "Start date should be less than end date !"
                            return render(request, 'promocodes/edit_promocode.html',locals())


                        # print(request.POST['is_active'])
                        Promocodes.objects.filter(id=id).update(start_date=formatted_start_date,end_date=formatted_end_date,is_active=request.POST['is_active'])
                        return redirect('/secret/list_promocodes/?msg='+'Promocode edited successfully')
                    else:
                        success=0
                        print("Invalid Form")
                        err_msg="Something went wrong"
                        print(form.errors)
                        for key, value in form.errors.items() :
                            error_msg[key] = value[0]
                        return render(request, 'promocodes/edit_promocode.html',locals())
                except Exception as E:
                    print(E)
                    err_msg="Something went wrong"
                    return render(request, 'promocodes/edit_promocode.html',locals()) 
        else:
            print("GET")
            return render(request, 'promocodes/edit_promocode.html',locals()) 
    except Exception as E:
        print(E)
        err_msg="Something went wrong"
        return render(request, 'promocodes/edit_promocode.html',locals()) 












@login_required
def  list_promocodes(request):
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
        # updating inactive objects 
        Promocodes.objects.filter(end_date__lt=datetime.datetime.now()).update(is_active=0)
        if data:
            print("*************GET DATA***********")
            promocodes= Promocodes.objects.filter(Q(code__istartswith=c[0]) |  Q(code__icontains=c[0])).values('id','course_id__course_name','course_duration',"start_date",'end_date','discount_percentage','code','is_active','used_count','course_id__level__level').order_by('-is_active','-id')
        else:
            print("*************GET NO DATA***********")
            promocodes= Promocodes.objects.filter().values('id','course_id__course_name','course_duration',"start_date",'end_date','discount_percentage','code','is_active','used_count','course_id__level__level').order_by('-is_active','-id')
    else:
        if data:
            print("*************POST  DATA***********")
            promocodes= Promocodes.objects.filter(Q(code__istartswith=c[0]) |  Q(code__icontains=c[0]) ).values('id','course_id__course_name','course_duration',"start_date",'end_date','discount_percentage','code','is_active','used_count','course_id__level__level').order_by('-is_active','-id')
        else:
            print("*************POST No DATA***********")
            promocodes= Promocodes.objects.filter().values('id','course_id__course_name','course_duration',"start_date",'end_date','discount_percentage','code','is_active','used_count','course_id__level__level').order_by('-is_active','-id')
    try:
        page       = request.GET.get('page', 1)
        paginator  = Paginator(promocodes, 10)
        promocodes = paginator.page(page)
        if not promocodes:
            promocodes = {}
            err_msg="No promocodes found"
    except PageNotAnInteger:
        promocodes = {}
        err_msg="Invalid Page Number"
    except EmptyPage:
        promocodes = {}
        err_msg="Empty Page"
    except Exception as e :
        print(e)
        err_msg="Something went wrong"
    return render(request,'promocodes/list_promocodes.html',{'msg':msg,'err_msg':err_msg,"promocodes":promocodes,"data":data})









@api_view(['DELETE'])
@login_required
def delete_promocode(request):
    if request.method == "DELETE":
        id = request.GET.get('id')
        new_status=request.GET.get('toggle_status')
        new_status=int(new_status)
        obj= Promocodes.objects.get(id=id)
        try:
            if new_status == 1 or new_status == "1":
                obj.is_active = 1
            else:
                obj.is_active = 0
            obj.save()
            return Response({'status': 200, 'message': 'success'})
        except Exception as e:
            print(e)
            return Response({'status': 500, 'message': 'Internal server error'})
    else:
        return Response({'status': 500, 'message': 'Bad Request'})
