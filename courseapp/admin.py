from django.contrib import admin
from  .models import Course,Lesson,LessonProgress

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
