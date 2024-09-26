from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    LessonListCreateView,
    LessonDetailView,
    LessonProgressListCreateView,
    LessonProgressDetailView,
    UserLessonsView,
    ProductLessonsView,
    ViewedLessonsCountView,
    TotalViewingTimeView
    

)




urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('progress/', LessonProgressListCreateView.as_view(), name='lesson-progress-list-create'),
    path('progress/<int:pk>/', LessonProgressDetailView.as_view(), name='lesson-progress-detail'),
    path('lessons/all/', UserLessonsView.as_view(), name='user-lessons'),
    path('products/<int:product_id>/lessons/', ProductLessonsView.as_view(), name='product-lessons'),
    path('lessons/viewed-count/', ViewedLessonsCountView.as_view(), name='viewed-lessons-count'),
    path('lessons/total-viewing-time/', TotalViewingTimeView.as_view(), name='total-viewing-time'),


]
