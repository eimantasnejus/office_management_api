from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from room_reservation_app.models import Room, Reservation
from room_reservation_app.views import check_business_logic


class ReservationTest(TestCase):
    """Tests for functionality related to room reservation endpoints."""

    rooms_url = '/room-reservation-app/rooms/'
    reservations_url = '/room-reservation-app/reservations/'

    def setUp(self):
        # Initialize client.
        self.client = APIClient()

        # Room Instances.
        self.room1 = Room.objects.create(title='Room 1')
        self.room2 = Room.objects.create(title='Room 2')

        # User Instances.
        self.user1 = User.objects.create_user(
            email='testuser1@example.com',
            first_name='Name1',
            last_name='Surname1',
            username='testuser1',
            password='12345'
        )
        self.user2 = User.objects.create_user(username='testuser2', password='12345')

        # Reservation Instances.
        self.reservation1 = Reservation.objects.create(
            title="Daily Stand-up",
            room=self.room1,
            reserved_from=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            reserved_to=datetime.now(pytz.timezone(settings.TIME_ZONE)) + timedelta(minutes=20),
            owner=self.user1,
        )
        self.reservation1.employees.set([self.user1, self.user2])
        self.reservation2 = Reservation.objects.create(
            title="Sprint Planning",
            room=self.room2,
            reserved_from=datetime.now(pytz.timezone(settings.TIME_ZONE)) + timedelta(hours=2),
            reserved_to=datetime.now(pytz.timezone(settings.TIME_ZONE)) + timedelta(hours=6),
            owner=self.user1,
        )
        self.reservation2.employees.set([self.user1, self.user2])

        # Reusable template for creating/updating reservation instances.
        self.current_time = datetime.now(pytz.timezone(settings.TIME_ZONE))
        self.reservation_template = {
            "title": "Post Mortem",
            "room": self.room1.id,
            "reserved_from": (self.current_time - timedelta(hours=3)).isoformat(),
            "reserved_to": (self.current_time - timedelta(hours=2)).isoformat(),
            "owner": self.user1.id,
            "employees": [self.user1.id, self.user2.id]
        }

    def test_get_rooms(self):
        """Test list all rooms endpoint."""
        # Do.
        response = self.client.get(self.rooms_url, format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Get should return 200 status code.')
        self.assertEquals(len(response.json()), 2, '2 Rooms should be returned.')

    def test_create_reservations(self):
        """Test create reservation endpoint."""
        # Setup.
        request_data = self.reservation_template
        # Do.
        response = self.client.post(self.reservations_url, request_data, format='json')
        # Check.
        response_json = response.json()
        self.assertEquals(response.status_code, 201, 'Create should return 201 status code.')
        self.assertEquals(response_json.get('title'), 'Post Mortem', 'Check response content validity')
        self.assertEquals(len(response_json.get('employees')), 2, 'Check response content validity')
        self.assertEquals(Reservation.objects.count(), 3, 'Check if Reservation was created in database.')

    def test_get_all_reservations(self):
        """Test get all reservations endpoint."""
        # Do.
        response = self.client.get(self.reservations_url, format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Get should return 200 status code.')
        self.assertEquals(len(response.json()), 2, 'In total there are 2 reservations.')
        self.assertEquals(
            (response.json()[0]['owner']['email']),
            'testuser1@example.com',
            'Related objects should be serialized in human readable format.')

    def test_get_reservations_by_room(self):
        """Test get all reservations for requested room endpoint."""
        # Do.
        response = self.client.get(f"{self.reservations_url}?room_id={self.room2.id}", format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Get should return 200 status code.')
        self.assertEquals(len(response.json()), 1, 'There is 1 reservation for room2.')

    def test_get_reservations_by_non_existent_room_id(self):
        """Test get reservations by room endpoint, but with non existent, valid room id."""
        # Do.
        response = self.client.get(f"{self.reservations_url}?room_id=548654", format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Should return 200 status code, as request is still valid.')
        self.assertEquals(len(response.json()), 0, 'There are no reservations for requested room.')

    def test_get_reservations_by_invalid_room_id(self):
        """Test get reservations by room endpoint, but with invalid room id."""
        # Do.
        response = self.client.get(f"{self.reservations_url}?room_id=invalid_id", format='json')
        # Check.
        self.assertEquals(response.status_code, 400, 'Should return status 400, as request is invalid.')

    def test_get_reservation(self):
        # Do.
        response = self.client.get(f"{self.reservations_url}{self.reservation1.id}/", format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Get should return 200 status code.')
        self.assertEquals(response.json().get('title'),
                          'Daily Stand-up',
                          'Check if returned reservation details are correct.')

    def test_update_reservation(self):
        # Setup.
        request_data = self.reservation_template
        # Do.
        response = self.client.put(f"{self.reservations_url}{self.reservation1.id}/", request_data, format='json')
        # Check.
        self.assertEquals(response.status_code, 200, 'Put should return 200 status code.')
        self.assertEquals(response.json().get('title'), 'Post Mortem', 'Reservation title should have changed.')

    def test_delete_reservation(self):
        # Do.
        response = self.client.delete(f"{self.reservations_url}{self.reservation1.id}/", format='json')
        # Check.
        self.assertEquals(response.status_code, 204, 'Delete should return 204 status code.')
        self.assertFalse(Reservation.objects.filter(id=self.reservation1.id),
                         'Check if Reservation was removed from database.')

    def test_is_room_available(self):
        """Check if helper function `check_business_logic` works as expected with various parameters.

        Visual aid in the comments for each case:
        "-" - Requested period
        "|" - Existing period
        "+" - Overlapping period
        """
        # Case date_from > date_to
        result = check_business_logic(
            self.room1,
            self.current_time - timedelta(hours=6),
            self.current_time - timedelta(hours=5))
        self.assertEquals(result, None)
        # Case ---- ||||
        result = check_business_logic(
            self.room1,
            self.current_time - timedelta(hours=6),
            self.current_time - timedelta(hours=5))
        self.assertEquals(result, None)
        # Case ---+|||
        result = check_business_logic(
            self.room1,
            self.current_time - timedelta(hours=6),
            self.current_time)
        self.assertEquals(type(result), Response)
        # Case |||++---
        result = check_business_logic(
            self.room1,
            self.current_time + timedelta(minutes=6),
            self.current_time + timedelta(hours=6))
        self.assertEquals(type(result), Response)
        # Case ---+++----
        result = check_business_logic(
            self.room1,
            self.current_time - timedelta(hours=6),
            self.current_time + timedelta(hours=6))
        self.assertEquals(type(result), Response)
        # Case |||+++|||
        result = check_business_logic(
            self.room1,
            self.current_time + timedelta(minutes=3),
            self.current_time + timedelta(minutes=6))
        self.assertEquals(type(result), Response)
        # Case ||| ---
        result = check_business_logic(
            self.room1,
            self.current_time + timedelta(hours=6),
            self.current_time + timedelta(hours=7))
        self.assertEquals(result, None)
        # Case overlapping time with room1, but different room.
        result = check_business_logic(
            self.room2,
            self.current_time,
            self.current_time + timedelta(hours=1.5))
        self.assertEquals(result, None)
