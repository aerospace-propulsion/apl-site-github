#!/usr/bin/env python3
"""Rough local render of the Jekyll site using python-liquid, to catch template/YAML errors and
broken image references before pushing to GitHub. Not a substitute for a real Jekyll build."""
import os, re, sys, yaml, glob, datetime, markdown_it
from liquid import Environment, FileSystemLoader
from liquid.filter import string_filter, with_environment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site_check')
cfg = yaml.safe_load(open(os.path.join(ROOT, '_config.yml'), encoding='utf-8'))
baseurl = cfg.get('baseurl', '') or ''

def jekyllize(src):
    # translate Jekyll-only syntax into python-liquid syntax
    src = re.sub(r'{%\s*seo[^%]*%}', '', src)
    def inc(m):
        name, args = m.group(1), m.group(2)
        kv = re.findall(r'(\w+)=("[^"]*"|\S+)', args)
        tail = ''.join(f', {k}: {v}' for k, v in kv)
        return '{% include "' + name + '"' + tail + ' %}'
    src = re.sub(r'{%\s*include\s+([\w./-]+)([^%]*)%}', inc, src)
    src = re.sub(r'\binclude\.(\w+)', r'\1', src)
    return src

class JLoader(FileSystemLoader):
    def get_source(self, env, template_name, **kw):
        ts = super().get_source(env, template_name, **kw)
        return ts._replace(text=jekyllize(ts.text))

env = Environment(loader=JLoader(os.path.join(ROOT, '_includes'), ext=''))

@string_filter
def relative_url(s): return baseurl + s
@string_filter
def absolute_url(s): return cfg['url'] + baseurl + s
@string_filter
def markdownify(s):
    import markdown as md
    return md.markdown(s)
def date_filter(v, fmt):
    if isinstance(v, str): v = datetime.datetime.fromisoformat(v)
    if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime): v = datetime.datetime(v.year, v.month, v.day)
    return v.strftime(fmt)
env.add_filter('relative_url', relative_url)
env.add_filter('absolute_url', absolute_url)
env.add_filter('markdownify', markdownify)
env.add_filter('date', date_filter)
env.add_filter('uniq', lambda a: list(dict.fromkeys(a)))

def fm_split(text):
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', text, re.S)
    if not m: return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)

def kramdown(text):
    import markdown as md
    return md.markdown(text, extensions=['md_in_html', 'attr_list', 'tables'])

data = {}
for f in glob.glob(os.path.join(ROOT, '_data', '*.yml')):
    data[os.path.basename(f)[:-4]] = yaml.safe_load(open(f, encoding='utf-8'))

# posts
posts = []
for f in sorted(glob.glob(os.path.join(ROOT, '_posts', '*.md'))):
    fm, body = fm_split(open(f, encoding='utf-8').read())
    d = fm['date'] if isinstance(fm['date'], datetime.date) else datetime.date.fromisoformat(str(fm['date']))
    slug = os.path.basename(f)[11:-3]
    url = f"/board/{d.year}/{d.month:02d}/{d.day:02d}/{slug}/"
    posts.append(dict(fm, date=datetime.datetime(d.year, d.month, d.day), url=url, body=body, path=f))
posts.sort(key=lambda p: (p['date'], p['path']), reverse=True)
for i, p in enumerate(posts):
    p['next'] = posts[i-1] if i > 0 else None
    p['previous'] = posts[i+1] if i+1 < len(posts) else None

site = dict(cfg, data=data, posts=posts, time=datetime.datetime.now())

def render_layout(layout, content, page):
    fm, body = fm_split(open(os.path.join(ROOT, '_layouts', layout + '.html'), encoding='utf-8').read())
    body = jekyllize(body)
    html = env.from_string(body).render(site=site, page=page, content=content)
    if fm.get('layout'): return render_layout(fm['layout'], html, page)
    return html

def render_page(path, extra=None):
    fm, body = fm_split(open(path, encoding='utf-8').read())
    page = dict(fm); page.update(extra or {})
    if 'url' not in page: page['url'] = page.get('permalink', '/')
    out = env.from_string(jekyllize(body)).render(site=site, page=page)
    if path.endswith('.md'): out = kramdown(out)
    layout = page.get('layout') or 'default'
    return render_layout(layout, out, page), page

errors = 0; refs = set()
pages = [os.path.join(ROOT, 'index.html'), os.path.join(ROOT, '404.html')] + glob.glob(os.path.join(ROOT, 'pages', '**', '*.*'), recursive=True)
os.makedirs(OUT, exist_ok=True)
for path in pages:
    try:
        html, page = render_page(path)
        url = page['url']
        dest = os.path.join(OUT, url.strip('/'), 'index.html') if url.endswith('/') else os.path.join(OUT, url.strip('/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True); open(dest, 'w', encoding='utf-8').write(html)
        refs.update(re.findall(r'(?:src|href)="([^"]+)"', html))
    except Exception as e:
        errors += 1; print('ERROR', path, e)
for p in posts:
    try:
        page = dict(p); page['layout'] = 'post'
        body = env.from_string(jekyllize(p['body'])).render(site=site, page=page)
        html = render_layout('post', kramdown(body), page)
        dest = os.path.join(OUT, p['url'].strip('/'), 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True); open(dest, 'w', encoding='utf-8').write(html)
        refs.update(re.findall(r'(?:src|href)="([^"]+)"', html))
    except Exception as e:
        errors += 1; print('ERROR post', p['path'], e)

# check local references
missing = []
for r in sorted(refs):
    if r.startswith('http') or r.startswith('#') or r.startswith('mailto') or r.startswith('javascript'): continue
    r = r.split('#')[0].split('?')[0]
    if baseurl and r.startswith(baseurl): r = r[len(baseurl):]
    local = os.path.join(ROOT, r.lstrip('/'))
    if r.endswith('/'): local = os.path.join(OUT, r.strip('/'), 'index.html')
    if not (os.path.exists(local) or os.path.exists(os.path.join(OUT, r.lstrip('/')))):
        missing.append(r)
print('pages', len(pages), 'posts', len(posts), 'errors', errors, 'refs', len(refs), 'missing', len(missing))
for m in missing[:40]: print('  MISSING', m)
sys.exit(1 if errors else 0)
