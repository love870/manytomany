from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import(ValidationError)
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField,FloatField,DateField
from django.db.models import Q


from secret.models  import Courses, CourseLevels, TimePeriods, Promocodes


class add_promocodes_serializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    course_duration = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    discount_percentage    =   serializers.IntegerField(required=True, min_value=0)
    start_date = serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])
    end_date =serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])


class edit_half_promocodes_serializer(serializers.Serializer):
    start_date = serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])
    end_date =serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])


class edit_full_promocodes_serializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    course_duration = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    discount_percentage    =   serializers.IntegerField(required=True, min_value=0)
    start_date = serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])
    end_date =serializers.DateField(required=True,format="%m/%d/%Y", input_formats=['%m/%d/%Y', 'iso-8601'])
