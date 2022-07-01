from django.shortcuts import render
from api.models import Profile

# Create your views here.
def Home(request):
    return render(request, 'frontend/index.html',{"user":request.user});

def ForgotPassword(request):
    return render(request, 'frontend/forgot-password.html',{"user":request.user});

def ResetPassword(request,token):
    p = Profile.objects.filter(onetime_token=token).first()
    if p:
        return render(request, 'frontend/reset-password.html',{"user":p.user,"token":token})
    else:
        return render(request, 'frontend/reset-password.html',{"user":None,"token":token})
