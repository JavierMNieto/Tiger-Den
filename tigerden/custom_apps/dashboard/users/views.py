from oscar.apps.dashboard.users import views
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse

from django.contrib.auth.models import Group

supervisor_group = Group.objects.get(name='Supervisor')

class UserDetailView(views.UserDetailView):
    def post(self, request, *args, **kwargs):
        if "user_action" in request.POST:
            return self.change_supervisor(request)

        return self.reload_page(error=_("No valid action submitted"))

    def change_supervisor(self, request):
        user = request.user

        if user.is_supervisor():
            supervisor_group.user_set.remove(user)
            messages.info(request, "Removed supervisor permissions from " + user.label())
        else:
            supervisor_group.user_set.add(user)
            messages.info(request, "Added supervisor permissions to " + user.label())
        
        return self.reload_page()
    
    def reload_page(self, fragment=None, error=None):
        url = reverse('dashboard:user-detail',
                      kwargs={'pk': self.request.user.id})
        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)