from django.shortcuts import render, redirect, get_object_or_404

from chat.models import Room, Message
from users.models import UserModel


def chat_view(request):
    if request.method == 'POST':
        room = request.POST['room']
        chat_type = request.POST.get('chat_type', 'group')

        try:
            existing_room = Room.objects.get(room_name=room)
        except Room.DoesNotExist:
            existing_room = Room.objects.create(
                room_name=room,
                chat_type=chat_type
            )
        return redirect('room', room_name=room, username=request.user)
    return render(request, 'chat.html')


def room_view(request, room_name, username):
    existing_room = get_object_or_404(Room, room_name=room_name)
    get_messages = Message.objects.filter(room=existing_room)
    rooms = request.user.chats.all()
    other_members = existing_room.members.exclude(id=request.user.id)
    q = request.GET.get("q")
    qs = UserModel.objects.filter(username__icontains=q) if q else UserModel.objects.none()

    context = {
        'rooms': rooms,
        'messages': get_messages,
        'username': request.user,
        "room_name": existing_room,
        'other_members': other_members,
        'members': qs,
    }
    return render(request, 'messages.html', context)


def chats_list(request):
    rooms = request.user.chats.order_by('-room_name')
    users = UserModel.objects.exclude(id=request.user.id).order_by('username')
    q = request.GET.get("q")

    if q:
        users = users.filter(username__icontains=q)


    context = {
        'rooms': rooms,
        'users': users,
    }

    return render(request, 'chats.html', context)


def another_user_profile_view(request, username):
    user = get_object_or_404(UserModel, username=username)
    users = UserModel.objects.exclude(id=request.user.id).order_by('username')

    q = request.GET.get('q')
    if q:
        users = users.filter(username__icontains=q)

    room_name = f"private_{'_'.join(sorted([request.user.username, user.username]))}"

    room = Room.objects.filter(room_name=room_name, chat_type='private').first()

    if not room:
        room = Room.objects.create(
            room_name=room_name,
            chat_type='private'
        )
        room.members.add(request.user, user)

    return redirect('room', room_name=room.room_name, username=request.user.username)