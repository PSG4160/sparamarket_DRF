from rest_framework import serializers
from .models import Product, Comment

class ProductSerializer(serializers.ModelSerializer):
    '''상품 목록 조회 Serializer'''
    user = serializers.ReadOnlyField(source='user.email') # user 필드에 작성자의 이메일만 출력
    
    class Meta:
        model = Product
        fields = ('id', 'user', 'title', 'created_at', 'view_count')
        
class ProductDetailSerializer(serializers.ModelSerializer):
    '''상품 상세 조회 및 생성 Serializer'''
    user = serializers.ReadOnlyField(source='user.email') # user 필드에 작성자의 이메일만 출력
    
    class Meta:
        model = Product
        fields = ('id', 'user', 'title', 'description', 'image', 'created_at', 'updated_at', 'view_count')

class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회 및 생성 Serializer"""
    author = serializers.ReadOnlyField(source='author.email')
    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    is_liked = serializers.SerializerMethodField() #좋아요 여부
    
    class Meta:
        model = Comment
        fields = ('id', 'product', 'author', 'content', 'created_at', 'updated_at', 'like_users', 'like_count', 'is_liked')
        read_only_fields = ('product','like_users')
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like_users.filter(pk=request.user.pk).exists()
        return False