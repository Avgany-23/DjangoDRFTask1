from django.urls import path, re_path
from .views import detector_api_view, DetectorFullGet, TemporaryCRUD


urlpatterns = [
    path('api/detectors/api_view', detector_api_view),
    path('api/detectors/full_info/<int:pk>', DetectorFullGet.as_view()),
    re_path('api/temporary/(?P<pk>\d+)?', TemporaryCRUD.as_view()),
]
