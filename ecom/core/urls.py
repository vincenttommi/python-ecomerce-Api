from  django.urls import path
from . import views



urlpatterns = [
    path('register/',views.RegisterUser.as_view(), name='RegisterUser'),
    path('verify/', views.VerifyuserEmail.as_view(), name='VerifyuserEmail'),
    path('login/', views.LoginView.as_view(), name='LoginView'),
    path('logout/', views.LogoutUserView.as_view(), name='LoginView'),
    
  
    
    
   
    
]
