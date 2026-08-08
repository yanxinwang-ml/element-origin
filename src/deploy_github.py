# Deploy the static site to GitHub Pages via the GitHub REST API.
# Uses the Contents API so it works even on a freshly created empty repo.
import base64
import json
import os
import time
import urllib.error
import urllib.request

TOKEN = open(os.path.join(os.environ["TEMP"], "gh_token.txt"), encoding="ascii").read().strip()
API = "https://api.github.com"
BASE_H = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "User-Agent": "codex-deploy",
}


def req(method, path, payload=None):
    headers = dict(BASE_H)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=40) as resp:
            body = resp.read().decode()
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            j = json.loads(body) if body else None
        except Exception:
            j = body
        return e.code, j


status, user = req("GET", "/user")
if status != 200:
    raise SystemExit("user lookup failed: %s %s" % (status, user))
login = user["login"]
print("login:", login)

# Reuse an existing empty repo named element-origin, otherwise create it.
name = "element-origin"
status, repo = req("GET", "/repos/%s/%s" % (login, name))
if status == 200:
    check, _ = req("GET", "/repos/%s/%s/contents/" % (login, name))
    if check in (404, 409):  # empty repository
        print("reusing empty repo:", name)
    else:
        raise SystemExit("repo %s already has content; pick another name" % name)
else:
    status, repo = req("POST", "/user/repos", {
        "name": name,
        "description": "元素起源 · 宇宙元素生成交互示意图（核合成动画）",
        "public": True,
        "has_issues": False,
        "has_projects": False,
        "has_wiki": False,
    })
    print("create repo:", status)
    if status not in (200, 201):
        print(repo)
        raise SystemExit(1)

branch = repo["default_branch"]
print("default branch:", branch)

files = (
    "index.html", "elements_data.js", "simulator.js", "README.md",
    "data/element_metadata.csv", "data/lodders09.dat",
    "data/periodic_elements.json", "src/generate_data.py",
)
for rel in files:
    with open(rel, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    payload = {
        "message": "添加 %s" % rel,
        "content": content,
        "branch": branch,
    }
    status, body = req("PUT", "/repos/%s/%s/contents/%s" % (login, name, rel), payload)
    if status not in (200, 201):
        raise SystemExit("content failed for %s: %s %s" % (rel, status, body))
    print("uploaded:", rel)

status, p = req("POST", "/repos/%s/%s/pages" % (login, name),
                {"source": {"branch": branch, "path": "/"}})
print("pages create:", status)
if status not in (200, 201):
    print(p)
    status2, p2 = req("PUT", "/repos/%s/%s/pages" % (login, name),
                      {"source": {"branch": branch, "path": "/"}})
    print("pages put:", status2, "ok" if status2 in (200, 201) else p2)

for i in range(36):
    time.sleep(10)
    status, pg = req("GET", "/repos/%s/%s/pages" % (login, name))
    st = pg.get("status") if isinstance(pg, dict) else None
    print("pages status:", st)
    if st == "built":
        print("PAGES_URL:", pg.get("html_url"))
        break
    if st == "errored":
        print(pg)
        break
