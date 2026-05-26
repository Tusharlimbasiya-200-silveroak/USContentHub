"""Add Trading link to platform nav bar in all existing static site HTML files."""
import os, glob

SITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites')
TRADING_LINK = '<a href="https://Tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint/">\U0001f4c8 Trading</a>'

# The exact News link text to find (use string replace, not regex)
NEWS_LINK = '<a href="https://Tusharlimbasiya-200-silveroak.github.io/usa-news-digest/">\U0001f4f0 News</a>'

updated = 0
skipped = 0
no_match = 0

for site_folder in os.listdir(SITES_DIR):
    site_path = os.path.join(SITES_DIR, site_folder)
    if not os.path.isdir(site_path):
        continue
    if site_folder == 'the-trading-blueprint':
        continue
    
    for filename in os.listdir(site_path):
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(site_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        if 'the-trading-blueprint' in content:
            skipped += 1
            continue
        
        if NEWS_LINK in content:
            new_content = content.replace(
                NEWS_LINK,
                NEWS_LINK + '\n                ' + TRADING_LINK
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated += 1
            print(f'  + {site_folder}/{filename}')
        else:
            no_match += 1

print(f'\nDone: {updated} updated, {skipped} skipped (already had link), {no_match} no match')
