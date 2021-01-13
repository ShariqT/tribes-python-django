from django.shortcuts import render, redirect
from tribes_storage.lib import actions
from django.urls import reverse
import json


global_data = {}
global_data['welcome_message'] = 'Storage'
global_data['appname'] = 'STOR'

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

def convert_entries_to_dict(entries, path):
    if len(path) == 0:
        ret_list = [{'Name': '/', 'Type': 0, 'Path': None }]
    else:
        ret_list = [{'Name': '../', 'Type': 0, 'Path':  "/".join(path[0:-1]) }]
    for entry in entries:
        ret_list.append({
            'Name': entry['Name'],
            'Type': entry['Type'],
            'Size': entry['Size'],
            'Hash': entry['Hash'],
            'Path': "/".join(path) + "/" + entry['Name']
        })
    return [ret_list[i:i + 4] for i in range(0, len(ret_list), 4)]



# Create your views here.
def index(request):
    template_data = global_data
    template_data['active_path'] = request.GET.get('path', None)
    path_parts = []
    root_node = {'name': "Root", 'relative_path': None, 'absolute_path': "/"}
    if template_data['active_path'] == None:
        files = actions.view_mfs_directory("/")
        template_data['path_info'] = [root_node]
        # template_data['path_str'] = "/"
    else:
        if template_data['active_path'].startswith("/") is False:
            abs_path = "/" + template_data['active_path']
        else:
            abs_path = template_data['active_path']
        files = actions.view_mfs_directory(abs_path)
        path_parts = abs_path.split("/")[1:]
        path_info = []
        print(path_parts)
        for idx, pp in enumerate(path_parts):
            
            path_info.append({'name': pp, 'relative_path': None, 'absolute_path': "/".join(path_parts[0:idx + 1])})
        template_data['path_info'] = [ root_node ] + path_info
        print(template_data['path_info'])
        # template_data['path_str'] =  "/".join(template_data['path_info'][1:]) + "/"
    if files['Entries'] == None:
        template_data['files'] = []
    else:
        template_data['files'] = convert_entries_to_dict(files['Entries'], path_parts)
    
    template_data['selected_menu'] = 'home'    
    return render(request, "storage/index.html", template_data)

def upload_view(request):
    if request.method == 'GET':
        template_data = global_data
        template_data['selected_menu'] = 'upload'
        return render(request, "storage/upload.html", template_data)
    elif request.method == 'POST':
        print(request.FILES)
        return redirect(reverse('Tribes:storage-index'))

def create_path(request):
    url = request.POST['path']
    active_path = request.POST['active_path']
    url = "/" + active_path + "/" + url
    actions.create_mfs_directory(url)
    return redirect(reverse('Tribes:storage-index'))
