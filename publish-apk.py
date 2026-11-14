#!/usr/bin/env python3
"""Upload an APK as a GitHub Release asset.

usage: publish-apk.py <repo> <tag> <apk-path> <notes>

**This script cannot run until a GitHub PAT is provisioned again.**

It used to read a 'hermes git token' PAT from the GNOME keyring. That PAT
is DEAD — it returns 401 on api.github.com/user — and it was deleted on
2026-11-14 along with the `github_pat` registry slot and the `gh` CLI's
hosts.yml token. Every PAT on this box was revoked.

Creating a Release and attaching an asset to it needs the **GitHub REST
API**, and the REST API needs a token. SSH cannot do this — SSH is for
git transport, not for the API.

To restore it:

  1. Create a fine-grained PAT at
     https://github.com/settings/personal-access-tokens with
     `Contents: read and write` on the target repo.
  2. Store it in the GNOME keyring under its OWN service, so it cannot
     collide with another item:

       secret-tool store --label='GitHub fine-grained PAT (live)' \
         service=github-fine-grained

  3. Read it back with:

       secret-tool lookup service github-fine-grained

Do NOT reuse `service=git` — that namespace already caused an ambiguous
lookup, and two items sharing one service is the hazard the keyring skill
documents.

Until then this exits with a clear message instead of a bare StopIteration.
"""
import os, sys, json, urllib.parse, urllib.request, urllib.error

if len(sys.argv) < 5:
    raise SystemExit(__doc__)

REPO, TAG, APK_PATH, NOTES = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

os.environ.setdefault("DBUS_SESSION_BUS_ADDRESS",
                      f"unix:path=/run/user/{os.getuid()}/bus")
import secretstorage
from secretstorage.collection import search_items

KEYRING_SERVICE = "github-fine-grained"

token = None
for it in search_items(secretstorage.dbus_init(), {}):
    # secretstorage.Item has no get_service(); the service is an attribute.
    if (it.get_attributes() or {}).get("service") == KEYRING_SERVICE:
        token = it.get_secret().decode()
        break

if not token:
    raise SystemExit(
        "No GitHub token is available.\n"
        "Every PAT on this box was revoked (401 on api.github.com/user), and\n"
        "the dead ones were deleted on 2026-11-14. Publishing a Release needs\n"
        "the GitHub REST API, which needs a token - SSH cannot do it.\n"
        "\n"
        "Create a fine-grained PAT with Contents:read+write on the target\n"
        "repo, then store it:\n"
        "  secret-tool store --label='GitHub fine-grained PAT (live)' \\\n"
        "    service=github-fine-grained\n"
    )

BASE = f"https://api.github.com/repos/{REPO}"
HEADERS = {"Authorization": f"Bearer {token}",
           "Accept": "application/vnd.github+json",
           "User-Agent": "hermes"}

def api(method, url, data=None, headers=None):
    h = dict(HEADERS)
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        print(f"  HTTP {e.code} on {method} {url}\n  {detail}", file=sys.stderr)
        raise

# 1. create the release (ignore 422 = already exists, then fetch it)
rel_url = f"{BASE}/releases/tags/{TAG}"
try:
    rel = api("POST", f"{BASE}/releases",
              json.dumps({"tag_name": TAG, "name": f"HTMA Mobile {TAG}",
                          "body": NOTES, "draft": False,
                          "prerelease": False}).encode(),
              {"Content-Type": "application/json"})
    print(f"  created release {rel['html_url']}")
except urllib.error.HTTPError as e:
    if e.code != 422:
        raise
    print(f"  release {TAG} exists, reusing it")
    rel = api("GET", rel_url)

# 2. drop any previous asset with this name, then upload.
#    Assets are listed by release ID, NOT by tag — /releases/tags/<tag>/assets
#    is a 404 and the upload step then fails on an empty asset list.
name = os.path.basename(APK_PATH)
assets_url = f"{BASE}/releases/{rel['id']}/assets"
for a in api("GET", assets_url):
    if a["name"] == name:
        api("DELETE", f"{BASE}/releases/assets/{a['id']}")
        print(f"  replaced existing asset {name}")

size = os.path.getsize(APK_PATH)
print(f"  uploading {name} ({size/1048576:.1f} MB)")
with open(APK_PATH, "rb") as f:
    payload = f.read()
ctype = "application/vnd.android.package-archive"
upload = urllib.request.Request(
    f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets"
    f"?name={urllib.parse.quote(name)}",
    data=payload,
    headers={**HEADERS, "Content-Type": ctype,
             "Content-Length": str(len(payload))},
    method="POST")
# urllib Request is not a context manager — urlopen() is.
with urllib.request.urlopen(upload, timeout=900) as r:
    asset = json.loads(r.read())

print(f"  DONE {asset['name']}  {asset['size']/1048576:.1f} MB")
print(f"  {asset['browser_download_url']}")