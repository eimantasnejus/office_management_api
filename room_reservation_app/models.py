from django.db import models


class Room(models.Model):
    """Model, representing meeting rooms in the office."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['title', 'created_at']

    def __str__(self):
        return self.title


class Reservation(models.Model):
    """Model, representing meeting room reservations."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    reserved_from = models.DateTimeField()
    reserved_to = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name='reservations', on_delete=models.CASCADE)
    employees = models.ManyToManyField('auth.User')

    class Meta:
        ordering = ['reserved_from', 'title']

    def __str__(self):
        return ", ".join([self.title, str(self.reserved_from.date())])
