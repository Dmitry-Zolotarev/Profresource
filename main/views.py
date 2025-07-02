from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Q
import json, re
from io import BytesIO
from datetime import date
from datetime import datetime
from docx import Document
from docx.shared import Mm, Pt, Inches
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
import openpyxl

from .models import (
    Слушатели, Пол, Группы, Курсы, Типы_курсов,
    Материалы_курсов, Типы_материалов,
    Организации, Человек_группа, Человек_организация,
    Статусы, Месяцы, Страны
)

def слушатели_view(request):
    if request.method == 'POST':
        error_found = False
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
        if not error_found:
            Слушатели(
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
            ).save()
            return redirect('student_list')
    return render(request, 'main/ListenerList.html', {
        'слушатели': Слушатели.objects.all(),
        'страны': Страны.objects.all(),
        'полы': Пол.objects.all(),
    })
# --- Группы ---
def группы_view(request):
    if request.method == 'POST':
        if 'submit_группа' in request.POST:
            if Группы.objects.filter(
                    Курс_id=request.POST.get('Курс'),
                    Дата_начала_курса=request.POST.get('Дата_начала_курса'),
                    Дата_окончания_курса=request.POST.get('Дата_окончания_курса')
            ).exists():
                messages.warning(request, "Такой курс уже есть в базе данных!")
            else:
                Группы.objects.create(
                    Курс_id=request.POST.get('Курс'),
                    Дата_начала_курса=request.POST.get('Дата_начала_курса'),
                    Дата_окончания_курса=request.POST.get('Дата_окончания_курса')
                )
                return redirect('group_list')
        elif 'submit_привязка' in request.POST:
            if Человек_группа.objects.filter(
                Слушатель_id=request.POST.get('Слушатель'),
                Группа_id=request.POST.get('Группа'),
            ).exists():
                messages.warning(request, "Эта привязка уже есть в базе данных!")
            else:
                Человек_группа.objects.create(
                    Слушатель_id=request.POST.get('Слушатель'),
                    Группа_id=request.POST.get('Группа'),
                    Статус_id=request.POST.get('Статус'),
                )
                return redirect('group_list')
    return render(request, 'main/GroupList.html', {
        'курсы': Курсы.objects.all(),
        'слушатели': Слушатели.objects.all(),
        'группы': Группы.objects.all(),
        'Человек_группа': Человек_группа.objects.all(),
        'статусы': Статусы.objects.all(),
    })
# --- Курсы ---
def курсы_view(request):
    if request.method == 'POST':
        if Курсы.objects.filter(
                Тип_id=request.POST.get('Тип'),
                Название=request.POST.get('Название'),
        ).exists():
            messages.warning(request, "Такой курс уже есть в базе данных!")
        else:
            Курсы.objects.create(
                Тип_id=request.POST.get('Тип'),
                Название=request.POST.get('Название'),
                Объём_часов=request.POST.get('Объём_часов'),
            )
            return redirect('course_list')
    return render(request, 'main/CourseList.html', {
        'типы_курсов': Типы_курсов.objects.all(),
        'курсы': Курсы.objects.all(),
    })
def страны_view(request):
    if request.method == 'POST':
        if Страны.objects.filter(
                Краткое_название=request.POST.get('Краткое_название'),
                Телефонный_код=request.POST.get('Телефонный_код'),
        ).exists():
            messages.warning(request, "Такой курс уже есть в базе данных!")
        else:
            Страны.objects.create(
                Название=request.POST.get('Название'),
                Краткое_название=request.POST.get('Краткое_название'),
                Телефонный_код=request.POST.get('Телефонный_код'),
            )
            return redirect('country_list')
    return render(request, 'main/CountryList.html', {
        'страны': Страны.objects.all(),
    })

# --- Материалы ---
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
# --- Организации ---
def организации_view(request):
    if request.method == 'POST':
        if 'submit_организация' in request.POST:
            if Организации.objects.filter(ИНН=request.POST.get('ИНН')).exists():
                messages.warning(request, f"Организация с ИНН {request.POST.get('ИНН')} уже есть в базе данных!")
            elif Организации.objects.filter(ОГРН=request.POST.get('ОГРН')).exists():
                messages.warning(request, f"Организация с ОГРН {request.POST.get('ОГРН')} уже есть в базе данных!")
            else:
                Организации.objects.create(
                    Название=request.POST.get('Название'),
                    ИНН=request.POST.get('ИНН'),
                    ОГРН=request.POST.get('ОГРН'),
                    Телефон=request.POST.get('Телефон'),
                    Email=request.POST.get('Email'),
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
    return render(request, 'main/OrganisationList.html', {
        'слушатели': Слушатели.objects.all(),
        'организации': Организации.objects.all(),
        'привязки': Человек_организация.objects.all(),
    })

def delete_listener(request, id):
    listener = get_object_or_404(Слушатели, id=id)
    if Человек_группа.objects.filter(Слушатель=listener).exists() \
       or Человек_организация.objects.filter(Слушатель=listener).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи.")
    else:
        listener.delete()
    return redirect('student_list')

def delete_group(request, id):
    group = get_object_or_404(Группы, id=id)
    if Человек_группа.objects.filter(Группа=group).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        group.delete()
    return redirect('group_list')
def delete_group_linking(request, id):
    get_object_or_404(Человек_группа, id=id).delete()
    return redirect('group_list')
def delete_course(request, id):
    course = get_object_or_404(Курсы, id=id)
    if Группы.objects.filter(Курс=course).exists() \
       or Материалы_курсов.objects.filter(Курс=course).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        course.delete()
    return redirect('course_list')

def delete_country(request, id):
    country = get_object_or_404(Страны, id=id)
    if Слушатели.objects.filter(Гражданство=country).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        country.delete()
    return redirect('country_list')

def delete_material(request, id):
    get_object_or_404(Материалы_курсов, id=id).delete()
    return redirect('material_list')

def delete_organisation(request, id):
    org = get_object_or_404(Организации, id=id)
    if Человек_организация.objects.filter(Организация=org).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        org.delete()
    return redirect('organisation_list')

def delete_org_linking(request, id):
    get_object_or_404(Человек_организация, id=id).delete()
    return redirect('organisation_list')

def today_date():
    month = Месяцы.objects.get(id=date.today().month).Название
    return f"{date.today().day} {month} {date.today().year} г."

def export_listeners_DOCX(request):
    try:
        doc = Document()
        section = doc.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Mm(297)
        section.page_height = Mm(210)
        # Уменьшение отступов слева и справа
        section.left_margin = Mm(10)
        section.right_margin = Mm(10)
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)
        # Название организации (3 строки)
        org_paragraph = doc.add_paragraph()
        org_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = org_paragraph.add_run(
            'Автономная некоммерческая организация дополнительного профессионального образования\n')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run = org_paragraph.add_run('«Сибирская академия профессионального обучения»')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True

        date = doc.add_paragraph("Отчёт от " + today_date())
        date.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date.runs[0].font.name = 'Times New Roman'
        date.runs[0].font.size = Pt(14)

        heading = doc.add_paragraph("Слушатели")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading_run = heading.runs[0]
        heading_run.font.name = 'Times New Roman'
        heading_run.font.size = Pt(14)

        headers = ['ФИО', 'Дата рождения', 'Пол', 'Гражданство', 'Серия паспорта', 'Номер паспорта', 'ИНН', 'СНИЛС']
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        for i, header in enumerate(headers):
            paragraph = table.rows[0].cells[i].paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            header = paragraph.add_run(header)
            header.font.name = 'Times New Roman'
            header.font.size = Pt(12)

        слушатели = Слушатели.objects.filter(id__in=json.loads(request.body).get('ids', [])).annotate(
            Пол_Название=F('Пол__Название'),
            Гражданство_Название=F('Гражданство__Краткое_название')
        )
        for s in слушатели:
            row = table.add_row().cells
            row[0].text = f"{s.Фамилия} {s.Имя} {s.Отчество or ''}"
            row[1].text = s.Дата_рождения.strftime('%d.%m.%Y') if s.Дата_рождения else ''
            row[2].text = s.Пол_Название or ''
            row[3].text = s.Гражданство_Название or ''
            row[4].text = s.Серия_паспорта or ''
            row[5].text = s.Номер_паспорта or ''
            row[6].text = s.ИНН or ''
            row[7].text = s.Номер_СНИЛС or ''
            # Установка шрифта
            for cell in row:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(12)

        director = doc.add_paragraph("\nДиректор" + (' ' * 50) +"В.Н. Котлов")
        director.alignment = WD_ALIGN_PARAGRAPH.CENTER
        director.runs[0].font.name = 'Times New Roman'
        director.runs[0].font.size = Pt(14)
        # Сохранение и ответ
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)

        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="Слушатели.docx"'
        return response

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
def export_groups_DOCX(request):
    try:
        doc = Document()
        section = doc.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Mm(297)
        section.page_height = Mm(210)
        section.left_margin = Mm(10)
        section.right_margin = Mm(10)
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)

        org_paragraph = doc.add_paragraph()
        org_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = org_paragraph.add_run('Автономная некоммерческая организация дополнительного профессионального образования\n')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run = org_paragraph.add_run('«Сибирская академия профессионального обучения»')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True

        date = doc.add_paragraph("Отчёт от " + today_date())
        date.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date.runs[0].font.name = 'Times New Roman'
        date.runs[0].font.size = Pt(14)

        heading = doc.add_paragraph("Группы и их состав")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading.runs[0].font.name = 'Times New Roman'
        heading.runs[0].font.size = Pt(14)

        body_unicode = request.body.decode('utf-8')
        ids = json.loads(body_unicode).get('ids', [])
        группы = Группы.objects.filter(id__in=ids).select_related('Курс', 'Курс__Тип')

        for группа in группы:
            # Заголовок группы
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(f"Группа №{группа.id} — {группа.Курс.Название} ({группа.Курс.Тип.Название})\n").bold = True
            p.add_run(f"Срок обучения: {группа.Дата_начала_курса.strftime('%d.%m.%Y')} - {группа.Дата_окончания_курса.strftime('%d.%m.%Y')}")
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)

            привязки = Человек_группа.objects.filter(Группа=группа).select_related('Слушатель', 'Статус')
            if not привязки.exists():
                paragraph = doc.add_paragraph("Слушателей нет")
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.runs[0].font.name = 'Times New Roman'
                paragraph.runs[0].font.size = Pt(12)
                continue

            headers = ['Слушатель', 'Статус']
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Table Grid'

            for i, text in enumerate(headers):
                paragraph = table.rows[0].cells[i].paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run(text)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)

            for привязка in привязки:
                слушатель = привязка.Слушатель
                row = table.add_row().cells

                values = [
                    f"{слушатель.Фамилия} {слушатель.Имя} {слушатель.Отчество or ''} (ИНН: {слушатель.ИНН})",
                    привязка.Статус.Название
                ]
                for i, text in enumerate(values):
                    cell = row[i]
                    paragraph = cell.paragraphs[0]
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = paragraph.add_run(text)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
        director = doc.add_paragraph("\nДиректор" + (' ' * 50) + "В.Н. Котлов")
        director.alignment = WD_ALIGN_PARAGRAPH.CENTER
        director.runs[0].font.name = 'Times New Roman'
        director.runs[0].font.size = Pt(14)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        response = HttpResponse(buf.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="Группы_и_слушатели.docx"'
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def export_courses_DOCX(request):
    try:
        doc = Document()
        section = doc.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Mm(297)
        section.page_height = Mm(210)
        # Уменьшение отступов слева и справа
        section.left_margin = Mm(10)
        section.right_margin = Mm(10)
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)
        # Название организации (3 строки)
        org_paragraph = doc.add_paragraph()
        org_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = org_paragraph.add_run('Автономная некоммерческая организация дополнительного профессионального образования\n')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run = org_paragraph.add_run('«Сибирская академия профессионального обучения»')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True

        date = doc.add_paragraph("Отчёт от " + today_date())
        date.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date.runs[0].font.name = 'Times New Roman'
        date.runs[0].font.size = Pt(14)

        heading = doc.add_paragraph("Курсы")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading_run = heading.runs[0]
        heading_run.font.name = 'Times New Roman'
        heading_run.font.size = Pt(14)

        headers = ['Курс', 'Количество часов']
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        for i, header in enumerate(headers):
            paragraph = table.rows[0].cells[i].paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            header = paragraph.add_run(header)
            header.font.name = 'Times New Roman'
            header.font.size = Pt(12)
        курсы = (Курсы.objects.filter(id__in= json.loads(request.body).get('ids', []))
                 .values('Название', 'Тип__Название', 'Объём_часов'))
        for курс in курсы:
            row = table.add_row().cells
            row[0].text = курс['Название'] + ' - ' + курс['Тип__Название']
            row[1].text = str(курс['Объём_часов'])
            # Установка шрифта
            for cell in row:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(12)
        director = doc.add_paragraph("\nДиректор" + (' ' * 50) + "В.Н. Котлов")
        director.alignment = WD_ALIGN_PARAGRAPH.CENTER
        director.runs[0].font.name = 'Times New Roman'
        director.runs[0].font.size = Pt(14)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)

        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="Курсы.docx"'
        return response

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def export_organisations_DOCX(request):
    try:
        doc = Document()
        section = doc.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Mm(297)
        section.page_height = Mm(210)
        section.left_margin = Mm(10)
        section.right_margin = Mm(10)
        section.top_margin = Mm(15)
        section.bottom_margin = Mm(15)

        org_paragraph = doc.add_paragraph()
        org_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = org_paragraph.add_run(
            'Автономная некоммерческая организация дополнительного профессионального образования\n')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run = org_paragraph.add_run('«Сибирская академия профессионального обучения»')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True

        date = doc.add_paragraph("Отчёт от " + today_date())
        date.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date.runs[0].font.name = 'Times New Roman'
        date.runs[0].font.size = Pt(14)

        heading = doc.add_paragraph("Организации и их сотрудники")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading.runs[0].font.name = 'Times New Roman'
        heading.runs[0].font.size = Pt(14)

        body_unicode = request.body.decode('utf-8')
        организации = Организации.objects.filter(id__in=json.loads(body_unicode).get('ids', []))

        for организация in организации:
            # Заголовок группы
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f"{организация.Название} (ИНН: {организация.ИНН}, ОГРН: {организация.ОГРН})")
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.bold = True

            привязки = Человек_организация.objects.filter(Организация=организация).select_related('Слушатель')
            if not привязки.exists():
                paragraph = doc.add_paragraph("Сотрудников нет в базе данных")
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.runs[0].font.name = 'Times New Roman'
                paragraph.runs[0].font.size = Pt(12)
                continue

            headers = ['Сотрудник', 'Должность']

            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Table Grid'

            for i, text in enumerate(headers):
                paragraph = table.rows[0].cells[i].paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run(text)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)

            for привязка in привязки:
                слушатель = привязка.Слушатель
                row = table.add_row().cells
                values = [
                    f"{слушатель.Фамилия} {слушатель.Имя} {слушатель.Отчество or ''} (ИНН: {слушатель.ИНН})",
                    привязка.Должность
                ]
                for i, text in enumerate(values):
                    cell = row[i]
                    paragraph = cell.paragraphs[0]
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = paragraph.add_run(text)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
        director = doc.add_paragraph("\nДиректор" + (' ' * 50) + "В.Н. Котлов")
        director.alignment = WD_ALIGN_PARAGRAPH.CENTER
        director.runs[0].font.name = 'Times New Roman'
        director.runs[0].font.size = Pt(14)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        response = HttpResponse(buf.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="Организации.docx"'
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def export_listeners_XLSX(request):
    try:
        # Создание Excel-файла
        wb = Workbook()
        ws = wb.active
        # Заголовки
        ws.append([
            "Фамилия", "Имя", "Отчество", "Дата рождения", "Пол", "Гражданство",
            "Серия паспорта", "Номер паспорта", "ИНН", "СНИЛС", "Телефон", "Email"
        ])
        # Данные
        for слушатель in Слушатели.objects.all():
            ws.append([
                слушатель.Фамилия,
                слушатель.Имя,
                слушатель.Отчество or "",
                слушатель.Дата_рождения.strftime("%d.%m.%Y") if слушатель.Дата_рождения else "",
                слушатель.Пол.Название if слушатель.Пол else "",
                слушатель.Гражданство.Краткое_название if слушатель.Гражданство else "",
                слушатель.Серия_паспорта or "",
                слушатель.Номер_паспорта or "",
                слушатель.ИНН or "",
                слушатель.Номер_СНИЛС or "",
                слушатель.Телефон or "",
                слушатель.Email or ""
            ])
            # Автоширина колонок
            for col in ws.columns:
                max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
                ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2
        # Отправка ответа
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Слушатели.xlsx"'

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.read())
        return response
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при генерации Excel: {str(e)}"}, status=500)  # Уберите, если у вас работает CSRF через заголовки
def export_courses_XLSX(request):
    try:
        # Создание Excel-файла
        wb = Workbook()
        ws = wb.active
        # Заголовки
        ws.append(["Название курса", "Тип", "Количество часов"])
        # Данные
        for курс in Курсы.objects.all():
            ws.append([
                курс.Название,
                курс.Тип.Название,
                курс.Объём_часов
            ])
            # Автоширина колонок
            for col in ws.columns:
                max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
                ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2
        # Отправка ответа
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Курсы.xlsx"'

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.read())
        return response
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при генерации таблицы Excel: {str(e)}"}, status=500)
def export_groups_XLSX(request):
    try:
        # Создание Excel-файла
        wb = Workbook()
        ws = wb.active
        # Заголовки
        ws.append( [ "Слушатель", "Статус", "Группа", "Курс", "Тип курса", "Дата начала курса", "Дата окончания курса"])
        # Данные
        for чел_группа in Человек_группа.objects.all():
            ws.append([
                f"{чел_группа.Слушатель.Фамилия} {чел_группа.Слушатель.Имя} {чел_группа.Слушатель.Отчество or ''} (ИНН: {чел_группа.Слушатель.ИНН})",
                чел_группа.Статус.Название,
                чел_группа.Группа_id,
                чел_группа.Группа.Курс.Название,
                чел_группа.Группа.Курс.Тип.Название,
                чел_группа.Группа.Дата_начала_курса.strftime("%d.%m.%Y"),
                чел_группа.Группа.Дата_окончания_курса.strftime("%d.%m.%Y")
            ])
        # Автоширина колонок (после заполнения)
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            column_letter = get_column_letter(column_cells[0].column)
            ws.column_dimensions[column_letter].width = length + 2
        # Ответ пользователю
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Группы.xlsx"'

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.read())
        return response
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при генерации  таблицы Excel: {str(e)}"}, status=500)

def export_organisations_XLSX(request):
    try:
        # Создание Excel-файла
        wb = Workbook()
        ws = wb.active
        # Заголовки
        ws.append([
            "Сотрудник", "Должность", "Название организации", "ИНН организации",
            "ОГРН организации", "Телефон организации", "Email организации"
        ])
        # Данные
        for чел_орг in Человек_организация.objects.all():
            ws.append([
                f"{чел_орг.Слушатель.Фамилия} {чел_орг.Слушатель.Имя} {чел_орг.Слушатель.Отчество or ''} (ИНН: {чел_орг.Слушатель.ИНН})",
                чел_орг.Должность,
                чел_орг.Организация.Название,
                чел_орг.Организация.ИНН,
                чел_орг.Организация.ОГРН,
                чел_орг.Организация.Телефон or '',
                чел_орг.Организация.Email or '',
            ])

        # Автоширина колонок (после заполнения)
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            column_letter = get_column_letter(column_cells[0].column)
            ws.column_dimensions[column_letter].width = length + 2

        # Ответ пользователю
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Сотрудники организаций.xlsx"'
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.read())
        return response
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при генерации таблицы Excel: {str(e)}"}, status=500)

def import_listeners_XLSX(request):
    listeners_count = Слушатели.objects.all().count()
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                фамилия, имя, отчество, дата_рождения, пол, гражданство, серия, номер_паспорта, инн, снилс, телефон, email = row[:12]
                пол = Пол.objects.filter(Название__iexact=пол).first()
                гражданство = Страны.objects.filter(Краткое_название__iexact=гражданство).first()
                try:
                    # Преобразуем строку даты в объект date
                    if isinstance(дата_рождения, str):
                        дата_рождения = datetime.strptime(дата_рождения, '%d.%m.%Y').date()
                except Exception:
                    messages.error(request, f"Ошибка формата даты рождения: {дата_рождения}")
                    continue
                # Проверка: существует ли такой слушатель по уникальному набору полей (ИНН или паспорт)
                if Слушатели.objects.filter(
                    Фамилия=фамилия,
                    Имя=имя,
                    Отчество=отчество,
                    Дата_рождения=дата_рождения,
                    ИНН=инн
                ).exists():
                    continue
                if фамилия and имя and дата_рождения and пол and гражданство and номер_паспорта and инн:
                    Слушатели.objects.create(
                        Фамилия=фамилия,
                        Имя=имя,
                        Отчество=отчество,
                        Дата_рождения=дата_рождения,
                        Пол=пол,
                        Гражданство=гражданство,
                        Серия_паспорта=серия or '',
                        Номер_паспорта=номер_паспорта,
                        ИНН=инн,
                        Номер_СНИЛС=снилс or '',
                        Телефон=телефон or '',
                        Email=email or ''
                    )
            if listeners_count == Слушатели.objects.all().count():
                messages.warning(request, "Из таблицы Excel не было добавлено новых данных.")
            else:
                messages.success(request, f"Успешно добавлены новые данные.")
        except Exception as e:
            messages.error(request, f"Ошибка при открытии таблицы Excel: {e}")
    return redirect('student_list')
@csrf_exempt


def import_groups_XLSX(request):
    groups_count = Группы.objects.all().count()
    group_links_count = Человек_группа.objects.all().count()
    if request.method == "POST" and request.FILES.get("excel_file"):
        try:
            file = request.FILES["excel_file"]
            wb = openpyxl.load_workbook(file)
            ws = wb.active

            rows = list(ws.iter_rows(min_row=2, values_only=True))  # Пропускаем заголовок
            for row in rows:
                (
                    слушатель,
                    статус,
                    группа_id,
                    курс,
                    тип_курса,
                    дата_начала,
                    дата_окончания,
                ) = row
                try:
                    # Преобразуем строку даты в объект date
                    if isinstance(дата_начала, str) and isinstance(дата_окончания, str):
                        дата_начала = datetime.strptime(дата_начала, '%d.%m.%Y').date()
                        дата_окончания = datetime.strptime(дата_окончания, '%d.%m.%Y').date()
                except Exception:
                    messages.error(request, "Ошибка формата дат")
                    continue

                if "(ИНН:" not in слушатель:
                    continue  # пропускаем строку с неправильным форматом

                фио, инн = слушатель.split("(ИНН:")
                фио_parts = фио.strip().split()
                фамилия = фио_parts[0]
                имя = фио_parts[1] if len(фио_parts) > 1 else ""
                отчество = фио_parts[2] if len(фио_parts) > 2 else ""

                инн = инн.strip(") ").strip()
                курс = Курсы.objects.filter(Название=курс).first()
                статус = Статусы.objects.filter(Название=статус).first()
                try:
                    слушатель, _ = Слушатели.objects.get_or_create(
                        ИНН=инн,
                        defaults={
                            "Фамилия": фамилия,
                            "Имя": имя,
                            "Отчество": отчество,
                        },
                    )
                except Exception:
                    continue
                # --- Получение или создание группы ---
                группа, _ = Группы.objects.get_or_create(
                    id=группа_id,
                    defaults={
                        "Курс": курс,
                        "Дата_начала_курса": дата_начала,
                        "Дата_окончания_курса": дата_окончания,
                    },
                )
                # --- Добавляем привязку ---
                Человек_группа.objects.get_or_create(
                    Слушатель=слушатель,
                    Группа=группа,
                    Статус=статус
                )
            if groups_count == Группы.objects.all().count() and group_links_count == Человек_группа.objects.all().count():
                messages.warning(request, "Из таблицы Excel не было добавлено новых данных.")
            else:
                messages.success(request, "Успешно добавлены новые данные.")
            return redirect("group_list")  # редирект обратно на страницу
        except Exception as e:
            return JsonResponse(
                {"error": f"Ошибка при импорте из Excel: {str(e)}"}, status=400
            )
    return JsonResponse({"error": "Файл не был загружен."}, status=400)

def import_courses_XLSX(request):
    courses_count = Курсы.objects.all().count()
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        imported_count = 0
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                название, тип, число_часов = row[:3]
                тип = Типы_курсов.objects.filter(Название__iexact=тип).first()
                # Проверка: существует ли такой слушатель по уникальному набору полей (ИНН или паспорт)
                if Курсы.objects.filter( Название=название, Тип=тип, ).exists(): continue
                if название and тип and число_часов:
                    Курсы.objects.create(
                        Название=название,
                        Тип=тип,
                        Объём_часов=число_часов
                    )
            if courses_count == Курсы.objects.all().count():
                messages.warning(request, "Из таблицы Excel не было добавлено новых данных.")
            else:
                messages.success(request, f"Успешно добавлены новые данные.")
        except Exception as e:
            messages.error(request, f"Ошибка при открытии таблицы Excel: {e}")
    return redirect('course_list')

def import_organisations_XLSX(request):
    organisations_count = Группы.objects.all().count()
    organisation_links_count = Человек_группа.objects.all().count()
    if request.method == "POST" and request.FILES.get("excel_file"):
        try:
            file = request.FILES["excel_file"]
            wb = openpyxl.load_workbook(file)
            imported_count = 0
            ws = wb.active

            rows = list(ws.iter_rows(min_row=2, values_only=True))  # Пропускаем заголовок
            for row in rows:
                (
                    сотрудник_str,
                    должность,
                    название_организации,
                    инн_организации,
                    огрн,
                    телефон,
                    email,
                ) = row

                # --- Парсинг сотрудника ---
                # Формат: "Иванов Иван Иванович (ИНН: 1234567890)"
                if "(ИНН:" not in сотрудник_str:
                    continue  # пропускаем строку с неправильным форматом

                фио, инн = сотрудник_str.split("(ИНН:")
                фио_parts = фио.strip().split()
                фамилия = фио_parts[0]
                имя = фио_parts[1] if len(фио_parts) > 1 else ""
                отчество = фио_parts[2] if len(фио_parts) > 2 else ""

                инн = инн.strip(") ").strip()

                try:
                    слушатель, _ = Слушатели.objects.get_or_create(
                        ИНН=инн,
                        defaults={
                            "Фамилия": фамилия,
                            "Имя": имя,
                            "Отчество": отчество,
                        },
                    )
                except Exception:
                    continue
                # --- Получение или создание организации ---
                организация, _ = Организации.objects.get_or_create(
                    ИНН=инн_организации,
                    defaults={
                        "Название": название_организации,
                        "ОГРН": огрн,
                        "Телефон": телефон,
                        "Email": email,
                    },
                )
                # --- Добавляем привязку ---
                Человек_организация.objects.get_or_create(
                    Слушатель=слушатель,
                    Организация=организация,
                    defaults={"Должность": должность}
                )
            if organisations_count == Организации.objects.all().count() and organisation_links_count == Человек_организация.objects.all().count():
                messages.warning(request, "Из таблицы Excel не было добавлено новых данных.")
            else:
                messages.success(request, f"Успешно добавлены новые данные.")
            return redirect("organisation_list")  # редирект обратно на страницу
        except Exception as e:
            return JsonResponse(
                {"error": f"Ошибка при импорте из Excel: {str(e)}"}, status=400
            )
    return JsonResponse({"error": "Файл не был загружен."}, status=400)

