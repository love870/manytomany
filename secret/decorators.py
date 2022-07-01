from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.shortcuts import render,redirect

def my_login_required(function):
   def wrap(request, *args, **kwargs):
      if request.session['name'] :
         return function(request, *args, **kwargs)
      else:
         return render(request, 'secret/login.html')
         raise PermissionDenied
   wrap.__doc__ = function.__doc__
   wrap.__name__ = function.__name__   
   return wrap



def superadmin_required(function):
   def wrap(request, *args, **kwargs):
      if request.session['role'] == "SuperAdmin":
         return function(request, *args, **kwargs)
      else:
         raise PermissionDenied
   wrap.__doc__ = function.__doc__
   wrap.__name__ = function.__name__   
   return wrap