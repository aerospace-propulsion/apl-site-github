# APL — 항공우주추진연구실 홈페이지 (GitHub Pages / Jekyll)

서울대학교 항공우주추진연구실(Aerospace Propulsion Laboratory) 공식 홈페이지(apl.snu.ac.kr, WordPress)를
GitHub Pages에서 동작하는 정적 사이트(Jekyll)로 옮긴 저장소입니다. 2026-09-23 기준 원본 사이트의
전체 페이지, 구성원 43명, 논문 119편(국제 97·국내 22), 게시판 61건과 이미지 470여 장을 담고 있습니다.

## 1. 배포 방법 (처음 한 번)

1. GitHub에 새 저장소를 만들고(예: `snu-apl`), 이 폴더의 내용을 `main` 브랜치에 올립니다.
   ```bash
   git init && git add . && git commit -m "APL website (Jekyll)"
   git branch -M main
   git remote add origin https://github.com/<계정 또는 조직>/<저장소>.git
   git push -u origin main
   ```
2. 저장소의 **Settings → Pages** 에서 Source를 **GitHub Actions** 로 선택합니다.
   (`.github/workflows/pages.yml` 이 자동으로 빌드·배포합니다. "Deploy from a branch"를 골라도 됩니다.)
3. `_config.yml` 의 `url` / `baseurl` 을 실제 주소에 맞게 고칩니다.
   - 사용자·조직 페이지 `https://<계정>.github.io` → `baseurl: ""`
   - 프로젝트 페이지 `https://<계정>.github.io/<저장소>` → `baseurl: "/<저장소>"`
   - 커스텀 도메인(apl.snu.ac.kr)을 붙이려면 `CNAME` 파일에 도메인을 한 줄 적고, Settings → Pages 에서 Custom domain을 설정한 뒤 DNS(CNAME 레코드)를 `<계정>.github.io` 로 가리킵니다.

푸시하면 1~2분 뒤 사이트가 갱신됩니다.

## 2. 내용 수정 방법

모든 내용은 GitHub 웹 화면에서 파일을 직접 편집(연필 아이콘)해도 됩니다.

| 무엇을 | 어디를 고치나 |
|---|---|
| 구성원 추가·수정 | `_data/members.yml` (staff / phd / ms / alumni 그룹) |
| 논문 추가 | `_data/publications_international.yml`, `_data/publications_domestic.yml` 맨 위에 항목 추가 |
| 연구 과제 | `_data/projects.yml` (current / past) |
| 홈 슬라이드·공지 | `_data/home.yml` |
| 상단 메뉴 | `_data/nav.yml` |
| 게시판 글 | `_posts/YYYY-MM-DD-제목.md` 파일 추가 (아래 예시) |
| PI 소개 | `pages/member/pi.html` |
| 연구 분야·설비·클러스터·장비예약 | `pages/research/*.html`, `*.md` |
| 찾아오시는 길 | `pages/directions.md` |
| 주소·전화 등 푸터 | `_config.yml` 의 `lab:` 항목 |
| 이미지 | `assets/img/uploads/연도/월/파일명` 에 넣고 위 파일에서 `/assets/img/uploads/...` 로 참조 |

### 게시판 글 예시 (`_posts/2026-10-01-ksas-fall-conference.md`)

```markdown
---
title: 2026 KSAS Fall Conference
date: 2026-10-01
thumb: /assets/img/uploads/2026/10/ksas-fall-1.jpg   # 목록 썸네일(선택)
---

<p><strong>2026.10.01.~03., Jeju</strong></p>
<p>PI, 홍길동</p>
<img src="{{ site.baseurl }}/assets/img/uploads/2026/10/ksas-fall-1.jpg" alt="">
<img src="{{ site.baseurl }}/assets/img/uploads/2026/10/ksas-fall-2.jpg" alt="">
```

파일 이름의 날짜가 글의 날짜가 되고, 주소는 `/board/2026/10/01/ksas-fall-conference/` 가 됩니다.
Markdown으로 써도 되고 HTML을 그대로 써도 됩니다. 이미지는 가로 1600px 이하로 줄여서 올리면 좋습니다.

### 구성원 예시

```yaml
phd:
  - name: 홍길동
    name_en: Gildong Hong
    role: Ph.D. Student
    email: gdhong [at] snu.ac.kr
    photo: /assets/img/uploads/2026/09/hong.jpg
    topics:
      - Hypersonic aerodynamics
      - Shock tunnel experiments
```

## 3. 원본 사이트와 달라진 점

- **게시판(Board)** : WordPress KBoard의 글 61건을 정적 페이지로 옮겼습니다. 댓글·글쓰기 기능은 없으며, 새 글은 `_posts/`에 파일을 추가합니다.
- **장비 예약(Equipments Reservation)** : 온라인 예약 폼 대신 담당자 이메일 안내로 대체했습니다.
- **구성원 개인 페이지** : 원본에서 내용이 비어 있던 개별 페이지는 만들지 않고 목록 카드만 유지했습니다.
- **홈 슬라이드의 애니메이션 GIF 3개**(17~74 MB)는 용량 문제로 MP4 동영상(총 6 MB)으로 바꿨습니다.
- 모든 이미지를 가로 1600px(썸네일 780px) 이하로 줄여 총 390 MB → 83 MB 로 만들었습니다.
- 로그인, 검색, 개인정보처리방침 페이지, 사이트맵 메뉴는 제외했습니다.

## 4. 로컬에서 미리보기 (선택)

Ruby가 설치되어 있으면 GitHub Pages와 같은 환경으로 확인할 수 있습니다.

```bash
bundle install
bundle exec jekyll serve
# http://localhost:4000
```

`tools/` 폴더에는 원본 사이트에서 자료를 옮길 때 쓴 스크립트가 들어 있으며 사이트 동작과는 무관합니다.
