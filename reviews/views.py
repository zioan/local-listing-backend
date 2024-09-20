from rest_framework import generics, permissions, serializers
from .models import Review
from .serializers import ReviewSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ReviewList(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        reviewed_user_id = self.kwargs['user_id']
        return Review.objects.filter(reviewed_user_id=reviewed_user_id)

    def perform_create(self, serializer):
        reviewed_user_id = self.kwargs['user_id']
        reviewed_user = User.objects.filter(id=reviewed_user_id).first()
        if not reviewed_user:
            raise serializers.ValidationError(
                {"reviewed_user": "User not found"})

        # Check if a review already exists
        existing_review = Review.objects.filter(
            reviewer=self.request.user, reviewed_user=reviewed_user).first()
        if existing_review:
            # Update existing review
            existing_review.rating = serializer.validated_data['rating']
            existing_review.content = serializer.validated_data['content']
            existing_review.save()
        else:
            # Create new review
            serializer.save(reviewer=self.request.user,
                            reviewed_user=reviewed_user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.reviewer != self.request.user:
            self.permission_denied(self.request)
        return obj
