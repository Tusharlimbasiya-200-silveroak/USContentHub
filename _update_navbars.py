"""Add 📈 Trading link to platform nav bar in all existing static site HTML files."""
import os, re

SITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites')
TRADING_LINK = '<a href="https://Tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint/">📈 Trading</a>'

# Pattern: find the News link and add Trading after it
NEWS_PATTERN = r'(<a href="https://Tusharlimbasiya-200-silveroak\.github\.io/usa-news-digest/">📰 News</a>)'

updated = 0
skipped = 0

for site_folder in os.listdir(SITES_DIR):
    site_path = os.path.join(SITES_DIR, site_folder)
    if not os.path.isdir(site_path):
        continue
    # Skip the trading blueprint itself (already has the link)
    if site_folder == 'the-trading-blueprint':
        continue
    
    for filename in os.listdir(site_path):
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(site_path, filename)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Check if already has the trading link
        if 'the-trading-blueprint' in content:
            skipped += 1
            continue
        
        # Check if has the News link to add after
        if 'usa-news-digest' in content and '📰' in content:
            new_content = re.sub(
                NEWS_PATTERN,
                r'\1\n                ' + TRADING_LINK,
                content
            )
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated += 1

print(f'Updated {updated} HTML files across static sites')
print(f'Skipped {skipped} files (already had Trading link)')
