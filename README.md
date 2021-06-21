# Office Management API

## Summary
Currently, Office Management API has one App - Room Reservation App, which allows employees to manage meeting room
reservations.

App administrator can manage Employees and Meeting Rooms.

## Technical Requirements
* Python 3.6+

## Setup
* `git clone git@github.com:eimantasnejus/office_management_api.git`;
* `cd office_management_api`;
* `pip install virtualenv` (if you don't already have virtualenv installed);
* `virtualenv venv` to create your new environment (called 'venv' here);
* `source venv/bin/activate` to enter the virtual environment;
* `pip install -r requirements.txt` to install the requirements in the current environment;
* `python manage.py createsuperuser --email sample@email.com --username sample_username` create Django administrator.

## Running App
`python manage.py runserver`

## Main Endpoints
* `admin/` - Django admin console for creating Employees and Meeting Rooms;
* `room-reservation-app/reservations/` - get list of reservations [GET, POST];
* `room-reservation-app/reservations/?room_id=1` - get list of reservations by meeting room id [GET, POST];
* `room-reservation-app/reservations/1/` - get list of reservations [GET, PUT, DELETE];
* `room-reservation-app/rooms/` - get list of rooms [GET].

## Running Tests
`python manage.py test`

## TODO
* TODO: Dockerize project and update launch instructions;
* TODO: Authentication solution;
* TODO: Redirect: http://127.0.0.1:8000/ -> http://127.0.0.1:8000/room-reservation-app/reservations/;
* TODO: Documentation for each endpoint.
* TODO: Migrations should be added to launch instructions

## Nice To Have
* Single Reservation object serializer;
* Code division to multiple directories / files.
* Pylint error fixes
