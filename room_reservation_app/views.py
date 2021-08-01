from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.response import Response

from room_reservation_app.models import Reservation, Room
from room_reservation_app.serializers import ReservationSerializer, RoomSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """This viewset automatically provides list, create, retrieve, update and destroy actions."""
    serializer_class = RoomSerializer
    queryset = Room.objects.all()


class ReservationViewSet(viewsets.ModelViewSet):
    """This viewset automatically provides list, create, retrieve, update and destroy actions."""
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    filterset_fields = ['room']

    def create(self, request, *args, **kwargs):
        """Run default create action with custom validation beforehand."""
        data = request.data
        error_response = check_room_availability(data.get('room'), data.get('reserved_from'), data.get('reserved_to'))
        if type(error_response) == Response:
            return error_response
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """Run default update action with custom validation beforehand."""
        data = request.data
        reservation = self.get_object()
        error_response = check_reservation_ownership(request.user, reservation)
        if not error_response:
            error_response = check_room_availability(
                data.get('room'), data.get('reserved_from'), data.get('reserved_to'), reservation)
        if error_response:
            return error_response
        return super().update(request)

    def destroy(self, request, *args, **kwargs):
        """Run default destroy action with custom validation beforehand."""
        reservation = self.get_object()
        error_response = check_reservation_ownership(request.user, reservation)
        if error_response:
            return error_response
        return super().destroy(request)


def check_room_availability(room: Room, time_from: datetime, time_to: datetime,
                            reservation: Optional[Reservation] = None) -> Optional[Response]:
    """Return detailed Response if room is not available during requested period.

    :param room: Room instance.
    :param time_from: datetime object, representing requested start of reservation.
    :param time_to: datetime object, representing requested end of reservation.
    :param reservation: Reservation instance. Optional parameter, if given, this reservation will not be checked for
                        period overlap. Used for updating Reservations.

    :return: Response or None. In case of business logic breach, informative message is returned.
    """

    if time_from > time_to:
        return Response("Reservation start time cannot be later than its end time!", status=status.HTTP_400_BAD_REQUEST)
    if not is_room_available(room, time_from, time_to, reservation):
        return Response("Selected room is occupied during requested period!", status=status.HTTP_400_BAD_REQUEST)


def is_room_available(
        room: Room, time_from: datetime, time_to: datetime, reservation: Optional[Reservation] = None) -> bool:
    """Return true if room is available for reservation, false otherwise."""
    # Main filter condition - period overlap.
    f = ~Q(reserved_to__lt=time_from) & ~Q(reserved_from__gt=time_to)
    # Additional condition - skip same reservation.
    if reservation:
        f &= ~Q(id=reservation.id)
    # Also check if room is the same.
    existing_reservation = Reservation.objects.filter(f, room=room).first()
    if existing_reservation:
        return False
    return True


def check_reservation_ownership(user: User, reservation: Reservation) -> Optional[Response]:
    """Return detailed error Response if reservation is not owned by user making the request."""
    if reservation.owner != user:
        return Response("Only reservation owner can delete it!", status=status.HTTP_403_FORBIDDEN)
