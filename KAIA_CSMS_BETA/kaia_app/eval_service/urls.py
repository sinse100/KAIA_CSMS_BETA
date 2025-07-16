from django.urls import path

from . import views

## (메모) : url과 views.py의 백엔드 처리 함수를 매핑시키는 파일

urlpatterns = [
    ## (메모) '/' 경로를 views.py의 main 함수와 매핑 
    path("", views.main, name="main"),                                                  ## (메모) / : 인덱스 페이지(메인 페이지)
    path("login/", views.login, name="login"),                                          ## (메모) /login : 로그인을 위한 URL
    path('sendcode/',views.send_code, name='send_code'),                                ## (메모) /send_code : 인증번호 발송을 위한 URL
    path('verify/',views.verify_code, name='verify_code'),                              ## (메모) /verify_code : 인증번호 검증을 위한 URL
    path('logout/',views.logout, name='logout'),                                        ## (메모) /logout : 로그아웃을 위한 URL
    path('signup/',views.signup, name='signup'),                                        ## (메모) /signup : 회원가입을 위한 URL
    path('oem_list_eval/', views.oem_list_eval, name="oem_list_eval"),                  ## (메모) /oem_list_eval : OEM사가 본인의 평가 신청 내역을 확인을 위한 URL
    path('oem_submit_eval/', views.oem_submit_eval, name="oem_submit_eval"),            ## (메모) /oem_list_eval : OEM사가 평가 항목 확인을 위한 URL
    path('oem_submit_evidence/', views.oem_submit_evidence,name="oem_submit_evidence"),  ## (메모) /oem_list_eval : 증거물 제출을 처리하는 URL
    path('evl_list_eval/',views.evl_list_eval, name='evl_list_eval'),                    ## (메모) /oem_list_eval : 평가자가 본인의 평가 신청 내역을 확인을 위한 URL
    path('show_eval_result/',views.show_eval_result, name='show_eval_result'),           
    path('checklist_evaluate/',views.checklist_evaluate, name='checklist_evaluate'),
    path('eval_result_submit/', views.eval_result_submit, name = 'eval_result_submit')
    ##path("signup_help", views.signup_help, name="signup_help")                
    ##path("about", views.about, name="about"),
     ##path("/signup", views.signup, name="signup"),
    ##path("/logout", views.logout, name="logout")
]