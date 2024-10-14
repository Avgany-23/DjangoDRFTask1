from rest_framework import serializers
from .models import Detector, TemporaryMeasurement

class DetectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detector
        fields = (
            'name',
            'description'
        )

    def create(self, validated_data):
        return Detector.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class TemporaryMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryMeasurement
        fields = (
            'temporary',
            'date_time',
            'detectors',
        )

    def create(self, validated_data):
        return TemporaryMeasurement.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.temporary = validated_data.get('temporary', instance.temporary)
        instance.date_time = validated_data.get('date_time', instance.date_time)
        instance.date_time = validated_data.get('date_time', instance.date_time)
        instance.save()
        return instance
