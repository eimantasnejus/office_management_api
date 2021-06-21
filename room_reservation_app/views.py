from datetime import datetime
from typing import Optional

from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from room_reservation_app.models import Reservation, Room
from room_reservation_app.serializers import ReservationSerializer, ReservationResponseSerializer, RoomSerializer


class ReservationList(APIView):
    """List all reservations, or create a new reservation."""

    @staticmethod
    def get(request):
        """Return all reservations or reservations by requested room."""
        if request.GET.get('room_id'):
            try:
                reservations = Reservation.objects.filter(room=request.GET.get('room_id'))
            except ValueError:
                return Response("room_id must be an integer.", status=status.HTTP_400_BAD_REQUEST)
        else:
            reservations = Reservation.objects.all()
        serializer = ReservationResponseSerializer(reservations, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        """Create a reservation instance."""
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Check business logic.
            error = check_business_logic(data.get('room'), data.get('reserved_from'), data.get('reserved_to'))
            if error:
                return error

            reservation = Reservation.objects.create(
                title=data.get('title'),
                room=data.get('room'),
                reserved_from=data.get('reserved_from'),
                reserved_to=data.get('reserved_to'),
                owner=data.get('owner'),
            )
            reservation.employees.set(data.get('employees'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationDetail(APIView):
    """Retrieve, update or delete a reservation instance."""

    def get(self, request, pk):
        reservation = self.get_object(pk)
        serializer = ReservationResponseSerializer(reservation)
        return Response(serializer.data)

    def put(self, request, pk):
        reservation = self.get_object(pk)
        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Check business logic.
            error = check_business_logic(data.get('room'), data.get('reserved_from'), data.get('reserved_to'))
            if error:
                return error
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reservation = self.get_object(pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_object(pk):
        try:
            return Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise Http404


class RoomList(APIView):
    """List all rooms."""

    @staticmethod
    def get(request):
        """Return list of all rooms."""
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)


def check_business_logic(room: Room, time_from: datetime, time_to: datetime) -> Optional[Response]:
    """Check if provided data follows business logic.

    :param room: Room instance.
    :param time_from: datetime object, representing requested start of reservation.
    :param time_to: datetime object, representing requested end of reservation.
    :return: Response or None. In case of business logic breach, Response with informative message is returned.
    """

    if time_from > time_to:
        return Response("Reservation start time cannot be later than its end time!", status=status.HTTP_400_BAD_REQUEST)
    if not is_room_available(room, time_from, time_to):
        return Response("Selected room is occupied during requested period!",
                        status=status.HTTP_400_BAD_REQUEST)


def is_room_available(room, time_from, time_to):
    """Return true if room is available for reservation, false otherwise."""
    existing_reservation = Reservation.objects.filter(
        (~Q(reserved_to__lt=time_from) &
         ~Q(reserved_from__gt=time_to)),
        room=room,
    ).first()
    if existing_reservation:
        return False
    return True
