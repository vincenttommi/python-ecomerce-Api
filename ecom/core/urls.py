from  django.urls import path
from . import views



urlpatterns = [
    path('register/',views.RegisterUser.as_view(), name='RegisterUser'),
    path('verify/', views.VerifyUserEmail.as_view(), name='VerifyuserEmail'),
    path('login/', views.LoginView.as_view(), name='LoginView'),
    path('logout/', views.LogoutUserView.as_view(), name='LoginView'),
    path('password-reset-request/', views.PasswordResetRequest.as_view(), name='verify'),
    path('password-reset-confrim/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', views.SetNewPassword.as_view(), name='set-new-password'),
    # path('create-product/', views.CreateProductView.as_view(), name='create-product'),
   
]
