from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Room(models.Model):
    CATEGORY_CHOICES = [
        ('Work', 'Work'),
        ('Friends', 'Friends'),
        ('News', 'News'),
    ]

    id = models.BigAutoField(primary_key=True)
    room_name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Friends')

    def add_member(self, user):
        RoomMembership.objects.create(room=self, user=user)

    def remove_member(self, user):
        RoomMembership.objects.filter(room=self, user=user).delete()

    def get_messages(self):
        return [message.serialize() for message in self.message_set.all()]
    
    def members(self):
        return [membership.user.username for membership in self.roommembership_set.all()]

    def serialize(self):
        return {
            "id": self.id,
            "room_name": self.room_name,
            "owner": self.owner.username,
            "category": self.category,
            "members": [membership.user.username for membership in self.roommembership_set.all()],
            "messages": [message.serialize() for message in self.message_set.all()],
        }

    def __str__(self):
        return self.room_name
    
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "sender": self.sender.username,
            "message": self.message,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"
    
class RoomMembership(models.Model):
    room = models.ForeignKey(Room,  on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')


    def __str__(self):
        return f'{self.user.username} in {self.room.room_name}'
