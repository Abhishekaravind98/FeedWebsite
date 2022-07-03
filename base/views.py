from multiprocessing import context
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Topic
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout

# rooms = [
#     {'id':1, 'name': 'lets learn python'},
#     {'id':2, 'name': 'Front end dev'},
#     {'id':3, 'name': 'Back end dev'},
    
# ]

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('homepage')

    page = 'login'

    if request.method == 'POST':
        username =request.POST.get('username')
        password =request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,  'User Does not exist')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Username or Password doesnt exist')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('homepage')

def registerPage(request):
    page = 'register'
    return render(request, 'base/login_register.html')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()
    room_count = rooms.count() #works better than len method of python

    context= {'rooms':rooms, 'topics':topics,'room_count':room_count}
    return render(request,'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    context= {'room':room}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')

    context={'form': form}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('you are not allowed here')



    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('homepage')

    context = {}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        room.delete()
        return redirect('homepage')
    return render(request, 'base/delete.html',{'obj':room})