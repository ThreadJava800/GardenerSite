import datetime
import json
import random
import string
import threading
from datetime import timedelta
from sqlite3 import Date

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

import main
from main.forms import LoginForm, RedactForm, RegisterForm, ChangePassForm, ForgotPassForm, ConfirmMailForm, \
    RestorePassForm, ChangeEmail, ChangeUserName
from main.models import Note, Bookmark, Code, SiteStatistics


def main_page(req: HttpRequest) -> HttpResponse:
    # registering last visit on our website
    if req.user.is_authenticated:
        req.user.last_login = timezone.now()
        req.user.save()
    else:
        try:
            stat = SiteStatistics.objects.get(id__exact=1)
            stat.last_login = timezone.now()
            stat.save()
        except Exception:
            SiteStatistics.objects.create(id=1, last_login=datetime.datetime.today())
    notes = list()
    data = req.GET.get('request')
    if data is not None:
        for n in Note.objects.all():
            if n.title.lower().find(data.lower()) != -1 or data.lower().find(n.title.lower()) != -1:
                notes.append(n)
    else:
        notes = list(Note.objects.all())
    return render(req, 'user/main_page.html', context={'notes': notes})


def note_page(req: HttpRequest, note_id: int) -> HttpResponse:
    note = Note.objects.filter(id__exact=note_id)
    exists = False
    bookmark = int()
    last_watering = None
    last_fertilize = None
    if not req.user.is_anonymous:
        exists = is_bookmark_exists(req.user, note_id)
        bookmarks = req.user.bookmarks.all()
        for b in bookmarks:
            if Note.objects.get(title__exact=b.note).id == note_id:
                bookmark = b.id
        if bookmark != int():
            bookmark_obj = Bookmark.objects.get(id__exact=bookmark)
            last_watering = bookmark_obj.last_watering
            last_fertilize = bookmark_obj.last_fertilize
            if last_watering is None:
                last_watering = 'Вы ещё ни разу не поливали.'
            else:
                last_watering = f'Последний полив был {last_watering}.'
            if last_fertilize is None:
                last_fertilize = 'Вы ещё ни разу не удобряли.'
            else:
                last_fertilize = f'Последний раз вы удобряли {last_fertilize}.'
    return render(req, 'user/view_note_page.html',
                  context={'note': note[0], 'exists': exists, 'bookmark': bookmark, 'last_watering': last_watering,
                           'last_fertilize': last_fertilize})


def login_page(req: HttpRequest) -> HttpResponse:
    return render(req, 'user/login_page.html', context={'form': LoginForm()})


def login_click(req: HttpRequest):
    if req.method == 'POST':
        user_login = req.POST.get('login')
        user_password = req.POST.get('password')
        user = authenticate(username=user_login, password=user_password)
        if user is not None:
            login(req, user)
            return redirect('/')
    return redirect('/login_page')


def forgot_pass_page(req: HttpRequest) -> HttpResponse:
    return render(req, 'user/forgot_password.html', context={'form': ForgotPassForm()})


def send_confirmation_mail(req: HttpRequest) -> HttpResponse:
    if req.method == 'POST':
        mail = req.POST.get('mail')
        if len(User.objects.filter(email__exact=mail)) > 0:
            code = ''.join(random.choices(string.digits, k=6))
            email = EmailMessage('Сброс пароля на сайте kgarden.org', f'Введите этот код на сайте: {code}', to=[mail])
            email.send()
            code_model = Code()
            code_model.code = code
            try:
                code_model.id = Code.objects.last().id + 1
            except AttributeError:
                code_model.id = 1
            code_model.save()
            code_model.user.add(User.objects.get(email__exact=mail))
            thread = threading.Thread(target=code_model.timer)
            thread.start()
            form = ConfirmMailForm(initial={
                'code_id': code_model.id,
                'email': mail
            })
            return render(req, 'user/ask_code.html', context={'form': form})
    return redirect('/forgot_pass')


def restore_password_page(req: HttpRequest) -> HttpResponse:
    if req.method == 'POST':
        code = req.POST.get('code')
        code_id = req.POST.get('code_id')
        mail = req.POST.get('email')
        code_model = None
        try:
            code_model = Code.objects.get(id__exact=int(code_id))
        except:
            redirect(reverse('/forgot_pass', kwargs={'show': True}))
        if code_model.user.all()[0] == User.objects.get(email__exact=mail):
            if code == code_model.code:
                code_model.delete()
                return render(req, 'user/restore_password_page.html',
                              context={'form': RestorePassForm(initial={'email': mail})})
        return redirect('/forgot_pass')


def choose_new_pass_page(req: HttpRequest):
    if req.method == 'POST':
        mail = req.POST.get('email')
        new_pass = req.POST.get('new_password')
        rep_pass = req.POST.get('rep_password')
        user = User.objects.get(email__exact=mail)
        if new_pass == rep_pass:
            user.set_password(new_pass)
            user.save()
    return redirect('/login_page')


def register_page(req: HttpRequest) -> HttpResponse:
    return render(req, 'user/register_page.html', {'form': RegisterForm()})


def register(req: HttpRequest):
    if req.method == 'POST':
        username = req.POST.get('username')
        user_email = req.POST.get('mail')
        user_password = req.POST.get('password')
        user_rep_password = req.POST.get('rep_password')
        for u in User.objects.all():
            if u.username == username or u.email == user_email:
                return redirect('/register_page')
        if user_password == user_rep_password:
            user = User.objects.create_user(username=username, email=user_email, password=user_password)
            group = Group.objects.get(name='BasicUser')
            group.user_set.add(user)
            user.save()
            return redirect('/')
    return redirect('/register_page')


@login_required(login_url='/login_page')
def logout_click(req: HttpRequest):
    logout(req)
    return redirect('/')


@login_required(login_url='/login_page')
def personal_page(req: HttpRequest) -> HttpResponse:
    return render(req, 'user/personal_page.html',
                  context={'form_pass': ChangePassForm(), 'form_mail': ChangeEmail(initial={'email': req.user.email}),
                           'form_username': ChangeUserName(initial={'username': req.user.username})})


@login_required(login_url='/login_page')
def change_password(req: HttpRequest):
    if req.method == 'POST':
        password = req.POST.get('cur_password')
        new_pass = req.POST.get('new_password')
        rep_pass = req.POST.get('rep_password')
        user = authenticate(username=req.user.username, password=password)
        if user is not None and new_pass == rep_pass:
            user.set_password(new_pass)
            user.save()
    return redirect('/user')


@login_required(login_url='/login_page')
def change_mail(req: HttpRequest):
    if req.method == 'POST':
        mail = req.POST.get('email')
        for u in User.objects.all():
            if u.email == mail:
                return redirect('/user')
        req.user.email = mail
        req.user.save()
        return redirect('/user')


@login_required(login_url='/login_page')
def change_username(req: HttpRequest):
    if req.method == 'POST':
        username = req.POST.get('username')
        for u in User.objects.all():
            if u.username == username:
                return redirect('/user')
        req.user.username = username
        req.user.save()
        return redirect('/user')


@login_required(login_url='/login_page')
def bookmarks_page(req: HttpRequest) -> HttpResponse:
    bookmarks = req.user.bookmarks.all()
    data = []
    for b in bookmarks:
        note = Note.objects.get(title__exact=b.note)
        add = {
            'bookmark': b,
            'data': note.date,
            'id': note.id
        }
        data.append(add)
    return render(req, 'user/bookmarks_page.html', context={'data': data})


def check_if_allowed(user: User, bookmark_id: int) -> bool:
    allowed_ids = list()
    for b in Bookmark.objects.all():
        if b.user.all()[0] == user:
            allowed_ids.append(b.id)
    if bookmark_id not in allowed_ids:
        return False
    return True


@login_required(login_url='/login_page')
def delete_bookmark(req: HttpRequest, bookmark_id: int):
    if req.method == 'POST':
        if not check_if_allowed(req.user, bookmark_id):
            return HttpResponseForbidden()
        bookmark = Bookmark.objects.get(id__exact=bookmark_id)
        note = Note.objects.get(title__exact=bookmark.note)
        bookmark.delete()
        return render(req, 'user/note_block.html',
                      context={'note': note, 'exists': False, 'bookmark': None, 'last_watering': None,
                               'last_fertilize': None})
    return HttpResponseBadRequest()


def is_bookmark_exists(user: User, note_id: int) -> bool:
    note_exists = False
    try:
        bookmarks = Bookmark.objects.filter(user__exact=user)
        for bookmark in bookmarks:
            associated_note = Note.objects.get(title__exact=bookmark.note)
            if associated_note.id == note_id:
                note_exists = True
                break
    except main.models.Bookmark.DoesNotExist:
        note_exists = False
    return note_exists


@login_required(login_url='/login_page')
def add_bookmark(req: HttpRequest, note_id: int):
    if req.method == 'POST':
        if not is_bookmark_exists(req.user, note_id):
            note = Note.objects.get(id__exact=note_id)
            bookmark = Bookmark()
            bookmark.note = note.title
            bookmark.id = Bookmark.objects.last().id + 1
            bookmark.save()
            bookmark.user.add(req.user)
            return render(req, 'user/note_block.html',
                          context={'note': note, 'exists': True, 'bookmark': bookmark.id,
                                   'last_watering': 'Вы ещё ни разу не поливали.',
                                   'last_fertilize': 'Вы ещё ни разу не удобряли.'})
        return HttpResponseForbidden()
    return HttpResponseBadRequest()


@login_required(login_url='/login_page')
def water(req: HttpRequest, bookmark_id: int):
    if req.method == "POST":
        if not check_if_allowed(req.user, bookmark_id):
            return HttpResponseForbidden()
        bookmark = Bookmark.objects.get(id__exact=bookmark_id)
        bookmark.last_watering = Date.today()
        bookmark.save()
        water_period = Note.objects.get(title__exact=bookmark.note).watering_period
        return HttpResponse(
            json.dumps({
                'last_watering': f'Последний полив был {bookmark.last_watering}.',
                'last_watering_for_nearest': f'Полив через {water_period} дней.'
            }),
            content_type="application/json"
        )
    return HttpResponseBadRequest()


@login_required(login_url='/login_page')
def delete_account(req: HttpRequest):
    for b in req.user.bookmarks.all():
        b.delete()
    for c in req.user.code.all():
        c.delete()
    req.user.delete()
    return redirect('/')


@login_required(login_url='/login_page')
def nearest_watering(req: HttpRequest):
    data = list()
    try:
        values = req.user.bookmarks.all()
        for val in values:
            if val.last_watering is not None:
                ass_note = Note.objects.get(title__exact=val.note)
                water_date = val.last_watering + timedelta(ass_note.watering_period)
                days = (water_date - datetime.datetime.today().date()).days  # days left till watering
                num = days
                if days < 0:
                    days = f'Вы пропустили полив, он был {abs(days)} дней назад'
                elif days == 0:
                    days = f'Полив сегодня!'
                else:
                    days = f'Полив через {days} дней'
                data.append({
                    'title': ass_note.title,
                    'days': days,
                    'days_num': num,
                    'bookmark': val.id
                })
        data = sorted(data, key=lambda k: k['days_num'])
    except Exception:
        pass
    return render(req, 'user/nearest_waterings.html', context={'data': data})


@login_required(login_url='/login_page')
def nearest_fertilize(req: HttpRequest):
    data = list()
    try:
        values = req.user.bookmarks.all()
        for val in values:
            if val.last_fertilize is not None:
                ass_note = Note.objects.get(title__exact=val.note)
                fertilized_date = val.last_fertilize + timedelta(ass_note.fertilize_period)
                days = (fertilized_date - datetime.datetime.today().date()).days  # days left till fertilizing
                num = days
                if days < 0:
                    days = f'Вы пропустили процесс удобрения, он был {abs(days)} дней назад'
                elif days == 0:
                    days = f'Удобрить желательно сегодня!'
                else:
                    days = f'Удобрять через {days} дней'
                data.append({
                    'title': ass_note.title,
                    'days': days,
                    'days_num': num,
                    'bookmark': val.id
                })
        data = sorted(data, key=lambda k: k['days_num'])
    except Exception:
        pass
    return render(req, 'user/nearest_fertilize.html', context={'data': data})


@login_required(login_url='/login_page')
def fertilize(req: HttpRequest, bookmark_id: int):
    if req.method == 'POST':
        if not check_if_allowed(req.user, bookmark_id):
            return HttpResponseForbidden()
        bookmark = Bookmark.objects.get(id__exact=bookmark_id)
        bookmark.last_fertilize = Date.today()
        bookmark.save()
        fertilize_period = Note.objects.get(title__exact=bookmark.note).fertilize_period
        return HttpResponse(
            json.dumps({
                'last_fertilize': f'Последний раз вы удобряли {bookmark.last_fertilize}.',
                'last_fertilize_for_nearest': f'В следующий раз удобрять через {fertilize_period} дней.'
            }),
            content_type="application/json"
        )
    return HttpResponseBadRequest()


@permission_required('main.note.can_add_note', login_url='/login_page')
def moder_main_page(req: HttpRequest) -> HttpResponse:
    notes = list(Note.objects.all())
    return render(req, 'moder/moder_main.html', context={'notes': notes})


@permission_required('main.note.can_change_note', login_url='/login_page')
def moder_redact_page(req: HttpRequest, note_id: int) -> HttpResponse:
    note = Note.objects.filter(id__exact=note_id)
    form = RedactForm(initial={
        'id': note[0].id,
        'title': note[0].title,
        'photo': note[0].photo,
        'text': note[0].text,
        'water_period': note[0].watering_period,
        'fertilize_period': note[0].fertilize_period
    })
    context = {
        'form': form,
        'note_id': note[0].id,
        'note_date': note[0].date
    }
    return render(req, 'moder/moder_redact_page.html', context=context)


@permission_required('main.note.can_change_note', login_url='/login_page')
def redact_note(req: HttpRequest):
    if req.method == 'POST':
        note = Note.objects.get(id__exact=int(req.POST.get('id')))
        note.title = req.POST.get('title')
        note.text = req.POST.get('text')
        note.photo = req.POST.get('photo')
        note.watering_period = req.POST.get('water_period')
        note.fertilize_period = req.POST.get('fertilize_period')
        note.save()
    return redirect('/moder')


@permission_required('main.note.can_add_note', login_url='/login_page')
def moder_add_note_page(req: HttpRequest) -> HttpResponse:
    return render(req, 'moder/add_note_page.html', context={'form': RedactForm()})


@permission_required('main.note.can_add_note', login_url='/login_page')
def add_note(req: HttpRequest):
    if req.method == 'POST':
        title = req.POST.get('title')
        text = req.POST.get('text')
        photo = req.POST.get('photo')
        note = Note()
        note.title = title
        note.text = text
        note.photo = photo
        note.date = Date.today()
        note.watering_period = req.POST.get('water_period')
        note.fertilize_period = req.POST.get('fertilize_period')
        note.save()
        return redirect('/moder')
    return redirect('/moder/add')


@permission_required('main.note.can_delete_note', login_url='/login_page')
def moder_delete_note_page(req: HttpRequest, note_id: int):
    note = Note.objects.get(id__exact=note_id)
    note.delete()
    return redirect('/moder')


@permission_required('main.note.can_delete_note', login_url='/login_page')
def moder_view_all(req: HttpRequest) -> HttpResponse:
    users = User.objects.all().order_by('last_login')
    return render(req, 'moder/moder_all.html',
                  context={'data': users, 'last_login': SiteStatistics.objects.get(id__exact=1).last_login})
