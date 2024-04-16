import os
from pathlib import Path
from random import randint

from django.core.files.images import ImageFile
from django.db import migrations


def fill_db(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    # categories
    Category = apps.get_model("shop", "Category")

    c1 = Category.objects.using(db_alias).create(name="Лазерные принтеры")
    c2 = Category.objects.using(db_alias).create(name="Струйные принтеры")
    c3 = Category.objects.using(db_alias).create(name="Термопринтеры")

    categories = [c1, c2, c3]

    Product = apps.get_model("shop", "Product")

    countries = ["Россия", "Китай", "Германия"]
    models = ["A12", "B55", "C74"]
    for i in range(1, 15 + 1):
        img_path = os.path.join(Path(__file__).parent.parent.parent, 'static', 'images', f'printer{i}.jpg')

        with open(img_path, "rb") as img:
            img_field = ImageFile(img)
            product = Product(
                name=f"Принтер {i}",
                category=categories[randint(0, 2)],
                price=randint(5000, 10000),
                quantity=randint(1, 100),
                manufacture_year=str(randint(2010, 2024)),
                country=countries[randint(0, 2)],
                model=models[randint(0, 2)],
            )
            product.image.save(name=f'printer{i}.jpg', content=img_field, save=True)
            product.save()


def fill_db_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_db, fill_db_reverse),
    ]
