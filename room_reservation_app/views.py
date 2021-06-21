from django.http import HttpResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from room_reservation_app.models import Reservation, Room
from room_reservation_app.serializers import ReservationSerializer, ReservationResponseSerializer, RoomSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the app index.")


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
        # TODO: Check if room is empty on requested time.
        if serializer.is_valid():
            data = serializer.validated_data
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
