import osmium
import os
import django
from tqdm import tqdm
from django.db import transaction

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebApp.settings')
django.setup()

from main.models import (
    Страны, Регионы, Районы, Населенные_пункты,
    Почтовые_индексы, Названия_улиц, Улицы
)


CITY_TO_REGION = {
    "Абакан": "Республика Хакасия",
    "Анадырь": "Чукотский автономный округ",
    "Архангельск": "Архангельская область",
    "Астрахань": "Астраханская область",
    "Байконур": "Байконур",
    "Барнаул": "Алтайский край",
    "Белгород": "Белгородская область",
    "Биробиджан": "Еврейская автономная область",
    "Благовещенск": "Амурская область",
    "Брянск": "Брянская область",
    "Великий Новгород": "Новгородская область",
    "Владивосток": "Приморский край",
    "Владикавказ": "Республика Северная Осетия — Алания",
    "Владимир": "Владимирская область",
    "Волгоград": "Волгоградская область",
    "Вологда": "Вологодская область",
    "Воронеж": "Воронежская область",
    "Гатчина": "Ленинградская область",
    "Горно-Алтайск": "Республика Алтай",
    "Грозный": "Чеченская Республика",
    "Донецк": "Донецкая Народная Республика",
    "Екатеринбург": "Свердловская область",
    "Запорожье": "Запорожская область",
    "Иваново": "Ивановская область",
    "Ижевск": "Удмуртская Республика",
    "Иркутск": "Иркутская область",
    "Йошкар-Ола": "Республика Марий Эл",
    "Казань": "Республика Татарстан",
    "Калининград": "Калининградская область",
    "Калуга": "Калужская область",
    "Кемерово": "Кемеровская область — Кузбасс",
    "Киров": "Кировская область",
    "Кострома": "Костромская область",
    "Красногорск": "Московская область",
    "Краснодар": "Краснодарский край",
    "Красноярск": "Красноярский край",
    "Курган": "Курганская область",
    "Курск": "Курская область",
    "Кызыл": "Республика Тыва",
    "Липецк": "Липецкая область",
    "Луганск": "Луганская Народная Республика",
    "Магадан": "Магаданская область",
    "Магас": "Республика Ингушетия",
    "Майкоп": "Республика Адыгея",
    "Махачкала": "Республика Дагестан",
    "Москва": "Москва",
    "Мурманск": "Мурманская область",
    "Нальчик": "Кабардино-Балкарская Республика",
    "Нарьян-Мар": "Ненецкий автономный округ",
    "Нижний Новгород": "Нижегородская область",
    "Новосибирск": "Новосибирская область",
    "Омск": "Омская область",
    "Орел": "Орловская область",
    "Оренбург": "Оренбургская область",
    "Пенза": "Пензенская область",
    "Пермь": "Пермский край",
    "Петрозаводск": "Республика Карелия",
    "Петропавловск-Камчатский": "Камчатский край",
    "Псков": "Псковская область",
    "Ростов-на-Дону": "Ростовская область",
    "Рязань": "Рязанская область",
    "Салехард": "Ямало-Ненецкий автономный округ",
    "Санкт-Петербург": "Санкт-Петербург",
    "Саранск": "Республика Мордовия",
    "Саратов": "Саратовская область",
    "Севастополь": "Севастополь",
    "Симферополь": "Республика Крым",
    "Смоленск": "Смоленская область",
    "Ставрополь": "Ставропольский край",
    "Сыктывкар": "Республика Коми",
    "Тамбов": "Тамбовская область",
    "Тверь": "Тверская область",
    "Томск": "Томская область",
    "Тула": "Тульская область",
    "Тюмень": "Тюменская область",
    "Улан-Удэ": "Республика Бурятия",
    "Ульяновск": "Ульяновская область",
    "Уфа": "Республика Башкортостан",
    "Хабаровск": "Хабаровский край",
    "Ханты-Мансийск": "Ханты-Мансийский автономный округ — Югра",
    "Херсон": "Херсонская область",
    "Чебоксары": "Чувашская Республика",
    "Челябинск": "Челябинская область",
    "Черкесск": "Карачаево-Черкесская Республика",
    "Чита": "Забайкальский край",
    "Элиста": "Республика Калмыкия",
    "Южно-Сахалинск": "Сахалинская область",
    "Якутск": "Республика Саха (Якутия)",
    "Ярославль": "Ярославская область",
}
MOSCOW_DISTRICTS = {
    "Центральный административный округ",
    "Северный административный округ",
    "Южный административный округ",
    "Восточный административный округ",
    "Западный административный округ",
    "Северо-Восточный административный округ",
    "Северо-Западный административный округ",
    "Юго-Восточный административный округ",
    "Юго-Западный административный округ",
    "Зеленоградский административный округ",
    "Новомосковский административный округ",
    "Троицкий административный округ",
}

# Кеши
cache_countries = {}
cache_regions = {}
cache_districts = {}
cache_places = {}
cache_postcodes = {}
cache_street_names = {}
cache_streets = {}

class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm(unit="obj")

    def get_or_create_country(self, name, short_name=None, phone_code=None):
        if name in cache_countries:
            return cache_countries[name]
        obj, _ = Страны.objects.get_or_create(
            Название=name,
            defaults={"Краткое_название": short_name or name[:50], "Телефонный_код": phone_code or ""}
        )
        cache_countries[name] = obj
        return obj

    def get_or_create_region(self, name, country):
        key = (name, country.id)
        if key in cache_regions:
            return cache_regions[key]
        obj, _ = Регионы.objects.get_or_create(Название=name, Страна=country)
        cache_regions[key] = obj
        return obj

    def get_or_create_district(self, name, region):
        if not name or not region:
            return None
        key = (name, region.id)
        if key in cache_districts:
            return cache_districts[key]
        obj, _ = Районы.objects.get_or_create(Название=name, Регион=region)
        cache_districts[key] = obj
        return obj

    def get_or_create_place(self, name, district, region):
        key = (name, region.id)
        if key in cache_places:
            return cache_places[key]
        obj, _ = Населенные_пункты.objects.get_or_create(
            Название=name,
            Регион=region,
            defaults={"Район": district}
        )
        # обновим район, если появился
        if not obj.Район and district:
            obj.Район = district
            obj.save(update_fields=["Район"])
        cache_places[key] = obj
        return obj

    def get_or_create_postcode(self, postcode, place_obj):
        if not postcode or not place_obj:
            return None
        key = (postcode, place_obj.id)
        if key in cache_postcodes:
            return cache_postcodes[key]
        obj, _ = Почтовые_индексы.objects.get_or_create(
            Индекс=postcode,
            Населенный_пункт=place_obj
        )
        cache_postcodes[key] = obj
        return obj

    def get_or_create_street_name(self, name):
        if not name:
            return None
        if name in cache_street_names:
            return cache_street_names[name]
        obj, _ = Названия_улиц.objects.get_or_create(Название=name)
        cache_street_names[name] = obj
        return obj

    def get_or_create_street(self, street_name_obj, place_obj):
        if not street_name_obj or not place_obj:
            return None
        key = (street_name_obj.id, place_obj.id)
        if key in cache_streets:
            return cache_streets[key]
        obj, _ = Улицы.objects.get_or_create(
            Название=street_name_obj,
            Населенный_пункт=place_obj
        )
        cache_streets[key] = obj
        return obj

    def process_address_tags(self, tags):
        city = tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village")
        region_name = tags.get("addr:region") or CITY_TO_REGION.get(city)

        if region_name not in CITY_TO_REGION.values():
            return

        # Москва: если city — это округ
        if region_name == "Москва" and city in MOSCOW_DISTRICTS:
            district_name = city
            city = "Москва"
        else:
            district_name = tags.get("addr:district")

        country = self.get_or_create_country("Российская Федерация", "Россия", "7")
        region = self.get_or_create_region(name=region_name, country=country)
        district = self.get_or_create_district(name=district_name, region=region) if district_name else None

        if city:
            place_obj = self.get_or_create_place(name=city, district=district, region=region)
        else:
            place_obj = None

        postcode = tags.get("addr:postcode")
        postcode_obj = self.get_or_create_postcode(postcode, place_obj)

        street_name = tags.get("addr:street") or tags.get("name")
        if street_name and place_obj:
            street_name_obj = self.get_or_create_street_name(street_name)
            self.get_or_create_street(street_name_obj, place_obj)

    def node(self, n):
        self.pbar.update(1)
        tags = n.tags
        if any(key in tags for key in ["addr:street", "addr:postcode", "addr:city", "addr:region", "name", "highway"]):
            with transaction.atomic():
                self.process_address_tags(tags)

    def way(self, w):
        self.pbar.update(1)
        tags = w.tags
        if any(key in tags for key in ["addr:street", "addr:postcode", "addr:city", "addr:region", "name", "highway"]):
            with transaction.atomic():
                self.process_address_tags(tags)

    def close(self):
        self.pbar.close()

def run_import(osm_pbf_path):
    handler = OSMHandler()
    handler.apply_file(osm_pbf_path, locations=False)
    handler.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python address.py path_to_file.osm.pbf")
        sys.exit(1)
    run_import(sys.argv[1])
