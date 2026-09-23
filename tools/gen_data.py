#!/usr/bin/env python3
"""Generate _data/*.yml and _posts/*.md from the scraped JSON (one-time migration helper)."""
import json, re, os, sys, urllib.parse, yaml, datetime

SRC = sys.argv[1]           # scratchpad dir with pubs.json, members.json, posts1.json, posts2.json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = '/assets/img/uploads/'

def dec(p):
    return urllib.parse.unquote(p)

class Dumper(yaml.SafeDumper):
    pass
def str_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
Dumper.add_representer(str, str_presenter)

def dump(obj, path, header):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header)
        yaml.dump(obj, f, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=1000)

# ---------- members ----------
m = json.load(open(os.path.join(SRC, 'members.json'), encoding='utf-8'))
def conv_member(x):
    info = x.get('info', [])
    email = None; topics = []; position = None
    for s in info:
        if '[at]' in s:
            email = s
        else:
            topics.append(s)
    d = {'name': x['name']}
    if x.get('en'): d['name_en'] = x['en']
    d['role'] = x['role']
    if email: d['email'] = email
    d['photo'] = IMG + dec(x['img'])
    return d, topics

out = {}
for group in ['staff', 'phd', 'ms', 'alumni']:
    lst = []
    for x in m[group]:
        d, topics = conv_member(x)
        if group == 'alumni':
            # first non-email line is the current affiliation, the rest are research topics
            if topics:
                d['current'] = topics[0]
                topics = topics[1:]
        if topics: d['topics'] = topics
        lst.append(d)
    out[group] = lst
header = """# 구성원 명단. 각 그룹(staff / phd / ms / alumni)의 항목을 추가·수정하면 페이지에 자동 반영됩니다.
# 필드: name(필수), name_en, role, email, photo(/assets/img/uploads/... 또는 외부 URL), topics(목록), current(alumni 현재 소속)
# 사진이 없으면 photo에 /assets/img/uploads/2024/08/APL-로고-03.png 을 넣으면 됩니다.
"""
dump(out, os.path.join(ROOT, '_data', 'members.yml'), header)

# ---------- publications ----------
p = json.load(open(os.path.join(SRC, 'pubs.json'), encoding='utf-8'))
def conv_pub(x):
    yr = re.search(r'\((\d{4})\)', x['c'])
    d = {'title': x['t'], 'authors_journal': x['c'], 'year': int(yr.group(1)) if yr else None,
         'url': x['u'], 'image': IMG + dec(x['img'])}
    return d
header = """# 논문 목록 (최신순). 새 논문은 맨 위에 추가하면 됩니다.
# 필드: title, authors_journal(저자·학술지·권호 한 줄), year, url(DOI 링크), image(대표 그림)
"""
dump([conv_pub(x) for x in p['intl']], os.path.join(ROOT, '_data', 'publications_international.yml'), header)
dump([conv_pub(x) for x in p['dom']], os.path.join(ROOT, '_data', 'publications_domestic.yml'), header)

# ---------- posts ----------
posts = json.load(open(os.path.join(SRC, 'posts1.json'), encoding='utf-8')) + \
        json.load(open(os.path.join(SRC, 'posts2.json'), encoding='utf-8'))
os.makedirs(os.path.join(ROOT, '_posts'), exist_ok=True)
def slug(s):
    s = re.sub(r'[^A-Za-z0-9\s-]', '', s).strip().lower()
    s = re.sub(r'[\s_]+', '-', s)
    return s[:60].strip('-')
seen = {}
for x in posts:
    html = x['html']
    html = re.sub(r'src="(?!https?://)([^"]+)"', lambda mm: 'src="{{ site.baseurl }}' + IMG + dec(mm.group(1)) + '"', html)
    html = html.replace('&nbsp;', ' ')
    html = re.sub(r'(<br>\s*)+$', '', html).strip()
    html = re.sub(r'<img ', '<img loading="lazy" ', html)
    # separate images by newlines for readability
    html = re.sub(r'>\s*<img', '>\n<img', html)
    html = re.sub(r'</p>\s*<', '</p>\n<', html)
    sl = slug(x['title']) or ('post-' + x['id'])
    base = f"{x['date']}-{sl}"
    n = seen.get(base, 0); seen[base] = n + 1
    fname = base + (f"-{n+1}" if n else '') + '.md'
    thumb = IMG + dec(x['thumb']) if x.get('thumb') else None
    fm = {'title': x['title'], 'date': x['date'], 'kboard_id': int(x['id'])}
    if thumb: fm['thumb'] = thumb
    with open(os.path.join(ROOT, '_posts', fname), 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(fm, f, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=1000)
        f.write('---\n\n' + html + '\n')
print('members', {k: len(v) for k, v in out.items()}, 'pubs', len(p['intl']), len(p['dom']), 'posts', len(posts))
