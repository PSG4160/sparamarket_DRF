from django.db import models
from django.conf import settings
# Create your models here.

# 상품 이미지를 저장할 경로를 생성하는 함수
def product_image_path(instance, filename):
    return f'product_images/{instance.user.username}/{filename}'

# 사용자의 등록한 상품을 저장하는 모델
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    title = models.CharField('제목', max_length=100)
    description = models.TextField('내용')
    image = models.ImageField('이미지', upload_to=product_image_path, blank=True, null=True)
    created_at = models.DateTimeField('작성일',auto_now_add=True)
    updated_at = models.DateTimeField('수정일',auto_now=True)
    view_count = models.PositiveIntegerField('조회수', default=0)  # 조회수 필드 추가

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_comments')

    def __str__(self):
        return f'{self.author} - {self.content}'