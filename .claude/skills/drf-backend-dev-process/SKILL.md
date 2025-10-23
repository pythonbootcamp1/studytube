---
name: drf-backend-dev-process
description: Django REST Framework 백엔드 개발을 위한 단계별 프로세스 가이드. JWT 인증, 파일 스트리밍, 소셜 기능, 통계 분석을 포함한 프로덕션 수준의 API 개발 시 사용. 사용자 요구사항 수집부터 테스트까지 체계적인 개발 워크플로우 제공.
---

# DRF Backend Development Process

Django REST Framework(DRF) 기반 백엔드 개발을 단계별로 진행하기 위한 종합 가이드입니다. 각 단계를 완료한 후 사용자의 테스트와 승인을 받아 다음 단계로 진행합니다.

## 핵심 원칙

### 개발 철학
- **API 문서 우선 개발**: drf-spectacular를 통한 OpenAPI 문서 기반 개발
- **다층 검증 시스템**: Model Validator → Serializer → View 단계별 검증
- **단계별 승인 프로세스**: 각 단계 완료 시 사용자 테스트 및 승인 필수
- **도메인 기반 설계**: 요구사항에 따른 명확한 앱 분리
- **최신 기술 스택**: 패키지 최신 버전 우선 적용

### 기술 스택
- **IDE**: Cursor (AI 기반 코드 에디터)
- **API 테스트**: Swagger UI (drf-spectacular)
- **데이터베이스**: 
  - 개발: SQLite
  - 프로덕션: PostgreSQL
- **환경 관리**: python-dotenv
- **인증**: JWT (djangorestframework-simplejwt)

### 핵심 기능
- JWT 인증 시스템
- 파일 업로드 및 스트리밍 (이미지, 음원, 동영상)
- 소셜 기능 (좋아요, 구독, 팔로우, 댓글)
- 통계 및 분석
- 다층 검증 시스템
- 세밀한 권한 관리

## 개발 흐름 (Development Flow)
```
Phase 1: 프로젝트 초기화
  1.1 요구사항 수집 → 1.2 앱 구조 설계 → 1.3 환경 설정
  ↓ [사용자 승인: 프로젝트 구조, Swagger 접근]

Phase 2: 데이터베이스 설계
  2.1 ERD 설계 → 2.2 모델 구현 (Validator 포함) → 2.3 Admin 커스터마이징
  ↓ [사용자 테스트: Admin 패널, 데이터 CRUD]

Phase 3: 인증 시스템
  3.1 User 모델 → 3.2 JWT 설정 → 3.3 인증 API
  ↓ [사용자 테스트: 회원가입, 로그인, 토큰]

Phase 4: 핵심 API
  4.1 Serializer (검증 포함) → 4.2 ViewSet → 4.3 라우팅
  ↓ [사용자 테스트: CRUD 작동]

Phase 5: 파일 처리
  5.1 파일 업로드 → 5.2 스트리밍 구현 → 5.3 썸네일 생성
  ↓ [사용자 테스트: 파일 업로드, 스트리밍 재생]

Phase 6: 소셜 기능
  6.1 좋아요 → 6.2 팔로우 → 6.3 댓글
  ↓ [사용자 테스트: 소셜 인터랙션]

Phase 7: 권한 관리
  7.1 기본 권한 → 7.2 객체 레벨 권한 → 7.3 커스텀 권한
  ↓ [사용자 테스트: 권한별 접근 제어]

Phase 8: 검색 및 필터링
  8.1 필터링 → 8.2 검색 → 8.3 정렬
  ↓ [사용자 테스트: 검색 정확도]

Phase 9: 통계 시스템
  9.1 기본 통계 → 9.2 집계 쿼리 → 9.3 통계 API
  ↓ [사용자 테스트: 통계 데이터 정확성]

Phase 10: 최적화
  10.1 쿼리 최적화 → 10.2 인덱스 → 10.3 성능 테스트
  ↓ [사용자 테스트: 응답 속도]

Phase 11: 테스트
  11.1 단위 테스트 → 11.2 통합 테스트
  ↓ [사용자 확인: 테스트 커버리지]

Phase 12: PostgreSQL 전환
  12.1 설정 → 12.2 마이그레이션 → 12.3 검증
  ↓ [프로덕션 준비 완료]
```

## Phase 1: 프로젝트 초기화

### 1.1 요구사항 수집

**목표**: 프로젝트 범위 명확화 및 앱 구조 설계

**작업 프로세스**:
1. 사용자와 상세 인터뷰 진행
2. 기능 요구사항 문서화
3. 앱 분리 전략 수립
4. API 엔드포인트 초안 작성

**질문 체크리스트**:
- 사용자 역할 구분? (일반/프리미엄/크리에이터/관리자)
- 콘텐츠 타입? (텍스트/이미지/음원/동영상)
- 소셜 기능 범위? (좋아요/댓글/팔로우/공유)
- 검색 기능 범위? (제목/내용/태그/사용자)
- 통계 요구사항? (실시간/일간/주간/월간)
- 파일 제한? (크기/형식/길이)
- 공개 범위 설정? (전체/팔로워/비공개)

**앱 분리 전략**:

기본 구조 (소규모):
```
accounts  - 사용자 인증 및 프로필
posts     - 게시글 관리
media     - 파일 업로드 및 스트리밍
social    - 좋아요, 팔로우, 댓글
```

확장 구조 (중대규모):
```
accounts      - 사용자 계정
profiles      - 프로필 관리
posts         - 게시글
media         - 미디어 파일
comments      - 댓글 시스템
likes         - 좋아요
follows       - 팔로우/구독
notifications - 알림 (선택)
analytics     - 통계 및 분석
tags          - 태그 시스템 (선택)
```

**완료 기준**:
- [ ] 요구사항 문서 작성 완료
- [ ] 앱 구조 다이어그램 완료
- [ ] API 엔드포인트 목록 완료
- [ ] 우선순위 설정 완료

**사용자 승인 요청**:
```
📋 검토 요청:

1. 앱 구조
   [제시한 앱 구조]
   
   적절한가요? 추가/변경 필요한 앱이 있나요?

2. API 엔드포인트
   [엔드포인트 목록]
   
   필요한 API가 모두 포함되었나요?

3. 우선순위
   MVP: [기능 목록]
   Phase 2: [기능 목록]
   
   우선순위가 적절한가요?

승인 시 다음 단계로 진행하겠습니다.
```

---

### 1.2 환경 설정 및 API 문서 초기화

**목표**: 개발 환경 구축 및 Swagger UI 세팅

**필수 패키지** (requirements.txt):
```
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
drf-spectacular==0.27.1
python-dotenv==1.0.1
django-cors-headers==4.3.1
django-filter==23.5
Pillow==10.2.0
psycopg2-binary==2.9.9
django-ratelimit==4.1.0
pytest==7.4.4
pytest-django==4.7.0
pytest-cov==4.1.0
```

**환경 변수 템플릿** (.env.example):
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1

CORS_ALLOWED_ORIGINS=http://localhost:3000

MAX_IMAGE_SIZE=5
MAX_AUDIO_SIZE=50
MAX_VIDEO_SIZE=200
```

**Bash 명령어 (사용자 실행)**:
```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Django 프로젝트 생성
django-admin startproject config .

# 4. 앱 생성
python manage.py startapp accounts
python manage.py startapp posts
# ... 기타 앱

# 5. 초기 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 6. 슈퍼유저 생성
python manage.py createsuperuser
```

**완료 기준**:
- [ ] 프로젝트 구조 생성 완료
- [ ] 패키지 설치 완료
- [ ] .env 파일 설정 완료
- [ ] 초기 마이그레이션 완료
- [ ] 슈퍼유저 생성 완료

**사용자 테스트 방법**:
```
🧪 환경 설정 테스트:

터미널에서 실행:
python manage.py runserver

접속 확인:
✅ http://127.0.0.1:8000/ - 서버 실행
✅ http://127.0.0.1:8000/admin/ - Admin 로그인
✅ http://127.0.0.1:8000/api/schema/swagger-ui/ - Swagger UI

모두 정상이면 승인해주세요.
```

---

## Phase 2: 데이터베이스 설계

### 2.1 ERD 설계

**목표**: 확장 가능한 데이터 구조 설계

**핵심 엔티티**:
- User: 사용자 (프로필 이미지 포함)
- Post: 게시글
- Media: 미디어 파일 (이미지/음원/동영상)
- Like: 좋아요
- Follow: 팔로우/구독
- Comment: 댓글
- Tag: 태그 (선택)

**관계 정의**:
- User ↔ Post: 1:N
- Post ↔ Media: 1:N
- User ↔ Like ↔ Post: M:N
- User ↔ Follow ↔ User: M:N (Self-referential)
- Post ↔ Comment: 1:N
- Comment ↔ Comment: 1:N (대댓글)

**인덱스 전략**:
- User: username, email, created_at
- Post: author_id + created_at, is_public + created_at
- Like: user_id + created_at, post_id
- Follow: follower_id, following_id

**사용자 승인 요청**:
```
📊 ERD 검토:

[ERD 다이어그램 제시]

1. 비즈니스 로직을 정확히 반영하나요?
2. 빠진 엔티티/속성이 있나요?
3. 관계 설정이 적절한가요?
4. 확장 가능한 구조인가요?

승인 시 모델 구현을 시작합니다.
```

---

### 2.2 모델 구현 (Validator 포함)

**목표**: Django 모델 구현 및 Model-level Validation

**핵심 구현 사항**:
1. **Custom User 모델**
   - AbstractUser 상속
   - profile_image (FileField + Validator)
   - bio, is_verified
   - 통계 필드 (followers_count, following_count, posts_count)
   - clean() 메서드로 모델 레벨 검증

2. **Post 모델**
   - author (ForeignKey → User)
   - title, content (MinLengthValidator)
   - is_public
   - 통계 필드 (view_count, likes_count, comments_count)
   - 금지어 검사 (clean())

3. **Media 모델**
   - post (ForeignKey → Post)
   - media_type (image/audio/video)
   - file (FileField)
   - 파일 크기/확장자 검증 (clean())
   - 메타데이터 자동 저장 (file_size, mime_type, duration)
   - 썸네일 자동 생성

4. **Like 모델**
   - user, post (unique_together)
   - 중복 방지
   - 좋아요 수 자동 증가/감소 (Signal)

5. **Follow 모델**
   - follower, following (unique_together)
   - 자기 자신 팔로우 방지 (clean())
   - 팔로워/팔로잉 수 자동 증가/감소

6. **Comment 모델**
   - post, author, parent (대댓글)
   - 대댓글 깊이 제한 (clean())
   - 댓글 수 자동 증가/감소

**Validator 패턴**:
```python
# Model-level Validation
def clean(self):
    super().clean()
    # 검증 로직
    if condition:
        raise ValidationError('에러 메시지')

def save(self, *args, **kwargs):
    self.full_clean()  # 검증 실행
    super().save(*args, **kwargs)
```

**Bash 명령어**:
```bash
# settings.py에 AUTH_USER_MODEL 설정 후
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # 재생성
```

**사용자 테스트**:
```
🧪 모델 테스트:

Admin 패널 접속: http://127.0.0.1:8000/admin/

확인 사항:
✅ 모든 모델이 표시되나요?
✅ 데이터 생성이 가능한가요?
✅ Validator가 작동하나요?
   - 큰 파일 업로드 시 에러
   - 금지어 입력 시 에러
   - 자기 자신 팔로우 시 에러
✅ 관계가 정상 작동하나요?

테스트 데이터 생성:
- 사용자 2-3명
- 게시글 2-3개
- 미디어 파일 업로드

승인 시 다음 단계로 진행합니다.
```

---

### 2.3 Admin 커스터마이징

**목표**: 효율적인 데이터 관리 인터페이스

**구현 사항**:
- list_display: 목록에 표시할 필드
- list_filter: 필터링 옵션
- search_fields: 검색 필드
- readonly_fields: 읽기 전용 필드
- fieldsets: 필드 그룹화
- actions: 커스텀 액션
- 이미지 미리보기

**완료 기준**:
- [ ] 모든 모델 Admin 등록 완료
- [ ] 검색/필터링 동작 확인
- [ ] 이미지 미리보기 표시
- [ ] 커스텀 액션 동작 확인

---

## Phase 3: JWT 인증 시스템

### 3.1 JWT 설정

**목표**: Token 기반 인증 시스템 구축

**settings.py 설정**:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### 3.2 인증 API 구현

**Serializer** (accounts/serializers.py):
- UserSerializer
- UserRegistrationSerializer (비밀번호 검증)
- UserProfileSerializer
- CustomTokenObtainPairSerializer

**ViewSet** (accounts/views.py):
- RegisterView (POST)
- CustomTokenObtainPairView (POST)
- TokenRefreshView (POST)
- ProfileView (GET, PATCH)
- ChangePasswordView (POST)

**URL 설정**:
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
GET  /api/auth/profile/
PATCH /api/auth/profile/
POST /api/auth/password/change/
```

**Swagger 문서화**:
- @extend_schema 데코레이터
- 요청/응답 예시
- 에러 응답 정의

**사용자 테스트**:
```
🧪 인증 API 테스트:

Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

1. 회원가입 (/api/auth/register/)
   ✅ 정상 회원가입 성공
   ✅ 중복 이메일 에러
   ✅ 약한 비밀번호 에러

2. 로그인 (/api/auth/login/)
   ✅ access/refresh 토큰 발급
   ✅ 잘못된 비밀번호 에러

3. 프로필 조회 (/api/auth/profile/)
   ✅ 토큰으로 인증 성공
   ✅ 토큰 없이 401 에러

4. 프로필 수정
   ✅ 프로필 이미지 업로드
   ✅ bio 수정

승인 시 다음 단계로 진행합니다.
```

---

## Phase 4: 핵심 API 개발

### 4.1 Serializer (검증 포함)

**목표**: 데이터 직렬화 및 Serializer-level Validation

**검증 계층**:
1. **Field-level Validation**
```python
   def validate_title(self, value):
       if len(value) < 2:
           raise serializers.ValidationError('제목은 2자 이상')
       return value
```

2. **Object-level Validation**
```python
   def validate(self, attrs):
       # 여러 필드 간 검증
       return attrs
```

3. **Custom Validators**
```python
   def validate_no_spam(value):
       if 'spam' in value.lower():
           raise serializers.ValidationError('스팸 키워드 포함')
```

**구현 Serializer**:
- PostListSerializer (목록용)
- PostDetailSerializer (상세용)
- PostCreateSerializer (생성용)
- PostUpdateSerializer (수정용)
- MediaSerializer

### 4.2 ViewSet 구현

**목표**: RESTful API 엔드포인트 구현

**핵심 구현**:
- ModelViewSet 사용
- get_queryset() 오버라이드 (쿼리 최적화)
- get_serializer_class() (상황별 Serializer)
- perform_create() (작성자 자동 설정)
- @action 데코레이터 (커스텀 액션)

**쿼리 최적화**:
```python
def get_queryset(self):
    return Post.objects.select_related(
        'author'
    ).prefetch_related(
        'media_files', 'likes'
    )
```

### 4.3 라우팅

**Router 설정**:
```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('posts', PostViewSet)
```

**사용자 테스트**:
```
🧪 CRUD API 테스트:

Swagger UI에서:

1. 게시글 목록 (GET /api/posts/)
   ✅ 페이지네이션 동작
   ✅ 작성자 정보 포함

2. 게시글 생성 (POST /api/posts/)
   ✅ 인증 필요
   ✅ Validation 에러 표시
   ✅ 생성 성공

3. 게시글 상세 (GET /api/posts/{id}/)
   ✅ 미디어 파일 포함
   ✅ 조회수 증가

4. 게시글 수정 (PATCH /api/posts/{id}/)
   ✅ 작성자만 수정 가능
   ✅ 타인 수정 시 403 에러

5. 게시글 삭제 (DELETE /api/posts/{id}/)
   ✅ 작성자만 삭제 가능

승인 시 다음 단계로 진행합니다.
```

---

## Phase 5: 파일 처리 및 스트리밍

### 5.1 파일 업로드

**목표**: 안전한 파일 업로드 시스템

**구현 사항**:
- 파일 크기 검증 (settings에서 설정)
- 확장자 화이트리스트
- MIME 타입 검증
- 고유 파일명 생성 (UUID)
- 날짜별 폴더 구조 (YYYY/MM/DD)
- 메타데이터 자동 저장

### 5.2 스트리밍 구현

**목표**: 음원/동영상 HTTP Range 요청 스트리밍

**구현 패턴**:
```python
from django.http import FileResponse, Http404
from wsgiref.util import FileWrapper
import os

@action(detail=True, methods=['get'])
def stream(self, request, pk=None):
    """미디어 파일 스트리밍"""
    media = self.get_object()
    
    # 파일 존재 확인
    if not os.path.exists(media.file.path):
        raise Http404
    
    # Range 요청 처리
    range_header = request.META.get('HTTP_RANGE', '').strip()
    size = os.path.getsize(media.file.path)
    
    if range_header:
        # Range 요청 파싱
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else size - 1
            length = end - start + 1
            
            # Partial Content 응답
            file = open(media.file.path, 'rb')
            file.seek(start)
            response = FileResponse(
                FileWrapper(file),
                content_type=media.mime_type,
                status=206
            )
            response['Content-Length'] = str(length)
            response['Content-Range'] = f'bytes {start}-{end}/{size}'
            response['Accept-Ranges'] = 'bytes'
            return response
    
    # 일반 응답
    response = FileResponse(
        open(media.file.path, 'rb'),
        content_type=media.mime_type
    )
    response['Content-Length'] = str(size)
    response['Accept-Ranges'] = 'bytes'
    return response
```

**핵심 개념**:
- HTTP Range 요청: 부분 콘텐츠 요청
- Status 206: Partial Content
- Content-Range 헤더
- Accept-Ranges 헤더

### 5.3 썸네일 자동 생성

**Pillow 사용**:
- 이미지 리사이징 (300x300)
- 품질 최적화 (quality=85)
- BytesIO로 메모리 처리
- save() 메서드에서 자동 생성

**사용자 테스트**:
```
🧪 파일 및 스트리밍 테스트:

1. 이미지 업로드
   ✅ 5MB 이하 업로드 성공
   ✅ 10MB 업로드 시 에러
   ✅ 썸네일 자동 생성
   ✅ 이미지 조회 가능

2. 음원 스트리밍
   ✅ mp3 파일 업로드 (50MB 이하)
   ✅ GET /api/media/{id}/stream/
   ✅ 브라우저에서 재생 가능
   ✅ Seek (탐색) 가능

3. 동영상 스트리밍
   ✅ mp4 파일 업로드 (200MB 이하)
   ✅ 스트리밍 재생
   ✅ 진행 바 조작 가능

승인 시 다음 단계로 진행합니다.
```

---

## Phase 6: 소셜 기능

### 6.1 좋아요 시스템

**구현**:
- Like 모델 (unique_together)
- @action: like(), unlike()
- 좋아요 수 자동 증가/감소
- 좋아요 여부 확인 (is_liked)

**API**:
```
POST   /api/posts/{id}/like/
DELETE /api/posts/{id}/unlike/
GET    /api/posts/{id}/likes/  # 좋아요한 사용자 목록
GET    /api/users/me/liked-posts/  # 내가 좋아요한 게시글
```

### 6.2 팔로우 시스템

**구현**:
- Follow 모델 (follower, following)
- @action: follow(), unfollow()
- 팔로워/팔로잉 수 자동 증가/감소
- 팔로우 여부 확인 (is_following)

**API**:
```
POST /api/users/{id}/follow/
DELETE /api/users/{id}/unfollow/
GET  /api/users/{id}/followers/
GET  /api/users/{id}/following/
```

### 6.3 댓글 시스템

**구현**:
- Comment 모델 (parent 필드)
- 대댓글 지원 (1단계 제한)
- 댓글 수 자동 증가/감소

**API**:
```
GET    /api/posts/{id}/comments/
POST   /api/posts/{id}/comments/
PATCH  /api/comments/{id}/
DELETE /api/comments/{id}/
POST   /api/comments/{id}/reply/  # 대댓글
```

**사용자 테스트**:
```
🧪 소셜 기능 테스트:

1. 좋아요
   ✅ 게시글에 좋아요
   ✅ 좋아요 취소
   ✅ 중복 좋아요 방지
   ✅ 좋아요 수 정확히 표시

2. 팔로우
   ✅ 다른 사용자 팔로우
   ✅ 언팔로우
   ✅ 자기 자신 팔로우 불가
   ✅ 팔로워/팔로잉 수 정확

3. 댓글
   ✅ 댓글 작성
   ✅ 대댓글 작성
   ✅ 본인 댓글만 수정/삭제
   ✅ 대댓글의 대댓글 불가

승인 시 다음 단계로 진행합니다.
```

---

## Phase 7: 권한 관리

### 7.1 기본 권한

**DRF 기본 권한**:
- IsAuthenticated: 인증 필수
- IsAuthenticatedOrReadOnly: 조회는 누구나
- IsAdminUser: 관리자만

### 7.2 객체 레벨 권한

**커스텀 권한 클래스**:
```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    """작성자만 수정/삭제 가능"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

### 7.3 세밀한 권한 관리

**목적별 권한**:
- IsOwner: 소유자만
- IsOwnerOrAdmin: 소유자 또는 관리자
- IsPublicOrOwner: 공개 게시글 또는 소유자
- IsVerified: 인증된 사용자만
- IsPremium: 프리미엄 사용자만 (요구사항에 따라)

**ViewSet별 권한**:
```python
class PostViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()
```

**사용자 테스트**:
```
🧪 권한 테스트:

1. 인증 없이
   ✅ 게시글 목록 조회 가능
   ✅ 게시글 작성 시 401 에러

2. 인증 후
   ✅ 본인 게시글 수정 가능
   ✅ 타인 게시글 수정 시 403 에러
   ✅ 타인 게시글 삭제 시 403 에러

3. 관리자
   ✅ 모든 게시글 수정/삭제 가능

승인 시 다음 단계로 진행합니다.
```

---

## Phase 8: 검색 및 필터링

### 8.1 필터링 (django-filter)

**FilterSet 구현**:
```python
class PostFilter(filters.FilterSet):
    author = filters.CharFilter(field_name='author__username')
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    is_public = filters.BooleanFilter()
    
    class Meta:
        model = Post
        fields = ['author', 'is_public']
```

### 8.2 검색 (SearchFilter)
```python
class PostViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'author__username']
```

### 8.3 정렬 (OrderingFilter)
```python
class PostViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'view_count', 'likes_count']
    ordering = ['-created_at']  # 기본 정렬
```

**사용자 테스트**:
```
🧪 검색/필터링 테스트:

Swagger UI에서:

1. 필터링
   ✅ ?author=username
   ✅ ?is_public=true
   ✅ ?created_after=2025-01-01

2. 검색
   ✅ ?search=키워드
   ✅ 제목, 내용, 작성자에서 검색

3. 정렬
   ✅ ?ordering=-created_at (최신순)
   ✅ ?ordering=-likes_count (좋아요 많은 순)
   ✅ ?ordering=-view_count (조회수 많은 순)

4. 복합 쿼리
   ✅ ?search=키워드&ordering=-likes_count

승인 시 다음 단계로 진행합니다.
```

---

## Phase 9: 통계 시스템

### 9.1 기본 통계

**User 통계**:
- followers_count
- following_count
- posts_count

**Post 통계**:
- view_count
- likes_count
- comments_count

### 9.2 집계 쿼리

**Django ORM Aggregation**:
```python
from django.db.models import Count, Avg, Max, Min, Sum

# 통계 예시
Post.objects.aggregate(
    total_posts=Count('id'),
    avg_likes=Avg('likes_count'),
    max_views=Max('view_count')
)

# 사용자별 통계
User.objects.annotate(
    total_likes=Sum('posts__likes_count'),
    total_views=Sum('posts__view_count')
)
```

### 9.3 통계 API

**엔드포인트**:
```
GET /api/analytics/overview/
    - 전체 통계 (사용자 수, 게시글 수, 총 좋아요 등)

GET /api/analytics/trending/
    - 인기 게시글 (24시간, 7일, 30일)

GET /api/analytics/posts/{id}/
    - 게시글별 상세 통계

GET /api/users/me/stats/
    - 내 통계
```

**구현 예시**:
```python
@action(detail=False, methods=['get'])
def overview(self, request):
    """전체 통계"""
    stats = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'total_likes': Like.objects.count(),
        'total_comments': Comment.objects.count(),
        'today_posts': Post.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
    }
    return Response(stats)

@action(detail=False, methods=['get'])
def trending(self, request):
    """인기 게시글"""
    period = request.query_params.get('period', '7d')
    
    if period == '24h':
        date_from = timezone.now() - timedelta(hours=24)
    elif period == '7d':
        date_from = timezone.now() - timedelta(days=7)
    else:
        date_from = timezone.now() - timedelta(days=30)
    
    posts = Post.objects.filter(
        created_at__gte=date_from,
        is_public=True
    ).order_by('-likes_count', '-view_count')[:10]
    
    serializer = self.get_serializer(posts, many=True)
    return Response(serializer.data)
```

**사용자 테스트**:
```
🧪 통계 테스트:

1. 전체 통계
   ✅ GET /api/analytics/overview/
   ✅ 사용자 수, 게시글 수 정확
   ✅ 오늘 작성된 게시글 수

2. 인기 게시글
   ✅ GET /api/analytics/trending/?period=24h
   ✅ GET /api/analytics/trending/?period=7d
   ✅ 좋아요/조회수 순 정렬

3. 개인 통계
   ✅ GET /api/users/me/stats/
   ✅ 내 팔로워/팔로잉 수
   ✅ 내 게시글 총 좋아요/조회수

승인 시 다음 단계로 진행합니다.
```

---

## Phase 10: 최적화

### 10.1 쿼리 최적화

**N+1 문제 해결**:
```python
# Bad: N+1 쿼리 발생
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # 각 post마다 쿼리

# Good: select_related 사용
posts = Post.objects.select_related('author').all()

# Good: prefetch_related 사용
posts = Post.objects.prefetch_related('media_files', 'likes').all()
```

**최적화 체크리스트**:
- [ ] select_related (ForeignKey, OneToOne)
- [ ] prefetch_related (ManyToMany, reverse ForeignKey)
- [ ] only() / defer()
- [ ] iterator() (대량 데이터)

### 10.2 인덱스 추가

**models.py Meta 클래스**:
```python
class Meta:
    indexes = [
        models.Index(fields=['author', '-created_at']),
        models.Index(fields=['is_public', '-created_at']),
        models.Index(fields=['-view_count']),
        models.Index(fields=['-likes_count']),
    ]
```

### 10.3 성능 테스트

**응답 시간 측정**:
- 목록 조회: < 200ms
- 상세 조회: < 100ms
- 생성: < 300ms
- 스트리밍: 즉시 시작

**사용자 테스트**:
```
🧪 성능 테스트:

1. 쿼리 수 확인
   ✅ 게시글 목록: 3개 이하 쿼리
   ✅ 게시글 상세: 5개 이하 쿼리

2. 응답 속도
   ✅ 목록 조회 빠른가?
   ✅ 100개 게시글에서도 빠른가?

3. 대용량 데이터
   ✅ 1000개 게시글 페이지네이션
   ✅ 스크롤 시 끊김 없음

승인 시 다음 단계로 진행합니다.
```

---

## Phase 11: 테스트

### 11.1 단위 테스트

**pytest 설정** (pytest.ini):
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**테스트 작성**:
```python
# tests/test_posts.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestPostAPI:
    def test_list_posts(self, client):
        """게시글 목록 조회 테스트"""
        url = reverse('post-list')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_create_post_without_auth(self, client):
        """인증 없이 게시글 작성 시 401"""
        url = reverse('post-list')
        data = {'title': 'Test', 'content': 'Content'}
        response = client.post(url, data)
        assert response.status_code == 401
```

**커버리지 목표**: 70% 이상

**Bash 명령어**:
```bash
# 테스트 실행
pytest

# 커버리지 확인
pytest --cov=. --cov-report=html
```

### 11.2 통합 테스트

**시나리오 테스트**:
1. 회원가입 → 로그인 → 게시글 작성 → 좋아요
2. 팔로우 → 팔로우한 사용자 게시글 조회
3. 파일 업로드 → 스트리밍 재생

**사용자 확인**:
```
🧪 테스트 실행:

터미널에서:
pytest

확인 사항:
✅ 모든 테스트 통과
✅ 커버리지 70% 이상
✅ 에러 없음

승인 시 다음 단계로 진행합니다.
```

---

## Phase 12: PostgreSQL 전환

### 12.1 PostgreSQL 설정

**.env 파일 수정**:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 12.2 마이그레이션

**Bash 명령어**:
```bash
# PostgreSQL 데이터베이스 생성
createdb your_db_name

# 마이그레이션
python manage.py migrate

# 슈퍼유저 재생성
python manage.py createsuperuser

# 테스트 데이터 로드 (선택)
python manage.py loaddata fixtures/initial_data.json
```

### 12.3 검증

**사용자 테스트**:
```
🧪 PostgreSQL 전환 테스트:

1. 서버 실행
   python manage.py runserver

2. 모든 기능 테스트
   ✅ 회원가입/로그인
   ✅ 게시글 CRUD
   ✅ 파일 업로드
   ✅ 스트리밍
   ✅ 좋아요/팔로우
   ✅ 검색/필터링
   ✅ 통계

모두 정상이면 프로덕션 준비 완료!
```

---

## 진행 프로토콜

### 단계 시작 시
```
📍 현재 단계: [Phase X - 단계명]

목표: [목표 설명]

작업 내용:
1. [작업 1]
2. [작업 2]

시작하겠습니다.
```

### 단계 완료 시
```
✅ 완료: [Phase X - 단계명]

구현된 기능:
- [기능 1]
- [기능 2]

🧪 테스트 방법:
[구체적인 테스트 시나리오]

확인 사항:
✅ [확인 항목 1]
✅ [확인 항목 2]

다음 단계로 진행할까요? (승인/수정/보류)
```

### Bash 명령어 실행 시
```
🔧 다음 명령어를 터미널에서 실행해주세요:

[명령어 블록]

완료하셨나요? (Y/N)
```

### 서버 실행 안내
```
🖥️ 서버를 실행해주세요:

터미널에서:
python manage.py runserver

브라우저에서:
http://127.0.0.1:8000/api/schema/swagger-ui/

테스트 후 결과를 알려주세요.
```

---

## 고급 기능 제안

프로젝트 완성 후 추가 검토 가능한 기능들:

### 1. 실시간 기능
- **WebSocket (Django Channels)**
  - 실시간 알림
  - 실시간 채팅
  - 라이브 스트리밍

### 2. 고급 검색
- **Elasticsearch 연동**
  - 전문 검색 (Full-text search)
  - 자동완성
  - 검색어 하이라이팅

### 3. 추천 시스템
- **협업 필터링**
  - 사용자 기반 추천
  - 콘텐츠 기반 추천
- **머신러닝 모델**
  - 개인화 추천

### 4. 고급 분석
- **데이터 시각화**
  - Chart.js / D3.js
  - 대시보드
- **A/B 테스트**
  - 기능 실험
  - 전환율 측정

### 5. 보안 강화
- **Rate Limiting (django-ratelimit)**
  - API 호출 제한
  - DDoS 방어
- **Two-Factor Authentication (2FA)**
  - OTP 인증
  - SMS 인증

### 6. 콘텐츠 관리
- **신고 시스템**
  - 부적절한 콘텐츠 신고
  - 자동 필터링
- **콘텐츠 모더레이션**
  - 관리자 검토 워크플로우
  - 자동 차단

### 7. 결제 시스템
- **Stripe/Toss Payments 연동**
  - 프리미엄 구독
  - 콘텐츠 구매
  - 후원 기능

### 8. 마케팅
- **SEO 최적화**
  - Meta tags
  - Sitemap
  - Open Graph
- **이메일 마케팅**
  - 뉴스레터
  - 프로모션

---

## 트러블슈팅

### 일반적인 문제

**1. 마이그레이션 충돌**
```bash
# 마이그레이션 리셋
python manage.py migrate --fake app_name zero
python manage.py migrate app_name
```

**2. JWT 토큰 인증 실패**
- Authorization 헤더: `Bearer <token>`
- 토큰 만료 확인
- SIMPLE_JWT 설정 확인

**3. CORS 오류**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

**4. 파일 업로드 실패**
- MEDIA_ROOT, MEDIA_URL 확인
- 디렉토리 권한 확인
- 파일 크기 제한 확인

**5. 스트리밍 작동 안 함**
- MIME 타입 확인
- Range 요청 헤더 확인
- 파일 경로 존재 확인

---

## 리소스

### 공식 문서
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- drf-spectacular: https://drf-spectacular.readthedocs.io/
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/

### 추천 패키지
- django-extensions: 개발 유틸리티
- django-silk: 프로파일링
- factory-boy: 테스트 데이터 생성
- faker: 더미 데이터

### 코드 품질
- black: 코드 포매팅
- flake8: 린팅
- isort: import 정렬
- mypy: 타입 체킹

---

이 Skill은 DRF 백엔드 개발의 전 과정을 단계별로 안내합니다. 각 단계를 완료하고 사용자의 테스트와 승인을 받아 진행하면, 프로덕션 수준의 안정적이고 확장 가능한 백엔드 시스템을 구축할 수 있습니다.