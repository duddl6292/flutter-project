from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.core.pagination import CommonPageNumberPagination

from .models import Hospital
from .serializers import HospitalSerializer


class HospitalListView(ListAPIView):
    """
    의료진 회원가입 및 로그인 화면에서 사용하는 병원 검색 API.

    GET /api/v1/hospitals/?search=서울
    GET /api/v1/hospitals/?search=서울&page=1&page_size=20
    """

    permission_classes = [AllowAny]
    serializer_class = HospitalSerializer
    pagination_class = CommonPageNumberPagination

    def get_queryset(self):
        keyword = self.request.query_params.get(
            "search",
            "",
        ).strip()

        queryset = Hospital.objects.filter(
            is_active=True,
        )

        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(address__icontains=keyword)
                | Q(hospital_code__icontains=keyword)
            )

        return queryset.order_by("name")