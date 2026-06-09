from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0007_remove_auto_cars_publication"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_article_search_tsv
            ON blog_article
            USING gin (
                (
                    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                    setweight(to_tsvector('english', coalesce(subtitle, '')), 'B') ||
                    setweight(to_tsvector('english', coalesce(content, '')), 'C')
                )
            )
            WHERE status = 'published';
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_article_search_tsv;",
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_article_search_trgm
            ON blog_article
            USING gin (
                (coalesce(title, '') || ' ' || coalesce(subtitle, '') || ' ' || coalesce(content, '')) gin_trgm_ops
            )
            WHERE status = 'published';
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_article_search_trgm;",
        ),
    ]
