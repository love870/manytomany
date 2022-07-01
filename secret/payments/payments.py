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

from secret.models  import Courses, CourseLevels, TimePeriods,Order_Items, Payments



@login_required
def order_items(request,id):
    msg=""
    try:
        order_items      = Order_Items.objects.filter(order_id_id=id,is_active=1).values('id','order_id','course_id','course_id__course_name','course_price','course_duration','child_name','child_grade','child_interests','child_age')  
        if order_items:
            order_items_list = order_items
            page          = request.GET.get('page', 1)
            paginator     = Paginator(order_items_list, 10)
            order_items      = paginator.page(page)
            return render(request, 'payments/order_items.html',{'order_items':order_items,'msg':msg})
        else:
            msg = "No Data Found"
    except Exception as e:
        print('error is',e)
        msg = "No Data Found"
    return render(request, 'payments/order_items.html',{'msg':msg})





def list_payments(request):
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
            payments= Payments.objects.filter(Q(order_id__parent_id__first_name__istartswith=c[0]) |  Q(order_id__parent_id__first_name__icontains=c[1])|Q(order_id__parent_id__last_name__istartswith=c[0]) |  Q(order_id__parent_id__last_name__icontains=c[1])).values('id','order_id','transaction_amt','transaction_mode',"transaction_platform",'transaction_date',"order_id__parent_id__first_name","order_id__parent_id__last_name",'order_id__grand_total_amt','transaction_date','promocode_id__code','promocode_id__discount_percentage').order_by('-id')
        else:
            print("*************GET NO DATA***********")
            payments= Payments.objects.filter().values('id','order_id','transaction_amt','transaction_mode',"transaction_platform",'transaction_date',"order_id__parent_id__first_name","order_id__parent_id__last_name",'order_id__grand_total_amt','transaction_date','promocode_id__code','promocode_id__discount_percentage').order_by('-id')
    else:
        if data:
            print("*************POST  DATA***********")
            payments= Payments.objects.filter(Q(order_id__parent_id__first_name__istartswith=c[0]) |  Q(order_id__parent_id__first_name__icontains=c[1])|Q(order_id__parent_id__last_name__istartswith=c[0]) |  Q(order_id__parent_id__last_name__icontains=c[1])).values('id','order_id','transaction_amt','transaction_mode',"transaction_platform",'transaction_date',"order_id__parent_id__first_name","order_id__parent_id__last_name",'order_id__grand_total_amt','transaction_date','promocode_id__code','promocode_id__discount_percentage').order_by('-id')
        else:
            print("*************POST No DATA***********")
            payments= Payments.objects.filter().values('id','order_id','transaction_amt','transaction_mode',"transaction_platform",'transaction_date',"order_id__parent_id__first_name","order_id__parent_id__last_name",'order_id__grand_total_amt','transaction_date','promocode_id__code','promocode_id__discount_percentage').order_by('-id')
    try:
        page       = request.GET.get('page', 1)
        paginator  = Paginator(payments, 10)
        payments = paginator.page(page)
        if not payments:
            payments = {}
            err_msg="No payments found"
    except PageNotAnInteger:
        payments = {}
        err_msg="Invalid Page Number"
    except EmptyPage:
        payments = {}
        err_msg="Empty Page"
    except Exception as e :
        print(e)
        err_msg="Something went wrong"

    return render(request,'payments/list_payments.html',{'msg':msg,'err_msg':err_msg,"payments":payments,"data":data})

