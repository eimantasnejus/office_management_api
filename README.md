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
* `python manage.py migrate` create initial database (this method will create sqlite database)
* `python manage.py createsuperuser --email sample@email.com --username sample_username` create Django administrator.

## Running App
`python manage.py runserver`

## Main Endpoints
Check *docs/api_documentation.md* for more information on endpoint usage.

* `admin/` - Django admin console for creating Employees and Meeting Rooms;
* `api/reservations/` - get list of reservations [GET, POST];
* `api/reservations/?room=1` - get list of reservations by meeting room id [GET, POST];
* `api/reservations/1/` - get reservation by id [GET, PUT, DELETE];
* `api/rooms/` - get list of rooms [GET].
* `api/reservations/1/` - get rooms by id [GET];

## Running Tests
`python manage.py test`

## TODO
* TODO: Dockerize project and update launch instructions;

## Nice To Have
* Code division to multiple directories / files;
* Documentation using Swagger;
* Pylint error fixes.
