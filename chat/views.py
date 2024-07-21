from django.shortcuts import render
from django.http import HttpResponse
from django.db import IntegrityError
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from .forms import RoomForm
from django.db.models import Q, Subquery, OuterRef

from .models import User, Room, Message, RoomMembership

def index(request):
    if request.user.id:
        user = request.user
        # rooms = Room.objects.filter(owner=request.user)
        latest_messages_timestamp_subquery = Message.objects.filter(
            room=OuterRef('pk')
        ).order_by('-timestamp').values('timestamp')[:1]

        # Subquery to get the latest message for each room
        latest_messages_subquery = Message.objects.filter(
            room=OuterRef('pk')
        ).order_by('-timestamp').values('message')[:1]

        # Annotate rooms with the latest message and latest message timestamp, then order by latest message timestamp
        rooms = Room.objects.filter(
            Q(owner=user) | Q(roommembership__user=user)
        ).distinct().annotate(
            latest_message=Subquery(latest_messages_subquery),
            latest_message_timestamp=Subquery(latest_messages_timestamp_subquery)
        ).order_by('-latest_message_timestamp')
        
        return render(request, "chat/chat.html", {
            "rooms":rooms,
        })
    return render(request, "chat/login.html",{"class":"container"})

def tabs(request, tab):
    if request.user.id:
        try:
            user = request.user
            # rooms = Room.objects.filter(owner=request.user)
            cat_ = tab.title()
            page = tab.lower()

            latest_messages_timestamp_subquery = Message.objects.filter(
            room=OuterRef('pk')
            ).order_by('-timestamp').values('timestamp')[:1]

            # Subquery to get the latest message for each room
            latest_messages_subquery = Message.objects.filter(
                room=OuterRef('pk')
            ).order_by('-timestamp').values('message')[:1]

            rooms = Room.objects.filter(
                (Q(owner=user) | Q(roommembership__user=user)) & Q(category=cat_)
            ).distinct().annotate(
                latest_message=Subquery(latest_messages_subquery),
                latest_message_timestamp=Subquery(latest_messages_timestamp_subquery)
            ).order_by('-latest_message_timestamp')
            
            return render(request, f"chat/{page}.html", {
                "rooms":rooms,
            })
        except:
            return redirect('index')

    return render(request, "chat/login.html",{"class":"container"})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username_l"]
        password = request.POST["password_l"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "chat/login.html", {
                "class":"container",
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "chat/login.html",{"class":"container"})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username_s"]
        email = request.POST["email_s"]

        # Ensure password matches confirmation
        password = request.POST["password_s"]
        confirmation = request.POST["confirmation_s"]

        if password != confirmation:
            return render(request, "chat/login.html", {
                "class":"container right-panel-active",
                "message": "Passwords must match."
            })
        print(username,email,password,confirmation)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            
        except IntegrityError:
            return render(request, "chat/login.html", {
                "class":"container right-panel-active",
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "chat/login.html",{"class":"container right-panel-active"})
    

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()

            group = get_object_or_404(Room, id=room.id)
            user = get_object_or_404(User, id=request.user.id)
            group.add_member(user)
            
            return redirect('index')
        else:
            
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = RoomForm()
        
   
def rooms(request,id):
    user = request.user
    # rooms = Room.objects.filter(owner=request.user)
    latest_messages_timestamp_subquery = Message.objects.filter(
        room=OuterRef('pk')
    ).order_by('-timestamp').values('timestamp')[:1]

    # Subquery to get the latest message for each room
    latest_messages_subquery = Message.objects.filter(
        room=OuterRef('pk')
    ).order_by('-timestamp').values('message')[:1]

    # Annotate rooms with the latest message and latest message timestamp, then order by latest message timestamp
    rooms = Room.objects.filter(
        Q(owner=user) | Q(roommembership__user=user)
    ).distinct().annotate(
        latest_message=Subquery(latest_messages_subquery),
        latest_message_timestamp=Subquery(latest_messages_timestamp_subquery)
    ).order_by('-latest_message_timestamp')

    is_member = RoomMembership.objects.filter(user=user, room__id = id)
    if is_member:
        data = Room.objects.get(pk=id)
        memnbers = data.members()
        msgs = data.get_messages()
        members_count = len(memnbers)
        me = request.user.username
        return render(request, "chat/rooms.html", {
            "rooms":rooms,
            "data":data,
            "msgs":msgs,
            "members":memnbers,
            "members_count":members_count,
            "me":me,
        })
    else:
        return redirect('index')


def settings(request, id):
    
    user = request.user
    # rooms = Room.objects.filter(owner=request.user)
    rooms = Room.objects.filter(
        Q(owner=user) | Q(roommembership__user=user)
    ).distinct()

    data = Room.objects.get(pk=id)
    memnbers = data.members()
    msg = Message.objects.filter(room=data).count()
    members_count = len(memnbers)
    me = request.user.username

    if request.method == "POST":
        confirmation_text = request.POST["confirmation_text"]
        if confirmation_text == 'YES':
            data.delete()
            return redirect('index')
        else:
            error_message = "You must type 'YES' to confirm deletion."
            messages.success(request, error_message)

    return render(request, "chat/settings.html", {
        "rooms":rooms,
        "data":data,
        "msg_count":msg,
        "members":memnbers,
        "members_count":members_count,
        "me":me,
    })

@csrf_exempt
@login_required
def add_member(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Room, id=group_id)
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        group.add_member(user)
        return JsonResponse({'status': 'success'})

@csrf_exempt
@login_required
def remove_member(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Room, id=group_id)
        
        if request.user.id == group.owner.id:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, username=user_id)
            group.remove_member(user)
            return JsonResponse({'status': 'success'})
        
