from room_reservation_app.views import RoomViewSet, ReservationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('rooms', RoomViewSet)
router.register('reservations', ReservationViewSet)
