from django.db.models import QuerySet
from rest_framework.decorators import api_view
from rest_framework import status, generics, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from .serializers import DetectorSerializer, TemporaryMeasurementSerializer
from .models import Detector, TemporaryMeasurement, models
from typing import Any, Optional
import api_detectors


# ------- через api_view и тело запроса -------
# Кастомные функции для валидации
def get_pk(obj: Any) -> Optional[int]:
    try:
        return int(obj)
    except (TypeError, ValueError):
        return None

def get_query_set(pk: int, model: models) -> Optional[QuerySet]:
    try:
        return model.objects.get(id=pk)
    except api_detectors.models.Detector.DoesNotExist:
        return None

def response_error(pk: Optional[int | str]) -> Response:
    if isinstance(pk, int) and pk < 0:
        data = {'Invalid value': 'id must be less than zero'}
    else:
        data = {'Invalid type': 'id must be of type int'}
    return Response(status=status.HTTP_400_BAD_REQUEST,
                        data=data)


# Кастомные функции для методов GUT, POST, PUT, PATCH, DELETE
def method_get(clean_pk: int) -> Response:
    if clean_pk == 0:
        detectors = Detector.objects.all()
    else:
        detectors = Detector.objects.filter(id=clean_pk).all()

    if not detectors:
        return Response(status=HTTP_404_NOT_FOUND, data={'Not found': f'id = {clean_pk} does`t exists'})

    result = DetectorSerializer(detectors, many=True)
    return Response(result.data)


def method_post(request: Request) -> Response:
    result = DetectorSerializer(data=request.data)
    if result.is_valid():
        result.save()
        return Response(result.data, status=status.HTTP_201_CREATED)
    return Response(result.errors, status=HTTP_400_BAD_REQUEST)


def method_patch(request: Request, clean_pk: int)  -> Response:
    query_set = get_query_set(clean_pk, Detector)
    if query_set is None:
        return Response({'Not found': f'id = {clean_pk} does`t exists'})

    result = DetectorSerializer(query_set, data=request.data, partial=False)
    if result.is_valid():
        result.save()
        return Response(result.data, status=status.HTTP_200_OK)
    return Response(result.errors, status=HTTP_400_BAD_REQUEST)

def method_put(request: Request, clean_pk: int) -> Response:
    if not request.data.get('description'):
        return Response(data={'description': ["This field may not be blank or required"]})
    return method_patch(request, clean_pk)

def method_delete(clean_pk: int) -> Response:
    query_set = get_query_set(clean_pk, Detector)
    if query_set is None:
        return Response({'Not found': f'id = {clean_pk} does`t exists'})
    query_set.delete()
    return Response(data='Success delete', status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def detector_api_view(request: Request) -> Response:
    """
    Запрос отвечает на методы GET, POST, PUT, PATCH и DELETE модели Detector
    Заголовок Type-Content: application/json
    В теле запроса передаются данные
        id = int - конкретный датчик
        id = 0 - список всех датчиков

    Пример с методом GET - получение ресурса/ов
        curl -X GET http://127.0.0.1:8000/api/detectors/api_view
            - H {"Content-Type": "application/json"}
            - b {"id": "3"}

    Пример с методом POST - создание ресурса
        curl -X POST http://127.0.0.1:8000/api/detectors/api_view
            - H {"Content-Type": "application/json"}
            - b {"name": "detector one", "description": "description detector"}

    Пример с методом PUT - полное обновление ресурса
        curl -X PUT http://127.0.0.1:8000/api/detectors/api_view
            - H {"Content-Type": "application/json"}
            - b {"id": "3", "name": "new detector name", "description": "new description detector"}

    Пример с методом PATCH - частичное обновление ресурса
        curl -X PATCH http://127.0.0.1:8000/api/detectors/api_view
            - H {"Content-Type": "application/json"}
            - b {"id": "3", "name": "new detector name"}

    Пример с методом DELETE - удаление ресурса
        curl -X PATCH http://127.0.0.1:8000/api/detectors/api_view
            - H {"Content-Type": "application/json"}
            - b {"id": "3", "name": "new detector name"}
    """

    if request.method == 'POST':
        return method_post(request)


    # Если запрос не на метод POST, то проверяем валидность id из body запроса
    clean_pk = get_pk(request.data.get('id'))
    if clean_pk is None or clean_pk < 0:
        return response_error(clean_pk)

    if request.method == 'GET':
        return method_get(clean_pk)
    if request.method == 'PUT':
        return method_put(request, clean_pk)
    if request.method == 'PATCH':
        return method_patch(request, clean_pk)
    if request.method == 'DELETE':
        return method_delete(clean_pk)


# ------- через APIView и параметры заголовков -------
class DetectorFullGet(APIView):
    """Метод GET по пути api/detectors/full_info/<int:pk>.
    Предоставляет полную информацию о датчике с измерением температуры"""
    def get(self, request: Request, pk) -> Response:
        det = Detector.objects.filter(id=pk).first()
        if det is None:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

        temp = TemporaryMeasurement.objects.filter(detectors=pk).all()
        result = {'id': pk, **DetectorSerializer(det, many=False).data,
                  'measurements':
                      TemporaryMeasurementSerializer(temp, many=True).data}
        return Response(result)


# ------- через RetrieveUpdateDestroyAPIView + Миксин на метод POST и параметры заголовков -------
class TemporaryCRUD(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    """Стандартные классы. Доступны методы GET, POST, PUT, PATCH и DELETE,
    доступны по адресу http://127.0.0.1:8000/api/temporary/?pk?  , где pk - дополнительный параметр URL"""
    queryset = TemporaryMeasurement.objects.all()
    serializer_class = TemporaryMeasurementSerializer

    def post(self, request: Request):
        """
        Пример с методом POST - создание ресурса
        curl -X POST http://127.0.0.1:8000/api/temporary/
            - H {"Content-Type": "application/json"}
            - b {"temporary": "34", "date_time": "2024-01-01T15:15:15", "detectors": "1"}
        """
        return super().create(request)
