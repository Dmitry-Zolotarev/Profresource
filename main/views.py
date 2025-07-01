from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Q
import json, re
from io import BytesIO

from docx import Document
from docx.shared import Mm, Pt, Inches
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .models import (
    Слушатели, Страны, Пол, Группы, Курсы, Типы_курсов,
    Материалы_курсов, Типы_материалов,
    Организации, Человек_группа, Человек_организация,
    Статусы, Адреса
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
        if Слушатели.objects.filter(Номер_СНИЛС=request.POST.get('Номер_СНИЛС')).exists():
            messages.warning(request, "Человек с этим СНИЛС уже есть в базе данных!")
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
            if Организации.objects.filter(
                    Название=request.POST.get('Название'),
                    ИНН=request.POST.get('ИНН'),
                    ОГРН=request.POST.get('ОГРН'),
                ).exists():
                messages.warning(request, "Эта организация уже есть в базе данных!")
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
@require_http_methods(["POST"])
def delete_listener(request, id):
    listener = get_object_or_404(Слушатели, id=id)
    if Человек_группа.objects.filter(Слушатель=listener).exists() \
       or Человек_организация.objects.filter(Слушатель=listener).exists() \
       or Адреса.objects.filter(id_студента=listener).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи.")
    else:
        listener.delete()
    return redirect('student_list')


@require_http_methods(["POST"])
def delete_group(request, id):
    group = get_object_or_404(Группы, id=id)
    if Человек_группа.objects.filter(Группа=group).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        group.delete()
    return redirect('group_list')


@require_http_methods(["POST"])
def delete_group_linking(request, id):
    get_object_or_404(Человек_группа, id=id).delete()
    return redirect('group_list')


@require_http_methods(["POST"])
def delete_course(request, id):
    course = get_object_or_404(Курсы, id=id)
    if Группы.objects.filter(Курс=course).exists() \
       or Материалы_курсов.objects.filter(Курс=course).exists():
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
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
        messages.error(request, "Удаление отменено — есть зависимые записи!")
    else:
        org.delete()
    return redirect('organisation_list')

@require_http_methods(["POST"])
def delete_org_linking(request, id):
    get_object_or_404(Человек_организация, id=id).delete()
    return redirect('organisation_list')
@csrf_exempt
def export_listeners(request):
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

        heading = doc.add_paragraph("\nДиректор" + (' ' * 50) +"В.Н. Котлов")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading.runs[0].font.name = 'Times New Roman'
        heading.runs[0].font.size = Pt(14)

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
@csrf_exempt
def export_groups(request):
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
                doc.add_paragraph()
        footer = doc.add_paragraph("Директор" + (' ' * 50) + "В.Н. Котлов")
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.runs[0].font.name = 'Times New Roman'
        footer.runs[0].font.size = Pt(14)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        response = HttpResponse(buf.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="Группы_и_слушатели.docx"'
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def export_courses(request):
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

        heading = doc.add_paragraph("\nДиректор" + (' ' * 50) + "В.Н. Котлов")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading.runs[0].font.name = 'Times New Roman'
        heading.runs[0].font.size = Pt(14)

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

@csrf_exempt
def export_organisations(request):
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
            doc.add_paragraph()
        footer = doc.add_paragraph("Директор" + (' ' * 50) + "В.Н. Котлов")
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.runs[0].font.name = 'Times New Roman'
        footer.runs[0].font.size = Pt(14)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        response = HttpResponse(buf.read(),
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="Организации.docx"'
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)