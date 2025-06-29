from django.views.decorators.http import require_http_methods
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import re

# Слушатели
def слушатели_view(request):
    error_found = False
    if request.method == 'POST':
        # Проверки только для граждан РФ (id = 1)
        if request.POST.get('Гражданство') == "1":
            if not re.fullmatch(r'\d{4}', request.POST.get('Серия_паспорта') or ''):
                messages.warning(request, "Серия паспорта РФ должна состоять из 4 цифр.")
                error_found = True
            if not re.fullmatch(r'\d{6}', request.POST.get('Номер_паспорта') or ''):
                messages.warning(request, "Номер паспорта РФ должен состоять из 6 цифр.")
                error_found = True
        if Слушатели.objects.filter(ИНН=request.POST.get('ИНН')).exists():
            messages.warning(request, "Человек с этим ИНН уже есть в базе данных!")
            error_found = True
        if Слушатели.objects.filter(Номер_СНИЛС=request.POST.get('Номер_СНИЛС')).exists():
            messages.warning(request, "Человек с этим СНИЛС уже есть в базе данных!")
            error_found = True
        if not error_found:
            слушатель = Слушатели(
                Фамилия=request.POST.get('Фамилия'),
                Имя=request.POST.get('Имя'),
                Отчество=request.POST.get('Отчество'),
                Дата_рождения=request.POST.get('Дата_рождения'),
                Пол_id=request.POST.get('Пол'),
                Гражданство_id=request.POST.get('Гражданство'),
                Серия_паспорта=request.POST.get('Серия_паспорта'),
                Номер_паспорта=request.POST.get('Номер_паспорта'),
                Номер_СНИЛС=request.POST.get('Номер_СНИЛС'),
                ИНН=request.POST.get('ИНН'),
                Телефон=request.POST.get('Телефон'),
                Email=request.POST.get('Email'),
            )
            слушатель.save()
            return redirect('student_list')
    return render(request, 'main/ListenerList.html', {
        'слушатели': Слушатели.objects.all(),
        'страны': Страны.objects.all(),
        'полы': Пол.objects.all(),
    })
def группы_view(request):
    if request.method == 'POST':
        if 'submit_группа' in request.POST:
            if Группы.objects.filter(
                    Название=request.POST.get('Название'),
                    Курс_id=request.POST.get('Курс'),
                    Дата_начала_курса=request.POST.get('Дата_начала_курса'),
                    Дата_окончания_курса=request.POST.get('Дата_окончания_курса')
            ).exists():
                messages.warning(request, "Такой курс уже есть в базе данных!")
            else:
                Группы.objects.create(
                    Название=request.POST.get('Название'),
                    Курс_id=request.POST.get('Курс'),
                    Дата_начала_курса=request.POST.get('Дата_начала_курса'),
                    Дата_окончания_курса=request.POST.get('Дата_окончания_курса')
                )
                return redirect('group_list')
        elif 'submit_привязка' in request.POST:
            слушатель = get_object_or_404(Слушатели, id=request.POST.get('Слушатель'))
            группа = get_object_or_404(Группы, id=request.POST.get('Группа'))
            if Человек_группа.objects.filter(
                Слушатель=слушатель,
                Группа=группа,
            ).exists():
                messages.warning(request, "Эта привязка уже есть в базе данных!")
            else:
                Человек_группа.objects.create(
                    Слушатель=слушатель,
                    Группа=группа,
                )
                return redirect('group_list')
    #GET-запрос
    return render(request, 'main/GroupList.html', {
        'курсы': Курсы.objects.all(),
        'слушатели': Слушатели.objects.all(),
        'группы': Группы.objects.all(),
        'Человек_группа': Человек_группа.objects.all(),
    })
def курсы_view(request):
    if request.method == 'POST':
        тип = get_object_or_404(Типы_курсов, id=request.POST.get('Тип'))
        название = request.POST.get('Название')
        if Курсы.objects.filter(Тип=тип,Название=название,).exists():
            messages.warning(request, "Такой курс уже есть в базе данных!")
        else:
            Курсы.objects.create(Тип=тип, Название=название)
            return redirect('course_list')
    #GET-запрос
    return render(request, 'main/CourseList.html', {
        'типы_курсов': Типы_курсов.objects.all(),
        'курсы': Курсы.objects.all(),
    })

def материалы_view(request):
    if request.method == 'POST':
        if Материалы_курсов.objects.filter(
                Название=request.POST.get('Название'),
                Ссылка_на_материал=request.POST.get('Ссылка'),
                Курс_id=request.POST.get('Курс'),
                Тип_id=request.POST.get('Тип'),
            ).exists():
            messages.warning(request, "Такой материал уже есть в базе данных!")
        else:
            Материалы_курсов.objects.create(
                Название=request.POST.get('Название'),
                Ссылка_на_материал=request.POST.get('Ссылка'),
                Курс_id=request.POST.get('Курс'),
                Тип_id=request.POST.get('Тип'),
            )
            return redirect('material_list')
    return render(request, 'main/MaterialList.html', {
        'материалы': Материалы_курсов.objects.all(),
        'курсы': Курсы.objects.all(),
        'типы': Типы_материалов.objects.all(),
    })
def организации_view(request):
    if request.method == 'POST':
        if 'submit_организация' in request.POST:
            if Организации.objects.filter(
                    Название=request.POST.get('Название'),
                    ИНН=request.POST.get('ИНН'),
                    ОГРН=request.POST.get('ОГРН'),
                    Email=request.POST.get('Email')
                ).exists():
                messages.warning(request, "Эта организация уже есть в базе данных!")
            else:
                Организации.objects.create(
                    Название=request.POST.get('Название'),
                    ИНН=request.POST.get('ИНН'),
                    ОГРН=request.POST.get('ОГРН'),
                    Email=request.POST.get('Email')
                )
                return redirect('organisation_list')
        elif 'submit_привязка' in request.POST:
            if Человек_организация.objects.filter(
                    Слушатель_id=request.POST.get('Слушатель'),
                    Организация_id=request.POST.get('Организация'),
                    Должность=request.POST.get('Должность'),
            ).exists():
                messages.warning(request, "Эта привязка уже есть в базе данных!")
            else:
                Человек_организация.objects.create(
                    Слушатель_id=request.POST.get('Слушатель'),
                    Организация_id=request.POST.get('Организация'),
                    Должность=request.POST.get('Должность'),
                )
                return redirect('organisation_list')
    #GET-запрос
    return render(request, 'main/OrganisationList.html', {
        'слушатели': Слушатели.objects.all(),
        'организации': Организации.objects.all(),
        'привязки': Человек_организация.objects.all(),
    })
@require_http_methods(["POST"])
def delete_listener(request, id):
    listener = get_object_or_404(Слушатели, id=id)
    if (Человек_группа.objects.filter(Слушатель=listener).exists() or
        Человек_организация.objects.filter(Слушатель=listener).exists() or
        Адреса.objects.filter(id_студента=listener).exists()):
        messages.error(request, "Удаление отменено - есть зависимые записи.")
        return redirect('student_list')
    listener.delete()
    return redirect('student_list')

@require_http_methods(["POST"])
def delete_group(request, id):
    group = get_object_or_404(Группы, id=id)
    if Человек_группа.objects.filter(Группа=group).exists():
        messages.error(request, "Удаление отменено - есть зависимые записи!")
        return redirect('group_list')
    group.delete()
    return redirect('group_list')

@require_http_methods(["POST"])
def delete_group_linking(request, id):
    get_object_or_404(Человек_группа, id=id).delete()
    return redirect('group_list')

@require_http_methods(["POST"])
def delete_course(request, id):
    course = get_object_or_404(Курсы, id=id)
    if (Группы.objects.filter(Курс=course).exists() or
        Материалы_курсов.objects.filter(Курс=course).exists()):
        messages.error(request, "Удаление отменено - есть зависимые записи!")
        return redirect('course_list')
    course.delete()
    return redirect('course_list')

@require_http_methods(["POST"])
def delete_material(request, id):
    get_object_or_404(Материалы_курсов, id=id).delete()
    return redirect('material_list')
@require_http_methods(["POST"])
def delete_organisation(request, id):
    org = get_object_or_404(Организации, id=id)
    if Человек_организация.objects.filter(Организация=org).exists():
        messages.error(request, "Удаление отменено - есть зависимые записи!")
        return redirect('organisation_list')
    org.delete()
    return redirect('organisation_list')
@require_http_methods(["POST"])
def delete_org_linking(request, id):
    get_object_or_404(Человек_организация, id=id).delete()
    return redirect('organisation_list')