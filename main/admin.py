from django.contrib import admin
from main.models import Note, Bookmark, Code, SiteStatistics

admin.site.register(Note)
admin.site.register(Bookmark)
admin.site.register(Code)
admin.site.register(SiteStatistics)
