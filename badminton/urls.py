from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="cokcok-project",
        default_version='1.1.1',
        description="cokcok-project API 문서",
        terms_of_service="",
        contact=openapi.Contact(email="straipe@naver.com"), # 부가정보
        license=openapi.License(name="mit"),     # 부가정보
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('process/',include('process.urls')),
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)