from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/reviews/',
         views.ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(),
         name='review-detail'),
    path('users/<int:user_id>/reviewer/<int:reviewer_id>/',
         views.ReviewerReviewDetail.as_view(), name='reviewer-review-detail'),
]
