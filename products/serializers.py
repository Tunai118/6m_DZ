from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'owner',
            'created_at',
        ]

        read_only_fields = [
            'owner',
            'created_at',
        ]