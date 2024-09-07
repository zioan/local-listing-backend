from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'listings', views.ListingViewSet)

urlpatterns = [
    # Router URLs (for ListingViewSet)
    path('', include(router.urls)),

    # Category URLs
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(),
         name='category-detail'),

    # Subcategory URLs
    path('subcategories/', views.SubcategoryList.as_view(),
         name='subcategory-list'),
    path('subcategories/<int:pk>/', views.SubcategoryDetail.as_view(),
         name='subcategory-detail'),
    path('subcategories/by-category/<int:category_id>/',
         views.SubcategoryByCategory.as_view(),
         name='subcategory-by-category'),

    # My Listings URL
    path('my-listings/', views.MyListingsView.as_view(), name='my-listings'),

    # Favorite Listings URLs
    path('favorites/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('listings/<int:pk>/favorite/',
         views.FavoriteToggleView.as_view(), name='favorite-toggle'),
]
