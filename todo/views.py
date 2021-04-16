from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required#for making pages only when logged in[is an decorator]
# Create your views here.


def home(request):
    context = {}
    return render(request, 'todo/home.html', context)


def signupuser(request):

    if request.method == "GET":
        context = {'form': UserCreationForm()}
        return render(request, 'todo/signupuser.html', context)    
    
    else:#that is if POST method
        if request.POST['password1'] == request.POST['password2']:
            
            try:

                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)#logged in as the given name let us into the application
                return redirect('currenttodos')

            except IntegrityError:#if the inputted username is taken already this shows error
                context = {'form': UserCreationForm(), 'error': "Username already taken.. Choose a new one"}
                return render(request, 'todo/signupuser.html', context)                 

        else:#if passwords didnt match
            context = {'form': UserCreationForm(), 'error': "passwords didnt match"}
            return render(request, 'todo/signupuser.html', context) 
         

def loginuser(request):
#copy from signupviews and do some customixations
    if request.method == "GET":
        context = {'form': AuthenticationForm()}
        return render(request, 'todo/loginuser.html', context)    
    
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user == None:
            context = {'form': AuthenticationForm(), "error": "Username and password didn't m,atch"}
            return render(request, 'todo/loginuser.html', context)
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    context = {"todos": todos}
    return render(request, 'todo/currenttodos.html', context)

@login_required
def createtodo(request):
    if request.method == "GET":
        context = {'form': TodoForm()}
        return render(request, 'todo/createtodo.html', context)
    else:
        try:#not to mess with frontend code

            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user#specifying user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            context = {'error': "bad data error"}
            return render(request, 'todo/createtodo.html', context)

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)#can update again in web
        context = {"todo": todo, "form": form}
        return render(request, 'todo/viewtodo.html', context)
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            context = {'todo': todo, "form": form, 'error': "bad data setup"}
            return render(request, 'todo/viewtodo.html', context)

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')
        
@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    context = {"todos": todos}
    return render(request, 'todo/completedtodos.html', context)
