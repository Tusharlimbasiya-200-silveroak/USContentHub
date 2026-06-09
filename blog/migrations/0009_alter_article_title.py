from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0008_add_article_search_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="title",
            field=models.CharField(max_length=500),
        ),
    ]
