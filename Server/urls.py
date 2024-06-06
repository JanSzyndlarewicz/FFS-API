"""
URL configuration for Server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from Server.views.auth_views import login_user, logout_user, register_user, session_info
from Server.views.bin_views import recover_file, get_files_in_bin, put_file_in_bin
from Server.views.file_views import file_view, get_user_filenames, get_user_files
from Server.views.share_views import share_view
from Server.views.utils_views import get_csrf_token


urlpatterns = [
    path('file/', file_view, name='file_operations'),
    path('file/<str:access_token>/', file_view, name='file_operations_with_token'),
    path('file/bin/all/', get_files_in_bin, name='get_files_in_bin'),
    path('file/bin/<str:access_token>/', put_file_in_bin, name='put_file_in_bin'),
    path('file/bin/restore/<str:access_token>/', recover_file, name='restore_file_from_bin'),
    path('getcsrf/', get_csrf_token, name='get_csrf_token'),
    path('session_info/', session_info, name='get_session_info'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),
    path('user_filenames/', get_user_filenames, name='get_user_filenames'),
    path('user_files/', get_user_files, name='get_user_files'),
    path('share/<str:access_token>/<str:shared_with>/', share_view, name='share_file_with_user'),
    path('share/<str:access_token>/', share_view, name='make_file_private'),
    path('share/', share_view, name='get_shared_files'),
]
