from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from room_reservation_app.models import Reservation, Room
from room_reservation_app.serializers import ReservationSerializer, ReservationResponseSerializer, RoomSerializer


class ReservationList(APIView):
    """List all reservations, or create a new reservation."""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
            error_message = check_business_logic(data.get('room'), data.get('reserved_from'), data.get('reserved_to'))
            if error_message:
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

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

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        reservation = self.get_object(pk)
        serializer = ReservationResponseSerializer(reservation)
        return Response(serializer.data)

    def put(self, request, pk):
        reservation = self.get_object(pk)
        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Check reservation ownership.
            if request.user != reservation.owner:
                return Response("Only reservation owner can update it!", status=status.HTTP_403_FORBIDDEN)
            # Check business logic.
            error_message = check_business_logic(
                data.get('room'), data.get('reserved_from'), data.get('reserved_to'))
            if error_message:
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reservation = self.get_object(pk)
        # Check reservation ownership.
        if request.user != reservation.owner:
            return Response("Only reservation owner can delete it!", status=status.HTTP_403_FORBIDDEN)
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


def check_business_logic(room: Room, time_from: datetime, time_to: datetime) -> str:
    """Check if provided data follows business logic.

    :param room: Room instance.
    :param time_from: datetime object, representing requested start of reservation.
    :param time_to: datetime object, representing requested end of reservation.
    :return: string. In case of business logic breach, informative message is returned.
    """

    if time_from > time_to:
        return "Reservation start time cannot be later than its end time!"
    if not is_room_available(room, time_from, time_to):
        return "Selected room is occupied during requested period!"
    return ''



def is_room_available(room: Room, time_from: datetime, time_to: datetime) -> bool:
    """Return true if room is available for reservation, false otherwise."""
    existing_reservation = Reservation.objects.filter(
        (~Q(reserved_to__lt=time_from) &
         ~Q(reserved_from__gt=time_to)),
        room=room,
    ).first()
    if existing_reservation:
        return False
    return True


def is_reservation_owner(user: User, reservation: Reservation) -> bool:
    """Return true if reservation is owned by user making a request, false otherwise."""
    return True if reservation.owner == user else False
