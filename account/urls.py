from django.urls import path
from .views import RegisterView, WithdrawalView, LoginView, LogoutView, WhoView, EmailCodeView, EditAccountView1, EditAccountView2, TokenCheckView, FindPasswordView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView

#추가
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', RegisterView.as_view()), #회원가입
    path('withdrawal/', WithdrawalView.as_view()), #회원탈퇴
    path('login/', LoginView.as_view()), #로그인
    path('logout/',LogoutView.as_view()), #로그아웃
    path('who/', WhoView.as_view()), #사용자 조회
    path('cktoken/', TokenCheckView.as_view()), #토큰유효성검사
    path('emailcode/', EmailCodeView.as_view()), #회원가입 이메일 인증코드
    path('edit1/', EditAccountView1.as_view()),
    path('edit2/', EditAccountView2.as_view()),
    
    path('findpw/', FindPasswordView.as_view()),
    
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),name="password_reset_confirm"),
    path('password_reset_complete/', CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]