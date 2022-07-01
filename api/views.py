import sys, os, json, io, boto3, base64, hashlib
from boto3.s3.transfer import S3Transfer
from datetime import datetime
from decouple import config

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Profile, Timezones, Roles

from secret.serializers.users import api_register


def checkAuth(request):
    if Token.objects.filter(key=request.META.get("HTTP_TOKEN")):
        return Token.objects.filter(key=request.META.get("HTTP_TOKEN"))[0]
    else:
        return 0


def checkTimezone(request):
    if Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE")).exists():
        return Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE"))[0]
    else:
        obj = Timezones.objects.create(tz_name=request.META.get("HTTP_TIMEZONE"))
        return Timezones.objects.filter(tz_name=request.META.get("HTTP_TIMEZONE"))[0]


# Create your views here.
@api_view(["POST"])
def Login(request):

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)

    reqdata = json.loads(request.body.decode("utf-8"))
    if int(reqdata["google"]) == 0:
        user = auth.authenticate(
            username=reqdata["username"], password=reqdata["secret"]
        )
    else:
        user = User.objects.filter(email=reqdata["email"]).values("is_active")
        if user:
            user = user[0]
            if user["is_active"] == False:
                data = {
                    "status": 400,
                    "data": {
                        "message": "Deactive account. Please check your email for verification or contact the admin!"
                    },
                }
                return JsonResponse(data)
        else:
            user = None

    if user:
        token = Token.objects.get_or_create(user=user)
        u = {}
        u["token"] = token[0].key
        u["id"] = user.id
        u["username"] = user.username
        u["role"] = user.profile.role.role
        u["phone"] = user.profile.phone
        u["first_name"] = user.first_name
        u["last_name"] = user.last_name
        u["email"] = user.email
        u["is_staff"] = user.is_staff
        u["is_active"] = user.is_active
        u["timezone"] = user.profile.timezone.tz_name if user.profile.timezone else None
        u["message"] = "Logged in successfully"
        data = {"status": 200, "data": u}
    else:
        if int(reqdata["google"]) != 0:
            data = {"status": 400, "data": {"message": "Account not registered"}}
        else:
            user = User.objects.filter(username=reqdata["username"]).values("is_active")
            if user:
                data = {"status": 400, "data": {"message": "Invalid password"}}
                if user[0]["is_active"] == False:
                    data = {
                        "status": 400,
                        "data": {
                            "message": "Deactive account. Please check your email for verification or contact the admin!"
                        },
                    }
            else:
                data = {"status": 400, "data": {"message": "Invalid username"}}
    return JsonResponse(data)


@api_view(["POST"])
def Register(request):

    try:
        timezone = checkTimezone(request)
        if timezone == 0:
            data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
            return JsonResponse(data)
        reqdata = json.loads(request.body.decode("utf-8"))
        try:
            usrname = (
                reqdata["username"]
                if (int(reqdata["google"]) == 0)
                else reqdata["email"]
            )
        except:
            usrname = reqdata["email"]
        if reqdata["password"] != reqdata["confirm-password"]:
            data = {"status": 400, "data": {"message": "Passwords did not match!"}}
            return JsonResponse(data)
        # check existing username
        if User.objects.filter(username=usrname):
            is_active = User.objects.filter(username=usrname).values("is_active")
            is_active = is_active[0]["is_active"]
            print(is_active)
            if is_active == 0:
                # print("Was deactive")
                # User.objects.filter(username=usrname).update(is_active=1)
                # re_register= User.objects.get(username=usrname)
                # re_register.set_password(reqdata['password'])
                # re_register.save()
                data = {
                    "status": 500,
                    "data": {
                        "message": "Account is deactive. Please contact the admin! "
                    },
                }
            else:
                data = {"status": 500, "data": {"message": "Account already exists! "}}
            return JsonResponse(data)
        if Profile.objects.filter(phone=reqdata["phone"]):
            data = {"status": 500, "data": {"message": "Phone number already exists! "}}
            return JsonResponse(data)

        # checking validations
        form = api_register(data=reqdata)
        if not form.is_valid():
            print(form.errors)
            data = {"status": 500, "data": {"message": "Invalid Data"}}
            return JsonResponse(data)

        # create user
        if int(reqdata["google"]) == 0:
            try:
                user = User(
                    username=usrname,
                    email=reqdata["email"],
                    first_name=reqdata["first_name"],
                    last_name=reqdata["last_name"],
                    is_active=0,
                )
                user.set_password(reqdata["password"])
                user.is_active = True
                user.save()
                print("user save")
                # save user profile
                print(Roles.objects.all())
                role_obj = Roles.objects.get(role="Parent")
                p = Profile.objects.get_or_create(
                    user=user,
                    latitude=reqdata["latitude"],
                    longitude=reqdata["longitude"],
                    device_token=reqdata["device_token"],
                    role=role_obj,
                    phone=reqdata["phone"],
                )
            except Exception as E:
                print("++++++++++++++++++++++++++=")
                print(str(E))
                try:
                    user.delete()
                except Exception as e:
                    print(e)
                data = {
                    "status": 500,
                    "data": {"message": "Something went wrong!", "trace": "error"},
                }
                return JsonResponse(data)
        else:
            # .split('@')[0]
            try:
                user = User(
                    username=usrname,
                    email=reqdata["email"],
                    first_name=reqdata["first_name"],
                    last_name=reqdata["last_name"],
                )
                user.set_unusable_password()
                user.is_active = True
                user.save()
                print("user save")
                # save user profile
                role_obj = Roles.objects.get(role="Parent")
                p = Profile.objects.get_or_create(
                    user=user,
                    latitude=reqdata["latitude"],
                    longitude=reqdata["longitude"],
                    device_token=reqdata["device_token"],
                    role=role_obj,
                    phone=reqdata["phone"],
                )
            except Exception as E:
                print("++++++++++++++++++++++++++=")
                print(E)
                try:
                    user.delete()
                except Exception as e:
                    print(e)
                data = {
                    "status": 500,
                    "data": {"message": "Something went wrong!", "trace": str(e)},
                }
                return JsonResponse(data)

        # send welcome email
        # try:
        #     token = Token.objects.get_or_create(user=user)
        #     print("gfgfdgf", token)

        #     subject = "welcome to GFG world"
        #     message = f"http://137.184.122.181/api/verify_email/?token={token[0]}"
        #     email_from = settings.EMAIL_HOST_USER
        #     recipient_list = [user.email]
        #     send_mail(subject, message, email_from, recipient_list)

        # web_url = config('WEBURL', default='pillarzapi-env.eba-fpqhfczp.us-east-1.elasticbeanstalk.com/')
        # subject, from_email, to = "Hey there - we're flipping upside down that you've joined us!", settings.EMAIL_HOST_USER, user.email
        # message = "http://ddb4-122-173-29-11.ngrok.io/api/verify_email/?token='+token[0].key+"
        # send_mail(subject, message, from_email, to)
        #
        # # msg = EmailMultiAlternatives(subject,  from_email, [to])
        # # msg.attach_alternative(html_content, "text/html")
        # # msg.send()
        # print("Email send")

        # except Exception as e:
        #     print("*************")
        #     print(e)

        if "timezone" in reqdata:
            t = Timezones.objects.filter(tz_name=reqdata["timezone"])
            if t:
                user.profile.timezone = t[0]
                user.profile.save()

        # token = Token.objects.get_or_create(user=user)

        u = {}
        # u['token']      = token[0].key
        # u['id']         = user.id
        # u['username']   = user.username
        # u['role']       =  user.profile.role.role
        # u['phone']       = user.profile.phone
        # u['first_name'] = user.first_name
        # u['last_name']  = user.last_name
        # u['email']      = user.email
        # u['is_staff']   = user.is_staff
        # u['is_active']  = user.is_active
        # u['timezone']   = None
        u["message"] = "Registered Successfully."
        if user.profile.timezone:
            u["timezone"] = user.profile.timezone.tz_name

        # user = auth.authenticate(username=usrname, password=reqdata['password'])

        data = {"status": 200, "data": u}
        return JsonResponse(data)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(e)},
        }
        return JsonResponse(data)



@api_view(["PUT", "GET"])
def MyProfile(request):

    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    timezone = checkTimezone(request)
    if timezone == 0:
        data = {"status": 403, "data": {"message": "Please Check Timezone!"}}
        return JsonResponse(data)
    try:

        AWS_STORAGE_URL = config("AWS_STORAGE_URL", default="")
        if request.method == "PUT":
            reqdata = json.loads(request.body.decode("utf-8"))
            User.objects.filter(id=token.user.id).update(
                first_name=reqdata["first_name"],
                last_name=reqdata["last_name"],
                email=reqdata["email"],
                username=reqdata["username"],
            )
            Profile.objects.filter(user=token.user.id).update(
                latitude=reqdata["latitude"],
                longitude=reqdata["longitude"],
                my_description=reqdata["my_description"],
                twitter_handle=reqdata["twitter_handle"],
                facebook_handle=reqdata["facebook_handle"],
                instagram_handle=reqdata["instagram_handle"],
                paypal_email=reqdata["paypal_email"],
            )
            token = checkAuth(request)

        p = {}
        p["latitude"] = token.user.profile.latitude
        p["longitude"] = token.user.profile.longitude
        p["my_description"] = token.user.profile.my_description
        p["twitter_handle"] = token.user.profile.twitter_handle
        p["facebook_handle"] = token.user.profile.facebook_handle
        p["instagram_handle"] = token.user.profile.instagram_handle
        p["paypal_email"] = token.user.profile.paypal_email
        p["avatar"] = AWS_STORAGE_URL + str(token.user.profile.avatar)
        p["role"] = token.user.profile.role.role
        p["phone"] = token.user.profile.phone
        p["first_name"] = token.user.first_name
        p["last_name"] = token.user.last_name
        p["email"] = token.user.email
        p["username"] = token.user.username

        data = {"status": 200, "data": p, "message": "success"}
        return JsonResponse(data)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(e)},
        }
        return JsonResponse(data)


@api_view(["PUT"])
def ChangePassword(request):

    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    try:

        if request.method == "PUT":
            print("arrive")
            u = token.user
            reqdata = json.loads(request.body.decode("utf-8"))
            opwd = reqdata["opwd"]
            npwd = reqdata["npwd"]
            cnpwd = reqdata["cnpwd"]
            if u.check_password(opwd) == True:
                if npwd == cnpwd:
                    if len(npwd) < 6:
                        data = {
                            "status": 400,
                            "data": {
                                "message": "Password length must be atleast 6 characters!"
                            },
                        }
                        return JsonResponse(data)
                    u.set_password(npwd)
                    u.save()
                    msg = "Password Updated!"
                    data = {"status": 200, "data": {"message": msg}}
                    return JsonResponse(data)
                else:
                    err = "New password(s) didn't match!"
                    data = {"status": 400, "data": {"message": err}}
                    return JsonResponse(data)
            else:
                err = "Incorrect Old Password!"
                data = {"status": 400, "data": {"message": err}}
                return JsonResponse(data)
        else:
            data = {"status": 405, "data": {"message": "Only PUT method accepted!"}}
            return JsonResponse(data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(e)},
        }
        return JsonResponse(data)


@api_view(["POST"])
def ForgotPassword(request):
    reqdata = json.loads(request.body.decode("utf-8"))

    if "email" in reqdata:

        user = User.objects.filter(email=reqdata["email"]).first()
        if user:
            if user.has_usable_password():

                # create token
                web_url = config("WEBURL", default="http://137.184.122.181/")
                strfortoken = user.email + "/" + str(datetime.now().timestamp())
                token = hashlib.md5(strfortoken.encode()).hexdigest()
                user.profile.onetime_token = token
                user.profile.save()

                # send email
                subject, from_email, to = (
                    "Reset your password",
                    settings.EMAIL_HOST_USER,
                    user.email,
                )
                html_content = render_to_string(
                    "email/reset-password.html",
                    {
                        "name": user.username,
                        "reset_link": web_url + "reset-password/" + token + "/",
                    },
                )
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                data = {
                    "status": 200,
                    "data": {
                        "message": "We have sent a link to reset your password on your registered email.!"
                    },
                }
                return JsonResponse(data)

            else:
                data = {"status": 400, "data": {"message": "Login with Google!"}}
                return JsonResponse(data)
        else:
            data = {"status": 400, "data": {"message": "Account not found!"}}
            return JsonResponse(data)
    elif "npwd" in reqdata and "cnpwd" in reqdata and "token" in reqdata:
        print("exist")
        p = Profile.objects.filter(onetime_token=reqdata["token"]).first()
        if p:
            u = p.user
            npwd = reqdata["npwd"].strip()
            cnpwd = reqdata["cnpwd"].strip()
            if npwd == cnpwd:
                if len(npwd) > 5:
                    u.set_password(npwd)
                    u.save()
                    p.onetime_token = None
                    p.save()
                    msg = "Password Updated!"
                    data = {"status": 200, "data": {"message": msg}}
                    return JsonResponse(data)
                else:
                    err = "Length of password should be atleast 6 characters!"
                    data = {"status": 400, "data": {"message": err}}
                    return JsonResponse(data)
            else:
                err = "New password(s) didn't match!"
                data = {"status": 400, "data": {"message": err}}
                return JsonResponse(data)
        else:
            data = {
                "status": 200,
                "data": {"message": "Password reset token has expired!"},
            }
            return JsonResponse(data)
    else:
        data = {"status": 400, "data": {"message": "Invalid request!"}}
        return JsonResponse(data)


@api_view(["POST", "GET"])
def Avatar(request):

    token = checkAuth(request)
    if token == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return Response(data)

    try:

        AWS_STORAGE_URL = config("AWS_STORAGE_URL", default="")
        user = token.user
        if request.method == "POST":
            avatar = request.FILES["file"]
            AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
            AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
            AWS_STORAGE_BUCKET_RGN = config(
                "AWS_STORAGE_BUCKET_RGN", default="us-east-1"
            )
            AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
            fs = FileSystemStorage(os.getcwd() + "/static/img/avatars")
            fname = avatar.name
            filename = fs.save(fname, avatar)
            s3_path = "avatars/" + fname
            local_path = os.getcwd() + "/static/img/avatars/" + fname
            transfer = S3Transfer(
                boto3.client(
                    "s3",
                    AWS_STORAGE_BUCKET_RGN,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    use_ssl=False,
                )
            )
            client = boto3.client("s3")

            transfer.upload_file(
                local_path,
                AWS_STORAGE_BUCKET_NAME,
                s3_path,
                extra_args={"ACL": "public-read"},
            )
            Profile.objects.filter(user=token.user.id).update(avatar=s3_path)

            os.remove(local_path)
            token = checkAuth(request)
            user = token.user
        if str(token.user.profile.avatar) != "":
            data = {
                "status": 200,
                "data": {"url": AWS_STORAGE_URL + str(token.user.profile.avatar)},
            }
        else:
            data = {"status": 404, "data": {"message": "avatar missing!"}}
        return Response(data)
    except Exception as e:
        print(e)
        data = {
            "status": 500,
            "data": {"message": "Something went wrong!", "trace": str(e)},
        }
        return JsonResponse(data)


@api_view(["POST"])
def Logout(request):
    print(request.META.get("HTTP_TOKEN"))

    print(request.user)

    if checkAuth(request) == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)
    try:
        auth.logout(request)
    except Exception as E:
        print(E)
    Token.objects.filter(key=request.META.get("HTTP_TOKEN")).delete()
    data = {"status": 200, "data": {"message": "Logged out!"}}
    return JsonResponse(data)


@api_view(["POST"])
def Dashboard(request):

    if checkAuth(request) == 0:
        data = {"status": 403, "data": {"message": "Not Logged In!"}}
        return JsonResponse(data)

    data = {"status": 200, "data": {"message": 1}}
    return JsonResponse(data)


def verify_email(request):
    msg = ""
    err_msg = ""
    if request.method == "GET":
        try:
            token = request.GET.get("token")
            if token:
                token = Token.objects.filter(key=token).values("user_id")
                if token:
                    user_id = token[0]["user_id"]
                    User.objects.filter(id=user_id).update(is_active=1)
                    user = User.objects.get(id=user_id)
                    Token.objects.filter(user_id=user_id).delete()
                    msg = "Email verified successfully. Please login from app to continue!"
                    return render(
                        request,
                        "secret/email-confirmation.html",
                        {"msg": msg, "err_msg": err_msg},
                    )
                else:
                    err_msg = "Incorrect Token!"
                    return render(
                        request,
                        "secret/email-confirmation.html",
                        {"msg": msg, "err_msg": err_msg},
                    )
            else:
                err_msg = "Token is missing!"
                return render(
                    request,
                    "secret/email-confirmation.html",
                    {"msg": msg, "err_msg": err_msg},
                )
        except Exception as E:
            print(E)
            err_msg = E
            return render(
                request,
                "secret/email-confirmation.html",
                {"msg": msg, "err_msg": err_msg},
            )
    else:
        err_msg = "Bad Request!"
        return render(
            request, "secret/email-confirmation.html", {"msg": msg, "err_msg": err_msg}
        )


def ForgotPassword_addition(request):
    if request.method == "POST":
        p = Profile.objects.filter(onetime_token=request.POST.get("token")).first()
        if p:
            u = p.user
            npwd = request.POST.get("npwd").strip()
            cnpwd = request.POST.get("cnpwd").strip()
            if npwd == cnpwd:
                if len(npwd) > 5:
                    u.set_password(npwd)
                    u.save()
                    p.onetime_token = None
                    p.save()
                    msg = "Password Updated!"
                    data = {"status": 200, "data": {"message": msg}}
                    return JsonResponse(data)
                else:
                    err = "Length of password should be atleast 6 characters!"
                    data = {"status": 400, "data": {"message": err}}
                    return JsonResponse(data)
            else:
                err = "New password(s) didn't match!"
                data = {"status": 400, "data": {"message": err}}
                return JsonResponse(data)
        else:
            data = {
                "status": 200,
                "data": {"message": "Password reset token has expired!"},
            }
            return JsonResponse(data)
    else:
        data = {"status": 400, "data": {"message": "Invalid request!"}}
        return JsonResponse(data)

