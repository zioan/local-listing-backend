from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ListingSitemap

sitemaps = {
    'listings': ListingSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/listings/', include('listings.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
