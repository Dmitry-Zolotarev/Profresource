from django.db import models

class Страны(models.Model):
    Название = models.CharField(max_length=100, unique=True)
    Краткое_название = models.CharField(max_length=50, unique=True)
    Телефонный_код = models.CharField(max_length=10)

class Регионы(models.Model):
    Код = models.CharField(max_length=10)
    Название = models.CharField(max_length=100)
    Страна = models.ForeignKey(Страны, on_delete=models.CASCADE)

class Районы(models.Model):
    Название = models.CharField(max_length=100)
    Регион = models.ForeignKey(Регионы, on_delete=models.CASCADE)

class Типы_населенных_пунктов(models.Model):
    Название = models.CharField(max_length=100, unique=True)

class Населенные_пункты(models.Model):
    тип = models.ForeignKey(Типы_населенных_пунктов, on_delete=models.CASCADE)
    Название = models.CharField(max_length=100)
    Район = models.ForeignKey(Районы, on_delete=models.CASCADE)

class Почтовые_индексы(models.Model):
    Индекс = models.CharField(max_length=10, unique=False)

class Типы_улиц(models.Model):
    Название = models.CharField(max_length=100)

class Названия_улиц(models.Model):
    Тип_улицы = models.ForeignKey(Типы_улиц, on_delete=models.SET_NULL, null=True)
    Название = models.CharField(max_length=100)

class Улицы(models.Model):
    Название = models.ForeignKey(Названия_улиц, on_delete=models.CASCADE)
    Населенный_пункт = models.ForeignKey(Населенные_пункты, on_delete=models.SET_NULL, null=True, blank=True)
    Почтовый_индекс = models.ForeignKey(Почтовые_индексы, on_delete=models.SET_NULL, null=True, blank=True)

class Адреса(models.Model):
    улица = models.ForeignKey(Улицы, on_delete=models.CASCADE)
    Номер_дома = models.CharField(max_length=20)

class Пол(models.Model):
    Название = models.CharField(max_length=20, unique=True)

class Типы_курсов(models.Model):
    Название = models.CharField(max_length=10, unique=True)

class Типы_материалов(models.Model):
    Название = models.CharField(max_length=100, unique=True)

class Организации(models.Model):
    Название = models.CharField(max_length=255, null=False, default="")
    ИНН = models.CharField(max_length=12, blank=True, unique=True)
    ОГРН = models.CharField(max_length=13, blank=True, unique=True)
    Телефон = models.CharField(max_length=10, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Адрес = models.ForeignKey(Адреса, on_delete=models.SET_NULL, null=True)

class Курсы(models.Model):
    Тип = models.ForeignKey(Типы_курсов, on_delete=models.CASCADE)
    Название = models.CharField(max_length=255)
    Объём_часов = models.IntegerField(blank=True, null=False, default=0)

class Группы(models.Model):
    Курс = models.ForeignKey(Курсы, on_delete=models.CASCADE)

class Слушатели(models.Model):
    Фамилия = models.CharField(max_length=100, null=False)
    Имя = models.CharField(max_length=100, null=False)
    Отчество = models.CharField(max_length=100, blank=True, null=True)
    Дата_рождения = models.DateField(null=True)
    Пол = models.ForeignKey(Пол, on_delete=models.SET_NULL, null=True)
    Серия_паспорта = models.CharField(max_length=10, blank=True, null=True)
    Номер_паспорта = models.CharField(max_length=20, blank=True, null=True)
    Гражданство = models.ForeignKey(Страны, on_delete=models.SET_NULL, null=True)
    Номер_СНИЛС = models.CharField(max_length=11, blank=True, null=True)
    ИНН = models.CharField(max_length=12, blank=True, null=True)
    Телефон = models.CharField(max_length=10, blank=True, null=True)
    Email = models.EmailField(blank=True, null=True)
    Адрес = models.ForeignKey(Адреса, on_delete=models.SET_NULL, null=True)

class Статусы(models.Model):
    Название = models.CharField(max_length=50, null=False, default="", unique=True)

class Приказы(models.Model):
    Hash = models.IntegerField(null=True)

class Протоколы(models.Model):
    Hash = models.IntegerField(null=True)

class Человек_группа(models.Model):
    Слушатель = models.ForeignKey(Слушатели, on_delete=models.CASCADE)
    Группа = models.ForeignKey(Группы, on_delete=models.CASCADE)
    Статус = models.ForeignKey(Статусы, on_delete=models.CASCADE, null=False, default="")

class Человек_организация(models.Model):
    Слушатель = models.ForeignKey(Слушатели, on_delete=models.CASCADE)
    Организация = models.ForeignKey(Организации, on_delete=models.CASCADE)
    Должность = models.CharField(max_length=255, blank=True, null=False, default="")

class Материалы_курсов(models.Model):
    Курс = models.ForeignKey(Курсы, on_delete=models.CASCADE)
    Тип = models.ForeignKey(Типы_материалов, on_delete=models.CASCADE)
    Название = models.CharField(max_length=255, null=False, default="")
    Ссылка_на_материал = models.CharField(max_length=255, null=False, default="about:blank")

class Месяцы(models.Model):
    Название = models.CharField(max_length=8)

