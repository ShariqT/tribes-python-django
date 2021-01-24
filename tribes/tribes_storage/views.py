from django.shortcuts import render, redirect
from tribes_storage.lib import actions
from django.urls import reverse
import json, io


global_data = {}
global_data['welcome_message'] = 'Storage'
global_data['appname'] = 'STOR'

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

FILE_TYPES = {
    'txt':'txt',
    'jpeg':'img',
    'pdf':'pdf',
    'jpg':'img',
    'png':'img',
    'rft':'txt',
    'doc':'word',
    'docx':'word',
    'gif':'img',
    'zip':'archive',
    'mp4':'video',
    'avi':'video',
    'mov':'video'

}
def determine_file_type(filename):
    filename_parts = filename.split(".")
    ret_val = ''
    try:
        ret_val = FILE_TYPES[filename_parts[1]]
    except KeyError:
        ret_val = 'file'
    return ret_val

def convert_entries_to_dict(entries, path):
    if len(path) == 0:
        ret_list = [{'Name': '/', 'Type': 'directory', 'Path': None }]
    else:
        ret_list = [{'Name': '../', 'Type': 'directory', 'Path':  "/".join(path[0:-1]) }]
    for entry in entries:
        pathstr = "/".join(path) + "/" + entry['Name']
        if pathstr.startswith("/") is True:
            res = actions.view_mfs_file_info("/".join(path) + "/" + entry['Name'])
        else:
            res = actions.view_mfs_file_info("/" + pathstr)

        if res['Type'] == 'directory':
            file_type = res['Type']
        else:
            file_type = determine_file_type(entry['Name'])
        ret_list.append({
            'Name': entry['Name'],
            'Type': file_type,
            'Size': res['Size'],
            'Hash': res['Hash'],
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
    if files['Entries'] == None:
        template_data['files'] = []
    else:
        template_data['files'] = convert_entries_to_dict(files['Entries'], path_parts)
    print(template_data['files'])
    template_data['selected_menu'] = 'home'    
    return render(request, "storage/index.html", template_data)

def upload_view(request):
    if request.method == 'GET':
        template_data = global_data
        template_data['selected_menu'] = 'upload'
        return render(request, "storage/upload.html", template_data)
    elif request.method == 'POST':
        print(request.FILES['file'])
        print(request.POST)
        if request.POST['currentPath'].startswith("/") is True:
            url = request.POST['currentPath'] + "/" + request.FILES['file'].name
        else:
            url  = "/" + request.POST['currentPath'] + "/" + request.FILES['file'].name
        data = io.BytesIO(request.FILES['file'].read())
        print(data.getbuffer().nbytes)
        res = actions.create_mfs_file(url, data)
        print(res)
        return redirect(reverse('Tribes:storage-index') + "?path=" + request.POST['currentPath'])

def create_path(request):
    url = request.POST['path']
    active_path = request.POST['active_path']
    url = "/" + active_path + "/" + url
    actions.create_mfs_directory(url)
    return redirect(reverse('Tribes:storage-index'))
