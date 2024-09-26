from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Course,Lesson,LessonProgress
from .serializers import CourseSerializer,LessonSerializer,LessonProgressSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Sum
from django.db import models

class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchining faqat o'zi kirish huquqiga ega bo'lgan kurslarni ko'rsatish
        return Course.objects.filter(course_users=self.request.user)

    def perform_create(self, serializer):
        # Kurs yaratilganda egasini avtomatik belgilash
        serializer.save(owner=self.request.user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchining faqat o'zi kirish huquqiga ega bo'lgan kurslarga ruxsat berish
        return Course.objects.filter(course_users=self.request.user)

    def perform_update(self, serializer):
        course = self.get_object()
        # Faqat kurs egasi kursni yangilashi mumkin
        if course.owner != self.request.user:
            raise PermissionDenied("Siz faqat o'zingizga tegishli kursni yangilashingiz mumkin.")
        serializer.save()

    def perform_destroy(self, instance):
        course = self.get_object()
        # Faqat kurs egasi kursni o'chirishi mumkin
        if course.owner != self.request.user:
            raise PermissionDenied("Siz faqat o'zingizga tegishli kursni o'chirishingiz mumkin.")
        instance.delete()



class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.all()



class LessonProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Foydalanuvchi darsni ko'rish jarayonini yangilash
        lesson_progress = serializer.save(user=self.request.user)
        return lesson_progress

class LessonProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        lesson_progress = self.get_object()
        # Foydalanuvchi ko'rgan vaqtni yangilash
        viewing_duration = self.request.data.get('viewing_duration', 0)
        lesson_progress.viewing_duration += viewing_duration

        # 80% ko'rilganligini tekshirish
        lesson_duration = lesson_progress.lesson.duration
        if lesson_progress.viewing_duration >= lesson_duration * 0.8:
            lesson_progress.is_watched = True

        lesson_progress.save()
        serializer.save()

    

class UserLessonsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchining kirish huquqi bor kurslaridan darslar
        return Lesson.objects.filter(courses__course_users=self.request.user)

    def list(self, request, *args, **kwargs):
        lessons = self.get_queryset()
        lesson_data = []
        
        for lesson in lessons:
            # Foydalanuvchining dars ko'rish progressini olish
            progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
            lesson_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'video': lesson.video,
                'duration': lesson.duration,
                'progress': {
                    'viewing_duration': progress.viewing_duration if progress else 0,
                    'is_watched': progress.is_watched if progress else False,
                }
            })
        
        return Response(lesson_data)




class ProductLessonsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Foydalanuvchining kirish huquqi bor kurslarni olish
        return Course.objects.filter(course_users=self.request.user)

    def list(self, request, *args, **kwargs):
        courses = self.get_queryset()
        course_data = []
        
        for course in courses:
            lessons = course.lessons.all()
            lesson_data = []
            for lesson in lessons:
                # Foydalanuvchining dars ko'rish progressini olish
                progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
                lesson_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'video': lesson.video,
                    'duration': lesson.duration,
                    'progress': {
                        'viewing_duration': progress.viewing_duration if progress else 0,
                        'is_watched': progress.is_watched if progress else False,
                        'last_viewed': progress.last_viewed if progress else None,
                    }
                })
            course_data.append({
                'id': course.id,
                'title': course.title,
                'owner': course.owner.username,
                'created_at': course.created_at,
                'lessons': lesson_data,
            })
        
        return Response(course_data)



class ViewedLessonsCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Barcha darslarni qaytarish
        return Lesson.objects.all()

    def get(self, request, *args, **kwargs):
        # Har bir dars uchun ko'rilgan holati va sonini hisoblash
        viewed_lessons = (
            self.get_queryset().annotate(view_count=Count('progress', filter=Q(progress__is_watched=True)))
        )

        # Natijani formatlash
        result = [
            {
                'id': lesson.id,
                'title': lesson.title,
                'view_count': lesson.view_count
            }
            for lesson in viewed_lessons
        ]

        return Response(result)


class TotalViewingTimeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Har bir dars uchun jami ko'rish vaqtini hisoblash
        total_viewing_time = (
            LessonProgress.objects.filter(is_watched=True)
            .aggregate(total_time=Sum('viewing_duration'))['total_time'] or 0
        )

        return Response({'total_viewing_time': total_viewing_time})