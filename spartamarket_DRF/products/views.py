from django.shortcuts import get_object_or_404
from .models import Product, Comment
from rest_framework.views import APIView
from .serializers import ProductSerializer, ProductDetailSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from django.core.cache import cache
# Create your views here.


class ProductListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly] # 로그인 안하면 읽기만 된다(GET)

    def get(self, request):
        ''' 상품 목록 조회'''
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        ''' 상품 게시글 생성'''
        serializer = ProductDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user = request.user) # Product 모델의 user필드와 요청 user
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)
    
    def get(self, request, pk):
        product = self.get_object(pk)
        
        # 로그인한 사용자이고 작성자가 아닌 경우에만 조회수 증가 처리
        # 24시간 동안 같은 IP에서 같은 게시글 조회 시 조회수가 증가하지 않음
        if request.user != product.user:
            # 해당 사용자의 IP와 게시글 ID로 캐시 키를 생성
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{pk}"
            
            # 캐시에 없는 경우에만 조회수 증가
            if not cache.get(cache_key):
                product.view_count += 1
                product.save()
                # 캐시 저장 (24시간 유효)
                # cache.set(cache_key, True, 60*60*24)
                cache.set(cache_key, True, 5)

        # product.view_count += 1
        # product.save()

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    
    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductDetailSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        
    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        data = {"pk": f"{pk} is deleted."}
        return Response(data, status=status.HTTP_200_OK)
    
class CommentListCreate(APIView):

    def get_product(self, product_pk):
        return get_object_or_404(Product, pk=product_pk)

    def get(self, request, product_pk):
        """댓글 목록 조회"""
        product = self.get_product(product_pk)
        comments = product.comments.all() # 역참조
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, product_pk):
        """댓글 생성"""
        product = self.get_product(product_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentLike(APIView):

    def get_product(self, product_pk):
        return get_object_or_404(Product, pk=product_pk)

    def get_comment(self, product, comment_pk):
        return get_object_or_404(Comment, pk=comment_pk, product=product)

    def post(self, request, product_pk, comment_pk):
        """댓글 좋아요 토글"""
        product = self.get_product(product_pk)
        comment = self.get_comment(product, comment_pk)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        if comment.like_users.filter(pk=user.pk).exists():
            # 좋아요 취소
            comment.like_users.remove(user)
            message = "댓글 좋아요가 취소되었습니다."
        else:
            # 좋아요 추가
            comment.like_users.add(user)
            message = "댓글을 좋아요 했습니다."

        # 댓글 정보를 시리얼라이저를 통해 반환
        serializer = CommentSerializer(comment, context={'request': request})

        return Response({
            'message': message,
            'comment': serializer.data
        }, status=status.HTTP_200_OK)