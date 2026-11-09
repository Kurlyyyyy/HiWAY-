from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_select_view, name='role_select'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/public/', views.public_login_view, name='public_login'),
    path('login/admin/', views.admin_login_view, name='admin_login'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('public/', views.public_dashboard_view, name='public_dashboard'),
    path('admin-desk/', views.admin_dashboard_view, name='admin_dashboard'),
    path('report/<int:pk>/', views.report_detail_view, name='report_detail'),
    path('report/new/', views.create_report_view, name='create_report'),
    path('report/<int:pk>/support/', views.support_report_view, name='support_report'),
    path('report/<int:pk>/delete/', views.delete_report_view, name='delete_report'),
    path('archive/', views.archive_view, name='archive'),
    path('archive/undo-last/', views.archive_undo_last_view, name='archive_undo_last'),
    path('archive/redo-last/', views.archive_redo_last_view, name='archive_redo_last'),
    path('report/<int:pk>/advance/', views.advance_report_status_view, name='advance_report_status'),
    path('report/<int:pk>/revert/', views.revert_report_status_view, name='revert_report_status'),
    path('report/<int:pk>/advance/', views.advance_report_status_view, name='advance_report_status'),
]