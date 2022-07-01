from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import(ValidationError)
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField,FloatField
from django.db.models import Q



class add_order_serializer(serializers.Serializer):
    grand_total_amt = serializers.FloatField(required=True)
    course_id = serializers.IntegerField(required=True)
    course_price = serializers.FloatField(required=True)
    course_duration =serializers.CharField(required=True)
    selected_date=serializers.DateTimeField(required=True)


class add_child_serializer(serializers.Serializer):
    child_name =serializers.CharField(required=True)
    child_age = serializers.IntegerField(required=True)
    child_grade = serializers.CharField(required=True)
    child_interests = serializers.CharField(required=True)
