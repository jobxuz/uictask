from django.db import models
from django.contrib.auth.models import User  # authapp foydalanuvchisi bilan ishlash



class Course(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owner_courses', on_delete=models.CASCADE)
    course_users = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Lesson(models.Model):
    title = models.CharField(max_length=255)
    video = models.URLField()  # Video URL yoki file
    duration = models.PositiveIntegerField()  # Ko'rish davomiyligi (sekundlarda)
    courses = models.ManyToManyField(Course, related_name='lessons', blank=True)

    def __str__(self):
        return self.title



class LessonProgress(models.Model):
    user = models.ForeignKey(User, related_name='lesson_progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progress', on_delete=models.CASCADE)
    viewing_duration = models.PositiveIntegerField(default=0)  # Foydalanuvchi ko'rgan vaqt (sekundlarda)
    is_watched = models.BooleanField(default=False)  # "Ko'rilgan"/"Ko'rilmagan" holati
    last_viewed = models.DateTimeField(null=True, blank=True)  # Oxirgi ko'rish sanasi

    def save(self, *args, **kwargs):
        # Ko'rish davomiyligi 80% dan oshsa, "Ko'rilgan" holatini yangilang
        lesson_duration = self.lesson.duration
        if lesson_duration > 0:  # Zero duration to avoid division by zero
            if self.viewing_duration >= (lesson_duration * 0.8):
                self.is_watched = True
            else:
                self.is_watched = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

