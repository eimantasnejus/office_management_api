# API Documentation

## Intro

This is a collection of sample API requests so that API users could quickly get hang of it.

## Rooms Endpoints

`GET` *room-reservation-app/rooms/*

List all rooms. API users have permission to read only. Other CRUD operations made with Django Admin.

## Reservations Endpoints

`GET` `POST` *room-reservation-app/reservations/*

List all reservations (GET), or create a new reservation (POST).

Anyone can Read, but only authorized users can Create.

Sample POST content:
```angular2html
{
   "title":"Retrospective",
   "room":1,
   "reserved_from":"2021-06-20T14:25:58.166219+03:00",
   "reserved_to":"2021-06-20T15:25:58.166219+03:00",
   "owner":1,
   "employees":[
      1,
      2
   ]
}
```

`GET` *room-reservation-app/reservations/?room_id=<int: room_id>*

List all reservations by selected room.

`GET` `PUT` `DELETE` *room-reservation-app/reservations/<int: reservation_id>/*

Get, Update or Delete single reservation.

Anyone can Read, but only authorized users who Created reservation can Update and Delete.

Sample PUT content:
```angular2html
{
   "title":"Retrospective",
   "room":2,
   "reserved_from":"2021-05-20T14:25:58.166219+03:00",
   "reserved_to":"2021-05-20T15:25:58.166219+03:00",
   "owner":1,
   "employees":[
      1,
      2,
      3
   ]
}
```
