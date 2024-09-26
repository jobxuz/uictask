from rest_framework import serializers
from .models import Course, Lesson,LessonProgress
from django.contrib.auth.models import User

class CourseSerializer(serializers.ModelSerializer):
    course_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Course
        fields = ['title', 'owner', 'course_users', 'created_at']
        read_only_fields = ['owner']



class LessonSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())

    class Meta:
        model = Lesson
        fields = ['title', 'video', 'duration', 'courses']


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['viewing_duration', 'is_watched', 'last_viewed']



