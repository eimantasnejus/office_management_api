from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from room_reservation_app.models import Reservation


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'title']


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'title', 'owner', 'employees', 'created_at', 'reserved_from', 'reserved_to', 'room']


class ReservationResponseSerializer(serializers.ModelSerializer):
    owner = SerializerMethodField(required=False)
    employees = SerializerMethodField(required=False)
    created_at = SerializerMethodField(required=False)
    reserved_from = SerializerMethodField(required=False)
    reserved_to = SerializerMethodField(required=False)
    room = SerializerMethodField(required=False)

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'owner', 'employees', 'created_at', 'reserved_from', 'reserved_to', 'room']

    def get_owner(self, obj):
        if obj.owner:
            return self.get_serialized_employee(obj.owner)

    def get_employees(self, obj):
        if obj.employees.all():
            return [self.get_serialized_employee(employee) for employee in obj.employees.all()]

    def get_created_at(self, obj):
        if obj.created_at:
            return self.get_serialized_datetime(obj.created_at)

    def get_reserved_from(self, obj):
        if obj.reserved_from:
            return self.get_serialized_datetime(obj.reserved_from)

    def get_reserved_to(self, obj):
        if obj.reserved_to:
            return self.get_serialized_datetime(obj.reserved_to)

    @staticmethod
    def get_room(obj):
        if obj.room:
            return {
                "id": obj.room.id,
                "title": obj.room.title,
            }

    @staticmethod
    def get_serialized_employee(employee):
        return {
            "id": employee.id,
            "email": employee.email,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
        }

    @staticmethod
    def get_serialized_datetime(datetime):
        return datetime.strftime("%Y-%m-%d %H:%M")
