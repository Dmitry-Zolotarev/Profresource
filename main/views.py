from django.views.decorators.http import require_http_methods
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import re


# Слушатели
def слушатели_view(request):
    if request.method == 'POST':
        фамилия = request.POST.get('Фамилия')
        имя = request.POST.get('Имя')
        отчество = request.POST.get('Отчество')
        дата_рождения = request.POST.get('Дата_рождения')
        пол = request.POST.get('Пол')
        серия_паспорта = request.POST.get('Серия_паспорта')
        номер_паспорта = request.POST.get('Номер_паспорта')
        гражданство_id = request.POST.get('Гражданство')
        номер_СНИЛС = request.POST.get('Номер_СНИЛС')
        ИНН = request.POST.get('ИНН')
        телефон = request.POST.get('Телефон')
        email = request.POST.get('Email')

        error_found = False

        # Проверки только для граждан РФ (id = 1)
        if гражданство_id == "1":
            if not re.fullmatch(r'\d{4}', серия_паспорта or ''):
                messages.warning(request, "Серия паспорта РФ должна состоять из 4 цифр.")
                error_found = True
            if not re.fullmatch(r'\d{6}', номер_паспорта or ''):
                messages.warning(request, "Номер паспорта РФ должен состоять из 6 цифр.")
                error_found = True

        if Слушатели.objects.filter(
            Фамилия=фамилия,
            Имя=имя,
            Отчество=отчество,
            Дата_рождения=дата_рождения,
            ИНН=ИНН
        ).exists():
            error_found = True

        if not error_found:
            слушатель = Слушатели(
                Фамилия=фамилия,
                Имя=имя,
                Отчество=отчество,
                Дата_рождения=дата_рождения,
                Пол=get_object_or_404(Пол, id=пол),
                Серия_паспорта=серия_паспорта,
                Номер_паспорта=номер_паспорта,
                Номер_СНИЛС=номер_СНИЛС,
                ИНН=ИНН,
                Телефон=телефон,
                Email=email
            )
            if гражданство_id:
                слушатель.Гражданство_id = гражданство_id
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
            название = request.POST.get('Название')
            курс = request.POST.get('Курс')
            начало = request.POST.get('Дата_начала_курса')
            окончание = request.POST.get('Дата_окончания_курса')

            if Группы.objects.filter(
                    Название=название,
                    Курс_id=курс,
                    Дата_начала_курса=начало,
                    Дата_окончания_курса=окончание
            ).exists():
                messages.warning(request, "Такой курс уже есть в базе данных!")
            else:
                Группы.objects.create(
                    Название=название,
                    Курс=get_object_or_404(Курсы, id=курс),
                    Дата_начала_курса=начало,
                    Дата_окончания_курса=окончание
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
        название = request.POST.get('Название')
        ссылка = request.POST.get('Ссылка')
        курс_id = request.POST.get('Курс')
        тип_id = request.POST.get('Тип')
        if Материалы_курсов.objects.filter(
                Название=название,
                Ссылка_на_материал=ссылка,
                Курс_id=курс_id,
                Тип_id=тип_id,
            ).exists():
            messages.warning(request, "Такой материал уже есть в базе данных!")
        else:
            Материалы_курсов.objects.create(
                Название=название,
                Ссылка_на_материал=ссылка,
                Курс_id=курс_id,
                Тип_id=тип_id,
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
            название = request.POST.get('Название')
            инн = request.POST.get('ИНН')
            огрн = request.POST.get('ОГРН')
            email = request.POST.get('Email')
            if Организации.objects.filter(
                    Название=название,
                    ИНН=инн,
                    ОГРН=огрн,
                    Email=email
                ).exists():
                messages.warning(request, "Эта организация уже есть в базе данных!")
            else:
                Организации.objects.create(
                    Название=название,
                    ИНН=инн,
                    ОГРН=огрн,
                    Email=email
                )
                return redirect('organisation_list')
        elif 'submit_привязка' in request.POST:
            слушатель = get_object_or_404(Слушатели, id=request.POST.get('Слушатель'))
            организация = get_object_or_404(Организации, id=request.POST.get('Организация'))
            if Человек_организация.objects.filter(
                    Слушатель=слушатель,
                    Организация=организация,
            ).exists():
                messages.warning(request, "Эта привязка уже есть в базе данных!")
            else:
                Человек_организация.objects.create(
                    Слушатель=слушатель,
                    Организация=организация,
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