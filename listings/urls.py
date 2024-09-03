from django.urls import path
from . import views

urlpatterns = [
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

    # Listing URLs
    path('listings/', views.ListingList.as_view(), name='listing-list'),
    path('listings/<int:pk>/', views.ListingDetail.as_view(),
         name='listing-detail'),
    path('listings/<int:pk>/favorite/',
         views.ListingFavorite.as_view(), name='listing-favorite'),
    path('listings/<int:pk>/unfavorite/',
         views.ListingUnfavorite.as_view(), name='listing-unfavorite'),
    path('my-listings/', views.MyListingsView.as_view(), name='my-listings'),
]
