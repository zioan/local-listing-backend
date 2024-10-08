from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Review
from .serializers import ReviewSerializer

User = get_user_model()


class ReviewList(generics.ListCreateAPIView):
    """View for listing and creating reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return reviews for the specified reviewed user."""
        reviewed_user_id = self.kwargs['user_id']
        return Review.objects.filter(reviewed_user_id=reviewed_user_id)

    def create(self, request, *args, **kwargs):
        """Create a new review or update an existing one."""
        reviewed_user_id = self.kwargs['user_id']
        reviewed_user = User.objects.filter(id=reviewed_user_id).first()

        if not reviewed_user:
            return Response({"reviewed_user": ["User not found"]},
                            status=status.HTTP_404_NOT_FOUND)

        if reviewed_user == request.user:
            return Response({"reviewed_user": ["You cannot review yourself"]},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        existing_review = Review.objects.filter(
            reviewer=request.user, reviewed_user=reviewed_user).first()

        if existing_review:
            existing_review.rating = serializer.validated_data['rating']
            existing_review.content = serializer.validated_data['content']
            existing_review.save()
            return Response(ReviewSerializer(existing_review).data,
                            status=status.HTTP_200_OK)
        else:
            review = serializer.save(
                reviewer=request.user, reviewed_user=reviewed_user)
            return Response(ReviewSerializer(review).data,
                            status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        """Return the context for the serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a review."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the review object, ensuring the reviewer
        is the current user."""
        obj = super().get_object()
        if obj.reviewer != self.request.user:
            self.permission_denied(self.request)
        return obj

    def update(self, request, *args, **kwargs):
        """Update the specified review."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        """Perform the actual update of the review."""
        serializer.save()

    def get_serializer_context(self):
        """Return the context for the serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReviewerReviewDetail(generics.RetrieveAPIView):
    """View for retrieving a specific review by reviewer and reviewed user."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the review object for the specified reviewer
        and reviewed user."""
        reviewed_user_id = self.kwargs['user_id']
        reviewer_id = self.kwargs['reviewer_id']
        review = Review.objects.filter(
            reviewed_user_id=reviewed_user_id, reviewer_id=reviewer_id).first()
        return review

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the review, returning 204 if not found."""
        instance = self.get_object()
        if not instance:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
