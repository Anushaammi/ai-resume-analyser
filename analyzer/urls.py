from django.urls import path
from . import views


urlpatterns = [

    # Home / Resume Analysis
    path(
        '',
        views.home,
        name='home'
    ),

    # Authentication
    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    # Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # Profile
    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    # Resume History
    path(
        'history/',
        views.resume_history,
        name='history'
    ),

    # Resume Details
    path(
        'history/details/<int:id>/',
        views.resume_details,
        name='resume_details'
    ),

    # Download PDF Report
    path(
        'history/download/<int:id>/',
        views.download_report,
        name='download_report'
    ),

    # Delete Resume History
    path(
        'history/delete/<int:id>/',
        views.delete_history,
        name='delete_history'
    ),
]