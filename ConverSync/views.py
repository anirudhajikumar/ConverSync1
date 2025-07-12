from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Topic, Message, Profile
from .forms import RoomForm, editProfilePage, signUpForm
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Django'},
#     {'id': 2, 'name': 'Bootstrap'},
#     {'id': 3, 'name': 'React'},
# ]
def loginPage(request):
    title="Conversync login"
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is not valid')


    context = {'page': page, 'title':title}
    return render(request, 'login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    title ='Conversync Register'
    page = 'register'
    form = signUpForm()
    
    if request.method == 'POST':
        form = signUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            Profile.objects.create(user=user, name=user.username)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration ! ')

    context = {
        'page': page,
        'form': form,
        'title': title,
    }
    return render(request, 'login_register.html', context)


def home(request):
    title ='Conversync'
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                | Q(name__icontains=q)
                                | Q(description__icontains=q))
    
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:4]

    
    room_count = rooms.count
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[:4]
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'title': title
    }
    return render(request, 'home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    title = room.name
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants' : participants,
        'title': title
    }

    return render(request, 'room.html', context)

@login_required(login_url='/login/')
def createRoom(request):
    title = "Create Room"
    form = RoomForm()
    context = {'form': form}
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
    context = {
        'title':title,
        'form': form
    }
    return render(request, 'room_form.html', context)


@login_required(login_url='/login/')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    title = 'Update '+ room.name
    if request.user != room.host:
        messages.error(request,'You are not allowed to perform the action')
        return redirect('/')

    else:
        if request.method == 'POST':
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect('home')
    context = {
        'form': form,
        'title': title,
    }
    return render(request, 'room_form.html', context)

@login_required(login_url='/login/')
def deleteRoom(request, pk):

    room = Room.objects.get(id=pk)
    title = 'Delete Room'
    if request.user != room.host:
        messages.error(request,'You are not allowed to perform the action')
        return redirect('/')

    else:
        if request.method == 'POST':
            room.delete()
            return redirect('/')
    context = {
        'obj': room,
        'title': title,
    }
    return render(request, 'delete.html', context)


@login_required(login_url='/login/')
def deleteMessage(request, pk):
    title = "Message Deletion"
    message = Message.objects.get(id=pk)
    room = message.room

    if request.user != message.user:
        messages.error(request,'You are not allowed to perform the action')
        return redirect('/')

    else:
        if request.method == 'POST':
            message.delete()
            return redirect('room',room.id)
    context = {
        'obj': message,
        'title': title
    }
    return render(request, 'delete.html', context)


def profilePage(request, pk):
    user = User.objects.get(id=pk)
    if user.profile:
        title = user.profile.name
    else:
        title = user.username
    rooms = user.room_set.all()
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:4]
    room_messages = user.message_set.all()
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_messages': room_messages,
        'title': title
    }
    return render(request,'profile.html', context)


@login_required
def editProfile(request):
    user = request.user
    title ="Edit user page"
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    
    if request.method == 'POST':
        form = editProfilePage(request.POST, request.FILES, instance=profile)  # ✅ FIXED
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        # ✅ Initialize form with existing profile data
        form = editProfilePage(instance=profile)

    return render(request, 'edit_user.html', {'form': form, 'title': title})

def TopicList(request):
    title= "Topics"
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(Q(name__icontains=q)).annotate(room_count=Count('room'))

    if request.method == "POST":
        topic_name = request.POST.get('topic_name')
        
        if topic_name:  # Only continue if a topic name was actually provided
            flag = 0
            for topic in topics:
                if topic.name.lower() == topic_name.lower():
                    flag = 1
                    break

            if flag == 1:
                messages.error(request, 'A topic with this name already exists!')
            else:
                Topic.objects.create(name=topic_name)
                messages.success(request, 'New topic created successfully!')
                return redirect('topic')  # Replace with your actual URL name
        else:
            messages.error(request, 'Topic name cannot be empty!')

    context = {
        'topics': topics,
        'title': title
    }
    return render(request, 'topics.html', context)

    

    