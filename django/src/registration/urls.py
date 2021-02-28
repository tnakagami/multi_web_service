from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    # Top
    path('', views.TopPage.as_view(), name='top_page'),
    # Login, Logout
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.LogoutPage.as_view(), name='logout'),
    # account list
    path('accounts_page/', views.AccountsPage.as_view(), name='accounts_page'),
    # Edit account status
    path('update/<pk>/', views.UpdateUserStatus.as_view(), name='update_user_status'),
    path('delete/<pk>/', views.DeleteUserPage.as_view(), name='delete_user_page'),
    # Register user information
    path('create_user/', views.CreateUser.as_view(), name='create_user'),
    path('create_user/done/', views.CreateUserDone.as_view(), name='create_user_done'),
    path('create_user/complete/<token>/', views.CreateUserComplete.as_view(), name='create_user_complete'),
    # Update account information
    path('detail_account_info/<int:pk>/', views.DetailAccountInfo.as_view(), name='detail_account_info'),
    path('update_account_info/<int:pk>/', views.UpdateAccountInfo.as_view(), name='update_account_info'),
    path('delete_own_account/<int:pk>/', views.DeleteOwnAccount.as_view(), name='delete_own_account'),
    # Change password
    path('change_own_password/', views.ChangePssword.as_view(), name='change_own_password'),
    path('change_own_password/complete/', views.ChangePassowrdComplete.as_view(), name='password_change_complete'),
    # Reset Password
    path('reset_password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset_password/done/', views.ResetPasswordDone.as_view(), name='reset_password_done'),
    path('reset_password/confirm/<uidb64>/<token>/', views.ResetPasswordConfirm.as_view(), name='reset_password_confirm'),
    path('reset_password/complete/', views.ResetPasswordComplete.as_view(), name='reset_password_complete'),
    # Change E-mail address
    path('change_email/', views.ChangeEmail.as_view(), name='change_email'),
    path('change_email/done/', views.ChangeEmailDone.as_view(), name='change_email_done'),
    path('change_email/complete/<param>/<token>/', views.ChangeEmailComplete.as_view(), name='change_email_complete'),
]

