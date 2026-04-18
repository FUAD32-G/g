from django.urls import path
from .views import *

urlpatterns = [
    path('', redirect_dashboard, name='redirect_dashboard'),

    path('reception/', reception_dashboard, name='reception_dashboard'),
    path('upload1/', upload1_dashboard, name='upload1_dashboard'),
    path('upload2/', upload2_dashboard, name='upload2_dashboard'),
    path('submission/', submission_dashboard, name='submission_dashboard'),
    path('tax/', tax_dashboard, name='tax_dashboard'),
    path('finance/', finance_dashboard, name='finance_dashboard'),
    path('owner/', main_dashboard, name='main_dashboard'),
    path('create-case/', create_case, name='create_case'),
    path('complete-task/<int:task_id>/', complete_task, name='complete_task'),
]
