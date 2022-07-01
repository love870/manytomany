from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import(ValidationError)
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField,FloatField
from django.db.models import Q




class add_user_serializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email    =    serializers.EmailField(required=True)
    phone = serializers.IntegerField(required=True, max_value=None, min_value=None)
    
   


class api_register(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email    =    serializers.EmailField(required=True)
    phone = serializers.IntegerField(required=True, max_value=None, min_value=None)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    device_token=serializers.CharField(required=True)
   


class edit_user_serializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
