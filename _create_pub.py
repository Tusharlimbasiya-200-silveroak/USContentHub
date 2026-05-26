import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'writeflow.settings'
django.setup()
from blog.models import Publication, Tag

pub, created = Publication.objects.get_or_create(
    slug='the-trading-blueprint',
    defaults={
        'name': 'The Trading Blueprint',
        'description': 'Stock market strategies, technical analysis, and trading psychology for American traders',
        'color': '#059669',
        'icon': '📈',
        'github_url': 'https://tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint/',
    }
)
action = 'Created' if created else 'Already exists'
print(f'{action}: {pub.name} (slug={pub.slug}, icon={pub.icon}, color={pub.color})')

# Create default tags
for tag_name in ['trading', 'stocks', 'forex', 'technical-analysis', 'investing', 'options', 'crypto', 'day-trading']:
    t, tc = Tag.objects.get_or_create(name=tag_name)
    print(f'  Tag: {t.name} ({"new" if tc else "exists"})')
