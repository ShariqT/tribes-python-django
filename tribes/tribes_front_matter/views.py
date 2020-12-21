from django.shortcuts import render
from tribes_front_matter.lib import actions
from django.http import HttpResponse
import json

template_data = {}
template_data['appname'] = 'FM'
template_data['welcome_message'] = 'Front Matter - What the World Sees Of You'
# Create your views here.
def index(request):
    data = template_data
    return render(request, "front_matter/index.html", data)


def view_config(request):
    data = {}
    data['welcome_message'] = template_data['welcome_message']
    data['appname'] = 'FM > Config'
    
    if request.method == 'GET':
        data['config_data'] = actions.read_jekyll_config()
        return render(request, "front_matter/config.html", data)
    else:
        print(request.POST['content'])
        actions.save_jekyll_config(request.POST['content'])
        data['config_data'] = actions.read_jekyll_config()
        res = HttpResponse(json.dumps({'config_data': data['config_data'] }))
        res['Content-Type'] = 'application/json'
        return res

def view_publish_feedback(request):
    data = {}
    data['welcome_message'] = template_data['welcome_message']
    data['appname'] = 'FM > Publish'
    data['socket_url'] = 'ws://localhost:8000/sys/command/feedback/'
    return render(request, "front_matter/publish.html", data)
