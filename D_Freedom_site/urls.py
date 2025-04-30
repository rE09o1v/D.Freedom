from django.urls import path
from . import views

app_name = 'D_Freedom_site'

urlpatterns = [
    path('', views.index, name='index'),
    path('service/', views.service, name='service'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('contact/thanks/', views.contact_thanks, name='contact_thanks'),
    path('price/', views.price, name='price'),
    path('modeling/', views.modeling, name='modeling'),
    path('drawing/', views.drawing, name='drawing'),
    path('printing/', views.printing, name='printing'),
    path('estimate/create/', views.create_estimate, name='create_estimate'),
    path('admin-estimate/create/', views.admin_create_estimate, name='admin_create_estimate'),
    path('estimate/<int:pk>/', views.estimate_detail, name='estimate_detail'),
    path('estimate/<int:pk>/pdf/', views.download_estimate_pdf, name='download_estimate_pdf'),
] 