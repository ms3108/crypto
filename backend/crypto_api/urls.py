from django.urls import path
from . import views

urlpatterns = [
    path('crypto/', views.CryptoListView.as_view(), name='crypto-list'),
    path('crypto/<str:symbol>/', views.CryptoDetailView.as_view(), name='crypto-detail'),
    path('admin/clear-cache/', views.ClearCacheView.as_view(), name='clear-cache'),
]