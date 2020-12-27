from django.shortcuts import render

template_data = {}
template_data['welcome_message'] = 'Storage'
template_data['appname'] = 'STOR'
# Create your views here.
def index(request):

    return render(request, "storage/index.html", template_data)