from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # MCQ
    # ==========================
    path("mcq/", views.mcq_view, name="mcq"),
    path("mcq/async/", views.mcq_view_async, name="mcq_async"),
    path("download_mcq_pdf/", views.download_mcq_pdf, name="download_mcq_pdf"),
    path("store-mcqs/", views.store_mcqs_view, name="store_mcqs"), 

    # ==========================
    # SUMMARY
    # ==========================
    path("summary/", views.summary_view, name="summary"),
    path("summary/async/", views.summary_view_async, name="summary_async"),
    path("download_summary_pdf/", views.download_summary_pdf, name="download_summary_pdf"),
    path("store-summary/", views.store_summary_view, name="store_summary"),

    # ==========================
    # TUTORIAL
    # ==========================
    path("tutorial/", views.tutorial_view, name="tutorial"),
    path("tutorial/async/", views.tutorial_view_async, name="tutorial_async"),
    path("download_tutorial_pdf/", views.download_tutorial_pdf, name="download_tutorial_pdf"),
    path("store-tutorial/", views.store_tutorial_view, name="store_tutorial"),

    # ==========================
    # QUIZ
    # ==========================
    path("quiz/", views.quiz_view, name="quiz"),
    path("quiz/async/", views.quiz_view_async, name="quiz_async"),

    # ==========================
    # TASK STATUS
    # ==========================
    path("task-status/<str:task_id>/", views.task_status_view, name="task_status"),
]