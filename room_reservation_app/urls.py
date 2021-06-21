from django.urls import path
from room_reservation_app import views

urlpatterns = [
    path('rooms/', views.RoomList.as_view()),
    path('reservations/', views.ReservationList.as_view()),
    path('reservations/<int:pk>/', views.ReservationDetail.as_view()),
]
