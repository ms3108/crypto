from django.shortcuts import render

# Create your views here.
import requests
import json
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pybreaker import CircuitBreaker

# Circuit Breaker Configuration
breaker = CircuitBreaker(fail_max=3, reset_timeout=60)


class CryptoService:
    BINANCE_URL = "https://api4.binance.com/api/v3/ticker/24hr"
    CACHE_TIMEOUT = 120  # 2 minutes

    @staticmethod
    @breaker
    def fetch_binance_data(symbol=None):
        """Fetch data from Binance API with circuit breaker"""
        url = CryptoService.BINANCE_URL
        params = {'symbol': symbol} if symbol else {}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_crypto_data(symbol):
        """Get crypto data with caching"""
        cache_key = f"crypto_{symbol}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data, True

        try:
            data = CryptoService.fetch_binance_data(symbol)
            cache.set(cache_key, data, CryptoService.CACHE_TIMEOUT)
            return data, False
        except Exception as e:
            # Try to return stale cached data
            stale_data = cache.get(cache_key + "_stale")
            if stale_data:
                return stale_data, True
            raise e

    @staticmethod
    def get_crypto_list():
        """Get list of popular crypto pairs"""
        cache_key = "crypto_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data, True

        try:
            # Get top 20 by volume
            data = CryptoService.fetch_binance_data()
            # Filter USDT pairs and sort by volume
            usdt_pairs = [item for item in data if item['symbol'].endswith('USDT')]
            top_pairs = sorted(usdt_pairs, key=lambda x: float(x['volume']), reverse=True)[:20]

            cache.set(cache_key, top_pairs, CryptoService.CACHE_TIMEOUT)
            return top_pairs, False
        except Exception as e:
            stale_data = cache.get(cache_key + "_stale")
            if stale_data:
                return stale_data, True
            raise e


class CryptoDetailView(APIView):
    """Get 24hr stats for a specific crypto symbol"""

    def get(self, request, symbol):
        try:
            data, from_cache = CryptoService.get_crypto_data(symbol.upper())

            response_data = {
                'symbol': data['symbol'],
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChange']),
                'change_percent_24h': float(data['priceChangePercent']),
                'volume_24h': float(data['volume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'from_cache': from_cache,
                'circuit_breaker_state': breaker.current_state
            }

            return Response(response_data)

        except requests.exceptions.RequestException:
            return Response(
                {'error': 'Failed to fetch data from Binance API', 'circuit_breaker_state': breaker.current_state},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CryptoListView(APIView):
    """Get list of popular crypto pairs"""

    def get(self, request):
        try:
            data, from_cache = CryptoService.get_crypto_list()

            crypto_list = []
            for item in data:
                crypto_list.append({
                    'symbol': item['symbol'],
                    'price': float(item['lastPrice']),
                    'change_percent_24h': float(item['priceChangePercent']),
                    'volume_24h': float(item['volume'])
                })

            response_data = {
                'count': len(crypto_list),
                'from_cache': from_cache,
                'circuit_breaker_state': breaker.current_state,
                'results': crypto_list
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': str(e), 'circuit_breaker_state': breaker.current_state},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ClearCacheView(APIView):
    """Admin endpoint to clear cache"""

    def post(self, request):
        try:
            cache.clear()
            breaker.reset()
            return Response({'message': 'Cache cleared and circuit breaker reset'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)