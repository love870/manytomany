from __future__ import unicode_literals
from email import message
from optparse import Values
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from requests import get
from rest_framework.response import Response
from fpdf import FPDF
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.models import User
import sys, os, json, io, base64, hashlib, re
from django.contrib import messages
from sympy import Add
from secret.serializers.users import add_user_serializer
from secret.serializers.courses import (
    add_course_serializer,
    course_fk_check,
    edit_course_serializer,
)
from django.conf.urls import static
from django.conf import settings

from django.http import HttpResponse
from django.views.generic import View
from reportlab.pdfgen    import canvas
from reportlab.lib.utils import ImageReader
from datetime            import datetime
from reportlab.lib.pagesizes import letter
from datetime import datetime
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from secret.models import AddStudent, Courses, CourseLevels, TimePeriods, Course_Classes, Weekdays, classs
from django.conf import settings
from django.core.mail import send_mail
from api.models import Profile
from django.shortcuts import render
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from fpdf import FPDF
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  


from django.core.files.storage import FileSystemStorage



@login_required
def list_courses(request):
   

    # xc=""
    # get_view_pdf_id=request.GET.get('get_viewpdf_id')
    # print(get_view_pdf_id)
    # buf=io.BytesIO()
    # c=canvas.Canvas(buf,pagesize=letter,bottomup=0)
    # textob=c.beginText()
    # textob.setTextOrigin(inch,inch)
    # textob.setFont("Helvetica",14)
    # lines=[
    #     "this",
    #     "second",
    #     "third"
    # ]
    # for line in lines:
    #     textob.textLine(line)
    
    # c.drawText(textob)
    # c.showPage()
    # c.show()
    # buf.seek(0)

    # return FileResponse(buf,as_attachment=True,filename=file.pdf)
        

    # context_dict={'xc':xc}
    # template = get_template('courses/list_courses.html')
    # html  = template.render(context_dict)
    # result = BytesIO()
    # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    # if not pdf.err:
    #     return HttpResponse(result.getvalue(), content_type='application/pdf')
    # return None

    # response = HttpResponse(content_type='application/pdf')  
    # response['Content-Disposition'] = 'attachment; filename="file.pdf"'  
    # p = canvas.Canvas(response)    
    # p.drawString(100,700, "Hello World")  
    # p.showPage()  
    # p.save()  
    # return response  
       
    # products = Courses.objects.get(request.GET.get("get_viewpdf_id"))

    # template_path = 'pdf.html'

    # context = {'products': products}

    # response = HttpResponse(content_type='application/pdf')

    # response['Content-Disposition'] = 'filename="products_report.pdf"'

    # template = get_template(template_path)

    # html = template.render(context)

    # # create a pdf
    # pisa_status = pisa.CreatePDF(
    #    html, dest=response)
    # # if error then show some funy view
    # if pisa_status.err:
    #     return HttpResponse('We had some errors <pre>' + html + '</pre>')
    # return response


    x=""
    filter_data=request.GET.get("result")
    # print(request.GET.values)
    
    print(filter_data,"********")
    if filter_data:
        print(filter_data)
        x = Courses.objects.filter(course_name__icontains=filter_data)
        print(x)
        html = render_to_string('courses/list_course_filter.html',{'x':x})
        return JsonResponse({'html':html})
    elif filter_data=="":
        x=Courses.objects.all()
        print(x)
        html= render_to_string('courses/list_course_filter.html',{'x':x})
        return JsonResponse({'html':html})
       

       


    msg = ""
    err_msg = ""
    try:
        data = request.POST["search"]
        data = data.strip()
        if len(data) == 0:
            data = ""
        else:
            print("Found data POST")
            print(data)
    except Exception as E:
        print(E)
        print("------------")
        try:
            data = request.GET.get("search_string")
            if data:
                data = data.strip()
                if len(data) == 0:
                    data = ""
                    print("Found but  GET None")
                else:
                    print("Found data GET")
                    print(data)
            else:
                print("GET NO NO DATA")
                data = ""
        except Exception as E:
            print(E)
            print("===========")
    if data:
        c = data.split()  # splitting search paramenter for improving search power
        if not 1 in c:
            c.append(c[0])

    if request.method == "GET":
        if data:
            print("*************GET DATA***********")
            courses = Courses.objects.filter(
                Q(course_name__istartswith=c[0]) | Q(course_name__icontains=c[0])
            ).values(
                "id",
                "course_name",
                "duration_value",
                "duration_period__duration",
                "level__level",
                "price_per_week",
                "price_per_month",
                "is_active"
            )
        else:
            print("*************GET NO DATA***********")
            courses = Courses.objects.filter().values(
                "id",
                "course_name",
                "duration_value",
                "duration_period__duration",
                "level__level",
                "price_per_week",
                "price_per_month",
                "is_active"
            )
    else:
        if data:
            print("*************POST  DATA***********")
            courses = Courses.objects.filter(
                Q(course_name__istartswith=c[0]) | Q(course_name__icontains=c[0])
            ).values(
                "id",
                "course_name",
                "duration_value",
                "duration_period__duration",
                "level__level",
                "price_per_week",
                "price_per_month",
                "is_active"
            )
        else:
            print("*************POST No DATA***********")
            courses = Courses.objects.filter().values(
                "id",
                "course_name",
                "duration_value",
                "duration_period__duration",
                "level__level",
                "price_per_week",
                "price_per_month",
                "is_active"
            )

    try:
        page = request.GET.get("page", 1)
        paginator = Paginator(courses, 10)
        courses = paginator.page(page)
        if not courses:
            courses = {}
            err_msg = "No courses found"
    except PageNotAnInteger:
        courses = {}
        err_msg = "Invalid Page Number"
    except EmptyPage:
        courses = {}
        err_msg = "Empty Page"
    except Exception as e:
        err_msg = "Something went wrong"

    return render(
        request,
        "courses/list_courses.html",
        {"msg": msg, "err_msg": err_msg, "courses": courses, "data": data},
    )


@login_required
def add_course(request):

    msg = ""
    err_msg = ""
    error_msg = {}
    level_obj = CourseLevels.objects.filter().values("id", "level").order_by("id")
    time_obj = TimePeriods.objects.filter().values("id", "duration").order_by("id")
    if request.method == "POST":
        try:
            course_name = request.POST["course_name"].strip()
            course_description = request.POST["course_description"].strip()
            price_per_week = request.POST["price_per_week"].strip()
            price_per_month = request.POST["price_per_month"].strip()

            level = request.POST["level"].strip()
            print(level,"ooooooo")

            if level:
                level = int(level)
            try:
                duration_value = request.POST["duration_value"].strip()
                duration_period = request.POST["duration_period"].strip()
                if duration_period:
                    duration_period = int(duration_period)
            except:
                duration_value = None
                duration_period = None

            form = add_course_serializer(data=request.POST)
            if form.is_valid():
                form2 = course_fk_check(data=request.POST)
                if form2.is_valid():
                    print("YES")
                    try:
                        form.save()
                    except Exception as er:
                        err_msg = er
                        return render(
                            request,
                            "courses/add_course.html",
                            {
                                "error_msg": error_msg,
                                "msg": msg,
                                "err_msg": err_msg,
                                "level_obj": level_obj,
                                "time_obj": time_obj,
                                "course_name": course_name,
                                "duration_value": duration_value,
                                "duration_period": duration_period,
                                "level": level,
                                "course_description": course_description,
                                "price_per_week": price_per_week,
                                "price_per_month": price_per_month
                            },
                        )

                    msg = "Successfully saved"
                    return render(
                        request,
                        "courses/add_course.html",
                        {"msg": msg, "level_obj": level_obj, "time_obj": time_obj},
                    )
                else:
                    err_msg = "Invalid Data foreign keys"
                    print("error foreign Keys")
                    print(form2.errors)
                    for key, value in form2.errors.items():
                        error_msg[key] = value[0]
            else:
                err_msg = "Invalid Data"
                for key, value in form.errors.items():
                    error_msg[key] = value[0]
            return render(
                request,
                "courses/add_course.html",
                {
                    "error_msg": error_msg,
                    "msg": msg,
                    "err_msg": err_msg,
                    "level_obj": level_obj,
                    "time_obj": time_obj,
                    "course_name": course_name,
                    "duration_value": duration_value,
                    "duration_period": duration_period,
                    "level": level,
                    "course_description": course_description,
                    "price_per_week": price_per_week,
                    "price_per_month": price_per_month
                },
            )
        except Exception as E:
            print(E)
            err_msg = "Something went wrong"
            return render(
                request,
                "courses/add_course.html",
                {
                    "error_msg": error_msg,
                    "msg": msg,
                    "err_msg": err_msg,
                    "level_obj": level_obj,
                    "time_obj": time_obj,
                },
            )
    return render(
        request,
        "courses/add_course.html",
        {
            "error_msg": error_msg,
            "msg": msg,
            "err_msg": err_msg,
            "level_obj": level_obj,
            "time_obj": time_obj,
        },
    )


@login_required
def edit_course(request, id):
    msg = ""
    err_msg = ""
    error_msg = {}
    success = 1
    level_obj = CourseLevels.objects.filter().values("id", "level")
    time_obj = TimePeriods.objects.filter().values("id", "duration").order_by("id")
    course_obj = Courses.objects.filter(id=id).values(
        "course_name",
        "duration_value",
        "duration_period",
        "level",
        "course_description",
        "price_per_week",
        "price_per_month"
    )
    if course_obj:
        course_obj = course_obj[0]
    else:
        err_msg = "Invalid Course"
        return render(
            request,
            "courses/edit_course.html",
            {"error_msg": error_msg, "msg": msg, "err_msg": err_msg},
        )
    if request.method == "POST":
        success = 0
        course_name = request.POST["course_name"].strip()
        course_description = request.POST["course_description"].strip()
        price_per_week = request.POST["price_per_week"].strip()
        price_per_month = request.POST["price_per_month"].strip()
        level = request.POST["level"].strip()

        if level:
            level = int(level)

        try:
            duration_value = request.POST["duration_value"].strip()
            duration_period = request.POST["duration_period"].strip()
            if duration_period:
                duration_period = int(duration_period)
        except:
            duration_value = None
            duration_period = None

        # serializer validations
        form = edit_course_serializer(
            instance=Courses.objects.get(id=id), data=request.POST
        )
        if form.is_valid():
            updated_obj = form.save()
            msg = "Updated Successfully"
            success = 1
            course_obj = Courses.objects.filter(id=id).values(
                "course_name",
                "duration_value",
                "duration_period",
                "level",
                "course_description",
                "price_per_week",
                "price_per_month"
            )[0]
        else:
            err_msg = "Invalid data"
            for key, value in form.errors.items():
                error_msg[key] = value[0]

        return render(
            request,
            "courses/edit_course.html",
            {
                "error_msg": error_msg,
                "msg": msg,
                "err_msg": err_msg,
                "level_obj": level_obj,
                "time_obj": time_obj,
                "course_obj": course_obj,
                "course_name": course_name,
                "duration_value": duration_value,
                "duration_period": duration_period,
                "level": level,
                "course_description": course_description,
                "price_per_week": price_per_week,
                "price_per_month": price_per_month,
                "success": success
            },
        )
    else:
        return render(
            request,
            "courses/edit_course.html",
            {
                "error_msg": error_msg,
                "msg": msg,
                "err_msg": err_msg,
                "level_obj": level_obj,
                "time_obj": time_obj,
                "course_obj": course_obj,
                "success": success,
            },
        )


@api_view(["DELETE"])
@login_required
def delete_course(request):
    if request.method == "DELETE":
        id = request.GET.get("id")
        new_status = request.GET.get("toggle_status")
        try:
            obj = Courses.objects.get(id=id)
            if new_status == 1 or new_status == "1":
                obj.is_active = 1
            else:
                obj.is_active = 0
            obj.save()
            return Response({"status": 200, "message": "success"})
        except Exception as e:
            print(e)
            return Response({"status": 500, "message": "Internal server error"})
    else:
        return Response({"status": 500, "message": "Bad Request"})

def course_class(request):
    course_ids = Courses.objects.filter().values("id", "course_name")
    teacher_ids = User.objects.filter().values("id", "username")
    week_days =  Weekdays.objects.filter().values("id", "day").order_by('id')
    if request.method == "POST":
        course_id = request.POST.get('course_id')
        day_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        if 'PM' in  request.POST['start_time']:
            new_start_time=convert24(start_time)
        if 'PM' in  request.POST['end_time']:
            new_end_time= convert24(end_time)

        if 'AM' in request.POST['start_time']:
            print("Am")
            new_start_time=convert24AM(start_time)
        if 'AM' in request.POST['end_time']:
            new_end_time=convert24AM(end_time)
        class_date = request.POST.get('class_date')
        class_grade = request.POST.get('class_grade')
        teac_id = request.POST.get('teacher_id', None)
        class_link = request.POST.get('class_link')
        recorded_link = request.POST.get('recorded_link')
        addclass_address= request.POST.get('addclassaddress')
        section = request.POST.get('section')
        answer=request.POST.get('select_id')
        
       
        try:
            course = Courses.objects.get(course_name=course_id)
            # print(course, "get")
        except:
            course = ""
            # print("empty")
        try:
            days = Weekdays.objects.get(day=day_week)
            # print(days, "get")
        except:
            days = ""
            # print("empty")

        try:
            teacher = User.objects.get(username=teac_id)
        except:
            teacher = None
        coursesss = Course_Classes.objects.create(course_id=course,day_of_week=days,
        start_time=new_start_time,end_time=new_end_time,class_date=class_date,class_grade=class_grade,teacher_id=teacher,class_link=class_link,

        recorded_link=recorded_link, address=addclass_address,class_type=answer,section=section,is_active=True)
        # print(teacher.email, "email")

        # msg_html = render_to_string('secret/mail.html')
        print(course_id)
        list= []
        email_get = Profile.objects.filter(role_id__role="Parent").all()
        context={}
        print(email_get)
        for eml_get in email_get:
            list.append(eml_get.user.email)
            from_email = settings.EMAIL_HOST_USER
            reciever_list= list 
            subject ="Wahoo New class is created..!!"
            html_message=render_to_string('secret/mail.html',{"course":course, "days":days, "new_start_time":new_start_time, "new_end_time":new_end_time, "class_date":class_date,"class_grade":class_grade,"teacher":teacher,"section":section})
            plain_message=strip_tags(html_message)
            if answer=="premisis":
                print(answer)
                # message = f"New class is created with course name {course},day of week {days}, start time {new_start_time}, end time {new_end_time}, class date {class_date}, class grade {class_grade}, teacher id {teacher}, and with section {section}"
                # context={"course":course, "days":days, "new_start_time":new_start_time, "new_end_time":new_end_time, "class_date":class_date}
                               
                send_mail(subject, html_message,from_email,reciever_list,html_message=html_message)
            elif answer=="virtual":
                print(answer)
                message = f"New class is created with course name {course}, day of week {days}, start time {new_start_time}, end time {new_end_time}, class date {class_date}, class grade {class_grade}, teacher id {teacher}, class link {class_link}, recorded link {recorded_link} and with section {section}"
                context={"course":course, "days":days, "new_start_time":new_start_time, "new_end_time":new_end_time, "class_date":class_date}
                send_mail(subject,html_message , from_email,reciever_list, html_message=plain_message)

        return render(request,"courses/course_classes.html", {'msg':"Successfully saved"})

    return render(request,"courses/course_classes.html", {'course_ids':course_ids, "teacher_ids":teacher_ids, "week_days": week_days})

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
    print("Arrival")
    if str1[-2:] == "AM": 
        print(str1.replace('AM',":00").replace(" ", ""))
        return str1.replace('AM',":00").replace(" ", "")
    else:
        if(str1[1]==":"):
            a = str(int(str1[:1]) + 12) + str1[1:8] 
            print(a.replace('AM',":00").replace(" ", ""))
            return a.replace('AM',":00").replace(" ", "")
        else:
            b = str(int(str1[:2]) + 12) + str1[2:8] 
            print(b)
            print(b.replace('AM',":00").replace(" ", ""))
            return b.replace('AM',":00").replace(" ", "")
    
def addstudent(request):
    print("hello")
    
   
    # dr=User.objects.get(id=4)
    # print(dr,"-------")
    # r=User.objects.all()
    # data={"r":r}
    # g=classs.objects.get(id=1)
    # print(g,"_________________---")
    r= User.objects.filter().values("username")
    print(r)
    if request.method == "POST":
        username=request.POST.get('username')   
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        password=request.POST.get('password')
        files=request.FILES.get('myfile')
        addcourses=request.POST.get('addcourses')
        print(files)
        print(username,firstname,lastname,password)
        print(addcourses,"ADDCOURSES")

        if User.objects.filter(username=username).exists():
            # get_username=User.objects.get(id=3)
            print("$$$$$$$") 
            get_username = User.objects.get(username=username)
            objec = AddStudent.objects.create(username=get_username, first_name=firstname, last_name=lastname,password=password,image_upload=files)
           
            users=classs.objects.filter(name=addcourses)[0]
       
            if users:
                objec.students.add(users) #many to many
            else:
                classs.objects.create(name=addcourses)
              

            

          

            messages.success(request, "added")

            
            return render(request,"courses/addstudent.html")
            
        else:
           
            print(r)
            print("*******")
            classs.objects.create(name=g)
            User.objects.create(username=username,first_name=firstname,last_name=lastname,password=password,image_upload=files)
            classs.objects.create(name=addcourses)
           
            messages.success(request, "created")
            return render(request,"courses/addstudent.html")
    return render(request,"courses/addstudent.html",{"r":r})


def view_image(request):
    image=AddStudent.objects.all()
    context={"image":image}

    return render(request,"courses/view_image.html",context)