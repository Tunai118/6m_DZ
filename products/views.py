from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product
from .permissions import IsModerator
from .serializers import ProductSerializer
from .tasks import save_celery_log, send_test_email


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsModerator]


class CeleryTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', 'Celery task was started')

        task = save_celery_log.delay(message)

        return Response(
            {
                'message': 'Celery task started',
                'task_id': task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class EmailTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = send_test_email.delay(email)

        return Response(
            {
                'message': 'Email task started',
                'task_id': task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )