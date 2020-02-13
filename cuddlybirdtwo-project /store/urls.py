from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('product/<slug:slug>/', views.SingleProduct.as_view(), name='product'),
    path('features/', views.FeaturesPage.as_view(), name='features'),
]
