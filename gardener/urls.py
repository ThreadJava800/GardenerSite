"""gardener URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main.views import main_page, note_page, login_page, moder_main_page, moder_redact_page, \
    moder_add_note_page, moder_delete_note_page, register_page, register, logout_click, login_click, add_note, \
    redact_note, personal_page, change_password, forgot_pass_page, send_confirmation_mail, bookmarks_page, \
    delete_bookmark, add_bookmark, restore_password_page, choose_new_pass_page, water, moder_view_all, change_mail, \
    change_username, delete_account, nearest_watering, fertilize, nearest_fertilize

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page),
    path('<int:note_id>', note_page),
    path('user', personal_page),
    path('bookmarks', bookmarks_page),
    path('delete_bookmark/<int:bookmark_id>', delete_bookmark),
    path('star/<int:note_id>', add_bookmark),
    path('change_pass', change_password),
    path('change_mail', change_mail),
    path('change_username', change_username),
    path('delete_acc', delete_account),
    path('forgot_pass', forgot_pass_page),
    path('confirm_personality', send_confirmation_mail),
    path('restore_pass', restore_password_page),
    path('set_new_pass', choose_new_pass_page),
    path('nearest', nearest_watering),
    path('fertilize_nearest', nearest_fertilize),
    path('water/<int:bookmark_id>', water),
    path('fertilize/<int:bookmark_id>', fertilize),
    path('login_page', login_page),
    path('login', login_click),
    path('register_page', register_page),
    path('register', register),
    path('logout', logout_click),
    path('moder', moder_main_page),
    path('moder/<int:note_id>', moder_redact_page),
    path('moder/change', redact_note),
    path('moder/add', moder_add_note_page),
    path('moder/delete/<int:note_id>', moder_delete_note_page),
    path('moder/add/new', add_note),
    path('moder/all', moder_view_all),
]
