from django.contrib import admin

from .models import User,Room,Message, RoomMembership

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(RoomMembership)
