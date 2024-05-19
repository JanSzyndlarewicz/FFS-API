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
from Server.views import upload_file, get_download_link, get_csrf_token, login_view, logout_view, register_view, \
    get_user_files

"""
ATTENTION!
IF YOUR REQUESTS ARE NOT WORKING, PLEASE MAKE SURE YOU HAVE CSRF TOKEN IN YOUR HEADERS.
YOU CAN GET IT BY SENDING A GET REQUEST TO '/getcsrf/' ENDPOINT.
ONCE YOU HAVE THE TOKEN, YOU CAN ADD IT TO YOUR HEADERS IN YOUR REQUESTS.
X-CSRFToken: <your_token>

How to use our insane Django API:
1. To upload a file wiht upload_file endpoint
In body of the request you have to add key 'file' of file with file to upload as a value
In headers you can add key 'password' with password as a value. 
In case of password-protected file, you will need to provide this password to download the file.
Otherwise, the file will be available for download without a password.
After successful upload you will get JSON response with URL to download the file '/download/<file_id>/'

2. To download a file with get_download_link endpoint
You have to provide file_id in URL. This file_id is the access_token of the file. 
If the file is password-protected, you will need to provide the password in the headers.
After successful download you will get the file.
"""


urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('download/<str:file_id>/', get_download_link, name='download_file'),
    path('getcsrf/', get_csrf_token, name='get_token'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('user_files/', get_user_files, name='user_files'),
]
