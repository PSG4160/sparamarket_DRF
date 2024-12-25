from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            'title': {'required': True},  # 제목 필수
            'description': {'required': True},  # 내용 필수
            'image': {'required': True},  # 상품 이미지 필수
        }
        
class ProductDetailSerializer(ProductSerializer):
    pass