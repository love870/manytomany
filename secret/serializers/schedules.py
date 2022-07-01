from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import(ValidationError)
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField,FloatField
from django.db.models import Q


from secret.models  import Course_Schedules, Class_Schedules


class add_course_schedule_serializer(serializers.ModelSerializer):
    class Meta: 
        model=Course_Schedules
        fields=('day_of_week','course_id','start_time','end_time')  


    def __init__(self, *args, **kwargs):
        super(add_course_schedule_serializer, self).__init__(*args, **kwargs)
        for fieldname in ['day_of_week','course_id','start_time','end_time']:
            self.fields[fieldname].required = True
   
    def create(self, validated_data):
        course_schedule = Course_Schedules.objects.create(**validated_data)
        return course_schedule

class add_class_schedule_serializer(serializers.ModelSerializer):
    class Meta: 
        model=Class_Schedules
        fields=('day_of_week','class_id','start_time','end_time')  


    def __init__(self, *args, **kwargs):
        super(add_class_schedule_serializer, self).__init__(*args, **kwargs)
        for fieldname in ['day_of_week','class_id','start_time','end_time']:
            self.fields[fieldname].required = True
   
    def create(self, validated_data):
        print(validated_data, "validae")
        class_schedule = Class_Schedules.objects.create(**validated_data)
        print(class_schedule, "course_schedule")
        return class_schedule