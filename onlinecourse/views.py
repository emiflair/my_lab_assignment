from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Course, Enrollment, Choice, Question, Submission
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

# Logger setup
logger = logging.getLogger(__name__)

# User Registration View
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.info("New user")

        if not user_exist:
            user = User.objects.create_user(username=username, password=password,
                                            first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

# User Login View
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
    return render(request, 'onlinecourse/user_login_bootstrap.html', context)

# User Logout View
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

# Check if user is enrolled in a course
def check_if_enrolled(user, course):
    if user.id:
        return Enrollment.objects.filter(user=user, course=course).exists()
    return False

# Course List View
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            course.is_enrolled = check_if_enrolled(user, course) if user.is_authenticated else False
        return courses

# Course Detail View
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

# Enrollment View
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if user.is_authenticated and not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))

# Extract selected answers from POST data
def extract_answers(request):
    return list(map(int, request.POST.getlist('choice')))

# Submit View
def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)
    selected_ids = extract_answers(request)
    print("DEBUG: Selected choice IDs:", selected_ids)


    for choice_id in selected_ids:
        choice = Choice.objects.get(id=choice_id)
        submission.choices.add(choice)

    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))

# Exam Result View
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()

    for question in questions:
        if question.is_get_score([choice.id for choice in selected_choices]):
            total_score += question.grade

    context = {
        "course": course,
        "grade": total_score,
        "selected_choices": selected_choices,
        "user": request.user
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
