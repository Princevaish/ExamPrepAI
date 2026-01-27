from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from home.models import Contact
from datetime import datetime
from django.contrib import messages

@login_required
def index(request):
    context={
        "variable_name":"This is sent from views.py"
    }
    return render(request, "index.html",context)

@login_required
def about(request):
    return render(request, "about.html")

@login_required
def services(request):
    return render(request, "services.html")

@login_required
def contacts(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, subject=subject, message=message, created_at=datetime.today())
        contact.save()
        messages.success(request, 'Your message has been sent successfully!')
    return render(request, "contact.html")

@login_required
def mcq(request):
    return render(request, "mcq.html")

@login_required
def summarizer(request):
    return render(request, "summarizer.html")

@login_required
def tutorials(request):
    return render(request, "tutorials.html")

@login_required
def quiz(request):
    return render(request, "quiz.html")

@login_required
def pricing(request):
    return render(request, "pricing.html")