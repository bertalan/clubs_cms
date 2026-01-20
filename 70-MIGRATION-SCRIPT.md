# Migration Script

## Export (old project)

```python
import json, os
from wagtail.models import Page
from wagtail.images.models import Image

OUTPUT = 'migration_data'
os.makedirs(OUTPUT, exist_ok=True)

def export_pages():
    data = []
    for p in Page.objects.all().specific():
        item = {'id': p.id, 'title': p.title, 'slug': p.slug, 'type': p.__class__.__name__, 'live': p.live}
        if hasattr(p, 'body') and p.body:
            item['body_raw'] = p.body.raw_data
        for f in ['intro', 'search_description']:
            if hasattr(p, f): item[f] = getattr(p, f, '')
        data.append(item)
    with open(f'{OUTPUT}/pages.json', 'w') as f:
        json.dump(data, f, indent=2)

def export_images():
    data = [{'id': i.id, 'title': i.title, 'file': i.file.name} for i in Image.objects.all()]
    with open(f'{OUTPUT}/images.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    export_pages()
    export_images()
```

## Import (new project)

```python
import json
from wagtail.models import Page
from apps.website.models import HomePage, NewsPage, AboutPage

MODEL_MAP = {'HomePage': HomePage, 'ArticlePage': NewsPage, 'WebPage': AboutPage}

def import_pages():
    with open('migration_data/pages.json') as f:
        pages = json.load(f)
    root = Page.objects.get(depth=1)
    for p in pages:
        if p['type'] not in MODEL_MAP: continue
        model = MODEL_MAP[p['type']]
        if model.objects.filter(slug=p['slug']).exists(): continue
        new_page = model(title=p['title'], slug=p['slug'], live=p['live'])
        root.add_child(instance=new_page)

if __name__ == '__main__':
    import_pages()
```

## Commands

```bash
# Export
cd /old && python manage.py shell < export_content.py
cp -r migration_data media /new/

# Import  
cd /new && python manage.py shell < import_content.py
```

## Mapping

| CodeRedCMS | Wagtail |
|------------|---------|
| ArticlePage | NewsPage |
| WebPage | AboutPage |
| FormPage | ContactPage |
