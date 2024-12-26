from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListAPIView.as_view(), name="product_list"),
    path("<int:pk>/", views.ProductDetailAPIView.as_view(), name="product_detail"),
    path('<int:product_pk>/comments/', views.CommentListCreate.as_view(), name='comments'),
    path('<int:product_pk>/comments/<int:comment_pk>/like/', views.CommentLike.as_view(), name='comment_like'),
]
