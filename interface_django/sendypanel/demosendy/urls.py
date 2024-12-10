from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # path('',views.index,name="index" ),
    path('',views.login_view,name="login" ),
    # path('',views.login_view,name="login" ),
    path('create_list/',views.create_list,name="create_list" ),
    path('create_campaign/',views.create_campaign,name="create_campaign" ),
    path('log_download/',views.log_download,name="log_download" ),
    path('all_campaign/',views.all_campaigns,name="all_campaigns" ),
    path('all_list/',views.all_list,name="all_list" ),
    path('all_templates/',views.all_templates,name="all_templates" ),
    path('create_template/',views.create_template,name="create_template" ),
    # path('custom_fields/',views.create_custom_fields,name="custom_fields" ),
    path('custom_fields/<str:list_id>/', views.create_custom_fields, name='custom_fields'),
    path('delete_list/<str:list_id>/', views.delete_list, name='delete_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list_details/<str:encrypted_list_id>/', views.list_details, name='list_details'),
    path('campaign_details/<str:campaign_ids>/', views.campaign_details, name='campaign_details'),
    path("api_consumptions/",views.api_consumption,name="api_consumptions"),
    path("logs_download/",views.logs_download,name="logs_download"),
    path("logout/",views.logout_view,name="logout"),

]