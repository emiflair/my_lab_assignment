from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Enrollment, Question, Choice, Submission

# Inline admin for related models
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 2

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

# Admin configuration for Course model
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

# Admin configuration for Question model
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content']

# Admin configuration for Lesson model
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

# Registering models with Django admin
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Enrollment)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
