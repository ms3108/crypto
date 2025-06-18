from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_home(request):
    return JsonResponse({
        'message': 'Crypto API is running!',
        'endpoints': {
            'crypto_list': '/api/crypto/',
            'crypto_detail': '/api/crypto/{symbol}/',
            'admin': '/api/admin/clear-cache/'
        }
    })

urlpatterns = [
    path('', api_home, name='home'),  # Add this line
    path('admin/', admin.site.urls),
    path('api/', include('crypto_api.urls')),
]