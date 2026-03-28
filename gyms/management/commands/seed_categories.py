"""
python3 manage.py seed_categories
python3 manage.py seed_categories --reset   # faqat DEBUG yoki ALLOW_CATEGORY_SEED_RESET=1
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from gyms.models import GymCategory


# icon field → Lucide icon nomi (frontend da shu nom bo'yicha komponent topiladi)
CATEGORIES = [
    # (name_uz,           slug,              lucide_icon,        order)
    ("Fitnes & Gym",      "fitnes",          "Dumbbell",         1),
    ("Futbol",            "futbol",          "CircleDot",        2),
    ("Mini Futbol",       "mini-futbol",     "Target",           3),
    ("Basketbol",         "basketbol",       "Trophy",           4),
    ("Voleybol",          "voleybol",        "Volleyball",       5),
    ("Boks",              "boks",            "Shield",           6),
    ("Kurash",            "kurash",          "Swords",           7),
    ("Judo",              "judo",            "Zap",              8),
    ("Karate",            "karate",          "Zap",              9),
    ("Taekwondo",         "taekwondo",       "Flame",           10),
    ("Sambo",             "sambo",           "Users",           11),
    ("Tennis",            "tennis",          "Activity",        12),
    ("Stol Tennisi",      "stol-tennisi",    "Layers",          13),
    ("Suzish (Basseyn)",  "suzish",          "Waves",           14),
    ("Gimnastika",        "gimnastika",      "PersonStanding",  15),
    ("Yoga",              "yoga",            "Heart",           16),
    ("CrossFit",          "crossfit",        "Timer",           17),
    ("Kikboksing",        "kikboksing",      "Footprints",      18),
    ("Shaxmat",           "shaxmat",         "Grid3x3",         19),
    ("Velosiped",         "velosiped",       "Bike",            20),
]


class Command(BaseCommand):
    help = "Mashhur sport kategoriyalarini bazaga yuklaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Avval mavjud kategoriyalarni o\'chirib qayta yuklaydi',
        )

    def handle(self, *args, **options):
        if options['reset']:
            if not settings.DEBUG and os.environ.get('ALLOW_CATEGORY_SEED_RESET') != '1':
                raise CommandError(
                    "Ishlab chiqarishda --reset xavfli (barcha kategoriyalar o'chadi). "
                    "Agar aniq bilib qilmoqchi bo'lsangiz: ALLOW_CATEGORY_SEED_RESET=1 "
                    "python manage.py seed_categories --reset"
                )
            deleted, _ = GymCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"{deleted} ta kategoriya o'chirildi."))

        created_count = updated_count = 0

        for name, slug, icon, order in CATEGORIES:
            obj, created = GymCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'order': order},
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ [{icon:18s}]  {name}")
            else:
                updated_count += 1
                self.stdout.write(f"  🔄 [{icon:18s}]  {name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nJami: {created_count} yangi + {updated_count} yangilangan kategoriya."
            )
        )
