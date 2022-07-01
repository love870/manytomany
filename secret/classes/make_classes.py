from __future__ import unicode_literals
import random,string,  time,schedule, os, urllib.request, datetime, sys, django, json, pytz, threading, importlib, csv,json,ast,boto3,datetime , io,base64,hashlib,re;
sys.path.append('../../')
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pillarz.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
        ) from exc
django.setup()
from django.contrib import auth
from django.db.models import Q
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from secret.models  import Courses, CourseLevels, TimePeriods, Course_Classes, Class_Students, Payments,Order_Items,Course_Schedules,Orders
from django.db.models import Count, Sum
from datetime import date
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives




def add_classes():
    print('Searching for new payments')
    for payment in Payments.objects.filter().values('id','order_id','order_id__selected_date','transaction_id','order_id__parent_id__email','order_id__parent_id__first_name','order_id__parent_id__last_name','order_id__grand_total_amt','promocode_id__code','promocode_id__discount_percentage'):
        today = date.today()
        order_id=payment['order_id']
        payment_id=payment['id']
        transaction_id=payment['transaction_id']
        email=payment['order_id__parent_id__email']
        first_name=payment['order_id__parent_id__first_name']
        last_name=payment['order_id__parent_id__last_name']
        grand_total_amt=payment['order_id__grand_total_amt']
        try:
            transaction_exists=0  #assuming  duplicate transaction id doesn't exists
            duplicates=Payments.objects.filter(transaction_id=transaction_id)
            if duplicates[1]:
                # more than one transaction id exists
                already_exists=Payments.objects.filter(transaction_id=transaction_id,id__lt=payment_id)
                if already_exists:
                    transaction_exists=1
        except Exception as e:
            print(e)

        if transaction_exists==0:
      
            if not Class_Students.objects.filter(order_id=payment['order_id']):
                student_info = Order_Items.objects.filter(order_id=payment['order_id']).values("course_id",'course_duration','child_grade').annotate(total_seats=Count('id'))
                total_seats=Order_Items.objects.filter(order_id=payment['order_id']).count()
                print(total_seats)
                course_id=student_info[0]['course_id']
                course_duration=student_info[0]['course_duration']
                child_grade = student_info[0]['child_grade']
                course_selected_date =payment["order_id__selected_date"]
                

                existing_classes= Class_Students.objects.filter(course_class_id__class_date__gte=today).filter(course_class_id__course_id=course_id).filter(course_class_id__class_grade=child_grade).annotate(reserved_seats=Sum("number_of_seats")).values('course_class_id')
                if existing_classes:
                    # if classes already exists with course id
                    print("already available class with students")
                    if course_duration=="weekly":
                        print("weekly payment")
                        print(course_selected_date)
                        add_to_existing_classes(course_id,course_selected_date,total_seats,order_id,child_grade)
                    else:
                        print("monthly payment")
                        monday_date_arr= get_all_mondays_of_month(course_selected_date)
                        # creating monthly classes
                        for course_date in monday_date_arr:
                            print(course_date)
                            add_to_existing_classes(course_id,course_date,total_seats,order_id,child_grade)

                else:
                    print("no existing classes")
                    # creating new classes
                    if course_duration=="weekly":
                       
                        print(course_selected_date)
                        add_new_classes(course_id,course_selected_date,payment['order_id'],total_seats,child_grade)
                    else:
                      
                        monday_date_arr= get_all_mondays_of_month(course_selected_date)
                        # creating monthly classes
                        for i in monday_date_arr:
                            print(i)
                            add_new_classes(course_id,i,payment['order_id'],total_seats,child_grade)

                # # send welcome email
                try:
                    coupon_code=payment['promocode_id__code']  
                    discount_percentage = payment['promocode_id__discount_percentage']
                    print("===========================")
                    order_details=Order_Items.objects.filter(order_id=order_id).values('child_name','course_duration','course_price','course_id__course_name','course_id__level_id__level')
                    get_selected_date=Orders.objects.filter(id=order_id).values('selected_date')
                    subject, from_email, to = "Hey there - Your Order has beed Placed!", settings.EMAIL_HOST_USER,email
                    html_content = render_to_string('email/order_confirmation.html', {'first_name':first_name,"last_name":last_name,'order_id':order_id,'grand_total_amt':grand_total_amt,'order_details':order_details,'course_name':order_details[0]['course_id__course_name'],'course_duration':order_details[0]['course_duration'],'level':order_details[0]['course_id__level_id__level'] ,'selected_date':get_selected_date[0]['selected_date'],'coupon_code':coupon_code,'discount_percentage':discount_percentage})
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as e:
                    print("error sending mail")
                    print(e)
        else:
            print('duplicate transaction id is present')
        
def add_new_classes(course_id,course_selected_date,order_id,total_seats,child_grade):
    #getting unique section id
    section = get_random_alphanumeric_string(4)
    for schedule in Course_Schedules.objects.filter(course_id_id=course_id).values("course_id",'day_of_week','start_time','end_time'):
        add_to_date = int(schedule['day_of_week'])-1  
        final_date= course_selected_date + datetime.timedelta(days=add_to_date)

        # creating course classes
        create_course_class=Course_Classes.objects.create(
            course_id_id=schedule['course_id'],
            day_of_week_id=schedule['day_of_week'],
            start_time=schedule['start_time'], 
            end_time= schedule['end_time'],
            class_date=final_date,
            class_grade=child_grade,
            section = section,
            is_active=1,
        ) 

        course_class_id=create_course_class.pk
        # creating Class_Students

        Class_Students.objects.create(
            course_class_id_id=course_class_id,
            order_id_id=order_id,
            number_of_seats=total_seats, 
            is_active=1,
        ) 






def add_to_existing_classes(course_id,course_selected_date,total_seats,order_id,child_grade):
    #getting unique section id
    section = get_random_alphanumeric_string(4)
    for schedule in Course_Schedules.objects.filter(course_id_id=course_id).values("course_id",'day_of_week','start_time','end_time'):
        add_to_date = int(schedule['day_of_week'])-1  
        final_date= course_selected_date + datetime.timedelta(days=add_to_date)
        classes= Class_Students.objects.filter(course_class_id__class_date=final_date).filter(course_class_id__course_id=course_id).filter(course_class_id__class_grade=child_grade).values('course_class_id','course_class_id__class_date').annotate(reserved_seats=Sum("number_of_seats")).order_by('course_class_id')
        if classes:
            student_fits=0
            for i in classes:
                print('-----classes exists-----')
                if i['reserved_seats'] + total_seats  <=5:
                    student_fits=1
                    course_class_id=i['course_class_id']
                    break

            if student_fits==1 :
                print('----students fits-------')
                Class_Students.objects.create(
                    course_class_id_id=course_class_id,
                    order_id_id=order_id,
                    number_of_seats=total_seats, 
                    is_active=1,
                ) 

            else:
                print('------students not fits----')
                # creating course classes
                create_course_class=Course_Classes.objects.create(
                    course_id_id=schedule['course_id'],
                    day_of_week_id=schedule['day_of_week'],
                    start_time=schedule['start_time'], 
                    end_time= schedule['end_time'],
                    class_date=final_date,
                    class_grade=child_grade,
                    section=section,
                    is_active=1,
                ) 
                course_class_id=create_course_class.pk
                # creating Class_Students
                Class_Students.objects.create(
                    course_class_id_id=course_class_id,
                    order_id_id=order_id,
                    number_of_seats=total_seats, 
                    is_active=1,
                ) 

        else:
            print('------classes not exists------')
            # creating course classes
            create_course_class=Course_Classes.objects.create(
                course_id_id=schedule['course_id'],
                day_of_week_id=schedule['day_of_week'],
                start_time=schedule['start_time'], 
                end_time= schedule['end_time'],
                class_grade=child_grade,
                class_date=final_date,
                section=section,
                is_active=1,
            ) 
            course_class_id=create_course_class.pk
            # creating Class_Students
            Class_Students.objects.create(
                course_class_id_id=course_class_id,
                order_id_id=order_id,
                number_of_seats=total_seats, 
                is_active=1,
            ) 


#datetime functions
def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)

def get_next_monday(current_monday_date):
    monday_date= current_monday_date + datetime.timedelta(days=7)
    return monday_date

def get_all_mondays_of_month(course_selected_date):
    course_selected_day=course_selected_date.weekday()
    if course_selected_day!=0:
        # if selected day is not monday
        course_selected_date = next_weekday(course_selected_date, 0)
    # getting next 3 mondays
    monday_date_arr=[course_selected_date] 
    for i in range(3):
        current_monday_date = monday_date_arr[-1]
        next_monday_date    = get_next_monday(current_monday_date)
        monday_date_arr.append(next_monday_date)
    return monday_date_arr


#for unique section id
def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    currentDay = datetime.datetime.now().day
    currentMonth = datetime.datetime.now().month
    currentYear = datetime.datetime.now().year
    result_str  =  str(currentDay) +'-'+ str(currentMonth)+'-'+ str(currentYear) + '-'+ result_str 
    return result_str


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
schedule.every(5).seconds.do(run_threaded,add_classes)
while True:
    schedule.run_pending()
    time.sleep(1)

