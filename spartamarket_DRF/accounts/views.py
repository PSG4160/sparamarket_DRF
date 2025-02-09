from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import SignupSerializer, UserUpdateSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

User = get_user_model()
# Create your views here.
@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시 / AllowAny 없어도 똑같이 동작함.
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message" : "회원가입이 성공적으로 완료되었습니다."
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    print(email)
    print(password)
    # 사용자 인증
    user = authenticate(request, email=email, password=password)
    if user is not None:
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': '로그인 성공'
        }, status=200)
    else:
        return JsonResponse({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=400)

@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시
def logout(request):
    print('---')
    try:
        refresh_token = request.data.get("refresh")
        print(refresh_token)
        token = RefreshToken(refresh_token)
        print(token)
        token.blacklist()
        print('---')
        return Response({"message": "로그아웃 성공"})
    except Exception:
        return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET', 'PUT', 'PATCH'])
def profile(request):
    user = request.user  # JWT 인증을 통해 얻은 현재 사용자
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=200)
    
    if request.method in ('PUT', 'PATCH') :
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)  # partial=True로 일부 업데이트 허용

        if serializer.is_valid():
            serializer.save()  # 수정 내용 저장
            return Response({
                "message": "회원정보가 성공적으로 수정되었습니다.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def follow(request, user_pk):
    profile_user = get_object_or_404(User, pk=user_pk)
    me = request.user
    
    if me == profile_user:
        return Response({'error': '자기 자신을 팔로우할 수 없습니다.'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    if me.followings.filter(pk=profile_user.pk).exists():
        me.followings.remove(profile_user)
        is_followed = False
        message = f'{profile_user.email}님 팔로우를 취소했습니다.'
    else:
        me.followings.add(profile_user)
        is_followed = True
        message = f'{profile_user.email}님을 팔로우했습니다.'

    return Response({
        'is_followed': is_followed,
        'message': message,
    }, status=status.HTTP_200_OK)