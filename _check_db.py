import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'writeflow.settings'
django.setup()
from blog.models import Publication, Article

print('=== PUBLICATIONS ===')
for p in Publication.objects.all():
    print(f'  {p.id}: {p.name} ({p.slug}) - icon:{p.icon} color:{p.color}')

print()
a = Article.objects.filter(status='published').first()
print(f'=== SAMPLE ARTICLE ===')
print(f'Title: {a.title}')
print(f'Slug: {a.slug}')
print(f'Subtitle: {a.subtitle}')
print(f'Read time: {a.read_time}')
print(f'Word count: {a.word_count}')
print(f'Meta: {a.meta_description}')
print(f'Cover: {a.cover_image}')
print(f'Pub: {a.publication}')
tags = list(a.tags.values_list("name", flat=True))
print(f'Tags: {tags}')
print(f'Content (first 1500 chars):')
print(a.content[:1500])
