from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from .forms import TeacherForm


def index(request):
    return render(request, "home/index.html")


def teacher(request):
    """
        Teacher page where they may register into the system 
    """
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    elif request.user.is_authenticated:
        return redirect('menu:index')
    else:
        form = TeacherForm()

    return render(request, 'home/teacher.html', {'form': form})
