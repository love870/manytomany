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
from secret.serializers.users import add_user_serializer, edit_user_serializer
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from api.models import Profile,Roles
from rest_framework.authtoken.models import Token
from django.template.loader import render_to_string

@login_required
def add_user(request):
    msg=""
    err_msg=""
    error_msg={}
    if request.method=="GET":
        return render(request,'users/add_users.html',{'msg':msg})
    else:
        try:
            first_name=request.POST['first_name'].strip()
            last_name=request.POST['last_name'].strip()
            email=request.POST['email'].strip().lower()
            phone = request.POST['phone'].strip()
            username=email
            password=request.POST['password'].strip()

            # check existing username
            if User.objects.filter(username=username):
                err_msg="Username already exists!"
                print("username exist")
                return render(request,'users/add_users.html',{'msg':msg,'err_msg':err_msg,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password':password,'phone':phone})
            if User.objects.filter(email=request.POST['email']):
                err_msg="Email already exists!"
                print("mail exist")
                return render(request,'users/add_users.html',{'msg':msg,'err_msg':err_msg,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password':password,'phone':phone})
            if Profile.objects.filter(phone=phone):
                err_msg="Phone no. already exists!"
                return render(request,'users/add_users.html',{'msg':msg,'err_msg':err_msg,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password':password,'phone':phone})

            # serialier validations
            form=add_user_serializer(data=request.POST)
            if form.is_valid():
                print("Valid")
                try:
                    user = User(username=username,email=email,first_name=first_name,last_name=last_name,is_staff=1)
                    user.set_password(password)
                    user.save()

                    # creating profile
                    role_obj=Roles.objects.get(role="Teacher")
                    p = Profile.objects.create(user=user,role=role_obj,phone=phone)

                    msg="User created Successfully"
                    return render(request,'users/add_users.html',{"msg":msg})
                except Exception as E:
                    try:
                        user.delete()
                    except Exception as user_error:
                        print(user_error)
                    try:
                        p.delete()
                    except Exception as profile_error:
                        print(profile_error)
                    print(E)
                    err_msg="Something went wrong"
                    return render(request,'users/add_users.html',{'error_msg':error_msg,'msg':msg, 'err_msg':err_msg ,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password':password,'phone':phone})
            else:
                for key, value in form.errors.items() :
                    error_msg[key] = value[0]
                print(error_msg)

        except Exception as E:
            print(E)
        return render(request,'users/add_users.html',{'error_msg':error_msg,'msg':msg, 'err_msg':err_msg,'first_name':first_name,'last_name':last_name,'username':username,'email':email,'password':password,'phone':phone})

@login_required
def list_users(request):
    name = request.GET.get('suggestion')
    if request.method=="POST":
        print("POST")
        print(request.POST.values)
        print(request.POST.get('firstname'),"request.POST.get('firstname')")
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        password=request.POST.get('password')
        result=User(first_name=firstname,last_name=lastname,email=email)
        
        result.save()
        print(firstname,lastname,phone,email,password)
  

    # print(request.GET.values)
    if name:
        print(name)
        search_filter_data=User.objects.filter(email__icontains=name)
        print("CHECK bro",search_filter_data)
        print("*********")
        html = render_to_string('users/list_user_filter.html',{'search_filter_data':search_filter_data})
        return JsonResponse({'html':html})
    else:
        search_filter_data=User.objects.all()
        print("kkkkkkkk")
#     context={'data':search_filter_data}
# return render("searchfilter.html",context)

    msg=''
    err_msg=''
    try:
        data=request.POST['search']
        print(data)
        data=data.strip()
        if len(data)==0:
            data=''
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
                    data=''
                    print("Found but  GET None")
                else:
                    print("Found data GET")
                    print(data)
            else:
                print("GET NO NO DATA")
                data=''
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
            users= User.objects.filter(Q(first_name__istartswith=c[0]) |  Q(email__istartswith=c[0]) | Q(first_name__istartswith=c[1]) |Q (email__istartswith=c[1])).values('id','first_name','last_name','email' ,'profile__phone',"profile__role_id__role",'is_active')
            pass
        else:
            print("*************GET NO DATA***********")
            users= User.objects.filter().values('id','first_name','last_name','email' ,'profile__phone',"profile__role_id__role","is_active")

    else:
        if data:
            print("*************POST  DATA***********")
            users= User.objects.filter(Q(first_name__istartswith=c[0]) |  Q(email__istartswith=c[0]) | Q(first_name__istartswith=c[1]) |Q (email__istartswith=c[1])).values('id','first_name','last_name','email' ,'profile__phone',"profile__role_id__role","is_active")
        else:
            print("*************POST DATA***********")
            users= User.objects.filter().values('id','first_name','last_name','email' ,'profile__phone',"profile__role_id__role","is_active")



    try:
        page       = request.GET.get('page', 1)
        paginator  = Paginator(users, 10)
        users = paginator.page(page)
        if not users:
            users = {}
            err_msg="No users found"
    except PageNotAnInteger:
        users = {}
        err_msg="Invalid Page Number"
    except EmptyPage:
        users = {}
        err_msg="Empty Page"
    except Exception as e :
        err_msg="Something went wrong"
    return render(request,'users/list_users.html',{'msg':msg,'err_msg':err_msg,  "users":users,"data":data})

# @login_required
# def list_users(request):
#     data={}
#     search=Profile.objects.all()
#     if request.method== "POST":
#         st=request.POST.get('search')
#         if st!=None:
#             search=Profile.objects.filter(email_icontains=st)
#         data={'search':search}
#     return render(request,'users/list_users.html',data)

@login_required
def edit_user(request,id):
    print("arrive")
    msg=""
    err_msg=""
    error_msg={}
    print(request.GET.get("qs"),"Check it out")

    if request.method=="POST":
        try:
            first_name=request.POST['first_name'].strip()
            last_name=request.POST['last_name'].strip()
            password=request.POST['password'].strip()
            # serialier validations
            form=edit_user_serializer(data=request.POST)
            if form.is_valid():
                print("Valid")
                if len(password)>0 and len(password)<6:
                    err_msg="Password length must be atleast 6 characters"
                    return render(request,'users/edit_user.html',{'error_msg':error_msg,'msg':msg, 'err_msg':err_msg,'first_name':first_name,'last_name':last_name})
                User.objects.filter(id=id).update(first_name=first_name,last_name=last_name)
                msg=" User updated Successfully"
                user = User.objects.filter(id=id).values("first_name","last_name")
                if len(password)>0:
                    user = User.objects.get(id=id)

                    user.set_password(password)
                    user.save()

                return render(request,'users/edit_user.html',{'msg':msg,"user":user,'first_name':first_name,'last_name':last_name})
            else:
                err_msg="Invalid Data!"
                for key, value in form.errors.items() :
                    error_msg[key] = value[0]
                print(error_msg)
                return render(request,'users/edit_user.html',{'error_msg':error_msg,'msg':msg, 'err_msg':err_msg,'first_name':first_name,'last_name':last_name})

        except Exception as E:
            print(E)
            err_msg="Something went wrong"
            return render(request,'users/edit_user.html',{'msg':msg})
    else:
        try:
            user = User.objects.filter(id=id).values("first_name","last_name")
            first_name=user[0]['first_name']
            last_name=user[0]['last_name']
        except:
            err_msg="Invalid User"
            return render(request,'users/edit_user.html',{'msg':msg,"err_msg":err_msg})
        return render(request,'users/edit_user.html',{'msg':msg,"user":user,'first_name':first_name,'last_name':last_name})

@api_view(['DELETE'])
@login_required
def delete_user(request):
    if request.method == "DELETE":
        id = request.GET.get('id')
        new_status=request.GET.get('toggle_status')
        new_status=int(new_status)
        obj= User.objects.get(id=id)
        is_deleted=None
        try:
            if new_status == 1 or new_status == "1":
                obj.is_active = 1
            else:
                obj.is_active = 0
                is_deleted=1
            obj.save()
            try:
                if is_deleted==1:
                    Token.objects.filter(user_id=id).delete()
            except Exception as E:
                print(E)
            return Response({'status': 200, 'message': 'success'})
        except Exception as e:
            print(e)
            return Response({'status': 500, 'message': 'Internal server error'})
    else:
        return Response({'status': 500, 'message': 'Bad Request'})

