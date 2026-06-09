from django.db import migrations


def remove_auto_cars(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    Publication = apps.get_model("blog", "Publication")

    Article.objects.filter(publication__slug="auto-cars").delete()
    Publication.objects.filter(slug="auto-cars").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0006_remove_publication_github_url"),
    ]

    operations = [
        migrations.RunPython(remove_auto_cars, migrations.RunPython.noop),
    ]
