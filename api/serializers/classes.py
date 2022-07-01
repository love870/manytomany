from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import(ValidationError)
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField,FloatField
from django.db.models import Q



class add_class_link_serializer(serializers.Serializer):
    class_id = serializers.IntegerField(required=True)
    class_link = serializers.CharField(required=True)
    
