from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueValidator
from django.db.models.fields import IntegerField, FloatField
from django.db.models import Q


from secret.models import Courses, CourseLevels, TimePeriods


class add_course_serializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = (
            "course_name",
            "level",
            "course_description",
            "price_per_week",
            "price_per_month"
        )

    def __init__(self, *args, **kwargs):
        super(add_course_serializer, self).__init__(*args, **kwargs)
        for fieldname in [
            "course_name",
            "level",
            "course_description",
            "price_per_week",
            "price_per_month",
        ]:
            self.fields[fieldname].required = True

    def create(self, validated_data):
        course = Courses.objects.create(**validated_data)
        return course


class course_fk_check(serializers.Serializer):
    level = serializers.IntegerField(required=True)


class edit_course_serializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = (
            "course_name",
            "course_description",
            "price_per_week",
            "price_per_month",
            "level",
        )

    def __init__(self, *args, **kwargs):
        super(edit_course_serializer, self).__init__(*args, **kwargs)
        for fieldname in [
            "course_name",
            "course_description",
            "price_per_week",
            "price_per_month",
            "level",
        ]:
            self.fields[fieldname].required = True

    def create(self, validated_data):
        course = Courses.objects.create(**validated_data)
        return course

    def update(self, instance, validated_data):
        instance.course_name = validated_data.get("course_name", instance.course_name)
        # instance.duration_value = validated_data.get('duration_value', instance.duration_value)
        instance.price_per_week = validated_data.get(
            "price_per_week", instance.price_per_week
        )
        instance.course_description = validated_data.get(
            "course_description", instance.course_description
        )
        instance.price_per_month = validated_data.get(
            "price_per_month", instance.price_per_month
        )
        # instance.duration_period = validated_data.get('duration_period', instance.duration_period)
        instance.level = validated_data.get("level", instance.level)
    

       

        instance.save()
        return instance
