from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
import json
import os
from django.contrib import messages
from tribes_core import models
from tribes_django import settings
from tribes_core.lib.actions import (
    decode_event_and_set_to_model,
    create_new_subscription_from_follow_request,
    get_site_owner_name,
    get_all_message_drafts,
    get_draft_by_id,
    send_new_or_updated_messages
)
from tribes_core.lib import events

def manage_subs(request):
    if request.method == 'GET':
        count = models.Subscription.objects.count()
        res = HttpResponse(json.dumps({'subscription': count}))
        res['Content-Type'] = 'application/json'
        return res
    if request.method == 'POST':
        follow_event = decode_event_and_set_to_model(request.POST['data'], 'FOLLOW')
        if create_new_subscription_from_follow_request(follow_event) is True:
            return HttpResponse(200)
        else:
            return HttpResponse(422)
    if request.method == 'DELETE':
        pass

# @TODO: Write tests for show_info
def show_info(request):
    if request.method == 'GET':
        info = models.Person.objects.all()[0]
        key = json.loads(info.identifier)
        res = HttpResponse(json.dumps({
            'public_key': key,
            'sub': reverse('sub_url')
        }))
        res['Content-Type'] = 'application/json'
        return res
    else:
        return HttpResponse(422)


def read_messages(request):
    if request.method == 'POST':
        message_model = models.Message()
        decode_event_and_set_to_model(request.POST['data'], 'MESSAGE', message_model)
        message_model.save()
        return HttpResponse(200)
    else:
        return HttpResponse(422)

def generate_keys(request):
    pass


def new_post(request):
    return render(request, "admin/new_post.html")

def save_message(request):
    if request.method == 'POST':
        if 'id' in request.POST.keys():
            post_model = models.Post.objects.get(id=request.POST['id'])
            post_model.text = request.POST['content']
            post_model.save()
        else:
            post_model = models.Post()
            data = {}
            data['author'] = get_site_owner_name()
            data['text'] = request.POST['content']
            evt = events.POST.create_from_dict(data)
            evt.set_model(post_model)
            evt.save_event_to_db()
        return HttpResponse(200)
    else:
        return HttpResponse(422)

def view_message_drafts(request):
    drafts = get_all_message_drafts()
    return render(request, "admin/view_message_drafts.html", {'drafts': drafts})

def view_message(request, id):
    draft = get_draft_by_id(id)
    return render(request, "admin/edit_post.html", {'draft': draft })

def delete_message(request):
    if request.method == 'POST':
        if 'id' not in request.POST.keys():
            return HttpResponse(422)
        post = models.Post.objects.get(id=request.POST['id'])
        post.delete()
        return HttpResponse(200)
    else:
        return HttpResponse(422)

def publish_message(request):
    if request.method != 'POST':
        return HttpResponse(422)
    post_model = models.Post()
    data = {}
    data['author'] = get_site_owner_name()
    data['text'] = request.POST['content']
    evt = events.POST.create_from_dict(data)
    evt.set_model(post_model)
    evt.save_event_to_db()
    evt.model.is_draft = False
    evt.model.save()

    send_new_or_updated_messages(evt)
    return HttpResponse(200)
def view_subs(request):
    return render(request, "admin/view_subs.html")

def view_followed(request):
    return render(request, "admin/view_followed.html")