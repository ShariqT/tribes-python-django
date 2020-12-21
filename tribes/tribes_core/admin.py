from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from tribes_core import models
from tribes_core import views
from tribes_front_matter import views as front_matter_views


# Register your models here.
class TribesAdminSite(admin.AdminSite):
    index_template = "admin/index.html"
    login_template = "admin/login.html"
    index_title = 'Tribes Admin'
    site_header = 'Tribes'
    def get_urls(self):
        urls = super().get_urls()
        tribe_urls = [
            url('generate_keys', self.admin_view(views.generate_keys), name='generate_keys'),
            url('new-post', self.admin_view(views.new_post), name='new-post'),
            url('save/message', self.admin_view(views.save_message), name='save-message'),
            url('view/message/drafts', self.admin_view(views.view_message_drafts), name='view-drafts'),
            path('view/message/<int:id>', self.admin_view(views.view_message), name='view-message'),
            path('view/delete/draft', self.admin_view(views.delete_message), name='delete-draft'),
            url('publish/message', self.admin_view(views.publish_message), name='publish-message'),
            url('view-subs', self.admin_view(views.view_subs), name='view-subs'),
            url('view-followed', self.admin_view(views.view_followed), name='view-followed'),
            url('front-matter/config', self.admin_view(front_matter_views.view_config), name='front-matter-config-file'),
            url('front-matter/publish', self.admin_view(front_matter_views.view_publish_feedback), name='front-matter-publish'),
            url('front-matter', self.admin_view(front_matter_views.index), name='front-matter-index'),

        ]
        return tribe_urls + urls


admin_site = TribesAdminSite(name="Tribes")
