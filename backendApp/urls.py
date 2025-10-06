"""
URL configuration for backendApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from backendApp.views import book_seat, movies_list, shows_list
from .views import RegisterView, cancel_booking, get_bookings; 
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/signup/', RegisterView.as_view(), name="signup_user"),
    path('api/user/login/', TokenObtainPairView.as_view(), name="login_user"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('api/movies/', movies_list, name="list_create_movies"),
    path('api/movies/<int:movie_id>/shows/', shows_list, name="list_create_shows"),
    path('api/shows/<int:show_id>/book/', book_seat, name="book_seat"),
    path('api/bookings/<int:booking_id>/cancel/', cancel_booking, name ="cancel_booking"),
    path('api/my-bookings', get_bookings, name="get_my_bookings")
]
