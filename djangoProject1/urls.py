"""
URL configuration for djangoProject1 project.

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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from app import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # 模板登录页面
    path('login2/', views.login2, name='login2'),
    # 模板注册页面
    path('register/', views.register, name='register'),
    # 模板用户主页
    path('index2/', views.index2, name='index2'),
    # 模板通知公告页
    path('announcements2/', views.announcements2, name='announcements2'),
    # 模板申请项目页
    path('apply_projects2/', views.apply_projects2, name='apply_projects2'),
    # 模板进度提示页面
    path('tips/', views.tips, name='tips'),
    # 模板查看进度表
    path('my_projects/', views.my_projects, name='my_projects'),
    # 模板提交中期报告页
    path('midterm_review/submit/<str:project_name>/', views.submit_midterm_review, name='submit_midterm_review'),
    # 模板查看中期报告页
    path('midterm_review/view/<str:project_name>/', views.view_midterm_review, name='view_midterm_review'),
    # 模板提交结项报告页
    path('submit_final_report/<str:project_name>/', views.submit_final_report, name='submit_final_report'),
    # 模板查看结项报告页
    path('projects/final_report/<str:project_name>/', views.view_final_report, name='view_final_report'),
    # 模板管理员主页
    path('index3/', views.index3, name='index3'),
    # 模板管理员通知公告页
    path('announcements/', views.announcement_list, name='announcement_list'),
    # 模板删除通知页面
    path('announcements/delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    # 模板发布通知页面
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    # 模板用户删除
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    # 模板立项审批页
    path('pending-projects1/', views.pending_projects1, name='pending_projects1'),
    # 模板反馈和意见
    path('submit_feedback/<str:project_name>/', views.submit_feedback, name='submit_feedback'),
    # 模板中期审批页
    path('pending-projects2/', views.pending_projects2, name='pending_projects2'),
    # 模板中期审批意见
    path('submit-review/<str:project_name>/', views.submit_review, name='submit_review'),
    # 模板结项审批页
    path('pending-projects3/', views.pending_projects3, name='pending_projects3'),
    # 模板结项审批意见
    path('update-comments/<str:project_name>/', views.update_final_report_comments,
         name='update_final_report_comments'),
    # 模板结项审批
    path('update-final-status/<str:project_name>/', views.update_final_report_status,
         name='update_final_report_status'),
    # 模板经费申请
    path('funding-application/', views.funding_application_view, name='funding_application'),
    # 模板经费审批
    path('pending-projects0/', views.pending_projects0, name='pending_projects0'),
    # 模板成果填报
    path('submit-results/', views.submit_results, name='submit_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)