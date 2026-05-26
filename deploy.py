"""
One-command deployment script for USContentHub.
Automates: CSS cache bust → collectstatic → git push → PythonAnywhere pull + reload.

Usage:
    python deploy.py "your commit message"
    python deploy.py                        # prompts for message

First run:
    Set your PythonAnywhere API token:
        set PA_API_TOKEN=your_token_here          (cmd)
        $env:PA_API_TOKEN = "your_token_here"     (PowerShell)
    Or create a .env file with: PA_API_TOKEN=your_token_here

    Get your token at: https://www.pythonanywhere.com/user/{username}/account/#api_token
"""

import os
import re
import sys
import subprocess
import urllib.request
import urllib.error
import json
import time

# ── Config ───────────────────────────────────────────────────────────
PA_USERNAME = "tusharlimbasiya200"
PA_DOMAIN = f"{PA_USERNAME}.pythonanywhere.com"
PA_API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_HTML = os.path.join(PROJECT_DIR, "blog", "templates", "blog", "base.html")
PYTHON = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON):
    PYTHON = os.path.join(PROJECT_DIR, "venv", "bin", "python")  # Linux/Mac
REMOTE_PROJECT = f"/home/{PA_USERNAME}/USContentHub"
# ─────────────────────────────────────────────────────────────────────

# Colors for terminal output
class C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def log(icon, msg):
    print(f"  {icon}  {msg}")


def step(num, title):
    print(f"\n{C.CYAN}{C.BOLD}[{num}]{C.END} {C.BOLD}{title}{C.END}")


def ok(msg):
    log(f"{C.GREEN}✓{C.END}", msg)


def fail(msg):
    log(f"{C.RED}✗{C.END}", f"{C.RED}{msg}{C.END}")


def warn(msg):
    log(f"{C.YELLOW}!{C.END}", f"{C.YELLOW}{msg}{C.END}")


def run(cmd, cwd=None, check=True):
    """Run a shell command and return stdout. Raises on failure if check=True."""
    result = subprocess.run(
        cmd, cwd=cwd or PROJECT_DIR,
        capture_output=True, text=True, shell=True
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed: {cmd}\n{stderr}")
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def get_api_token():
    """Read PA API token from env or .env file."""
    token = os.environ.get("PA_API_TOKEN", "").strip()
    if token:
        return token
    env_file = os.path.join(PROJECT_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("PA_API_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip("'\"")
                    if token:
                        return token
    return None


def pa_api(method, endpoint, data=None, token=None):
    """Make a PythonAnywhere API request."""
    url = f"{PA_API_BASE}/{endpoint}"
    headers = {"Authorization": f"Token {token}"}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data.encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except urllib.error.URLError as e:
        return 0, str(e.reason)


# ── Step 1: Bump CSS version ────────────────────────────────────────
def bump_css_version():
    step(1, "Bump CSS cache version")
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    match = re.search(r"(style\.css\?v=)(\d+)", html)
    if not match:
        warn("No CSS version found in base.html — skipping bump")
        return None

    old_ver = int(match.group(2))
    new_ver = old_ver + 1
    html = html.replace(f"style.css?v={old_ver}", f"style.css?v={new_ver}")

    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    ok(f"v={old_ver} → v={new_ver}")
    return new_ver


# ── Step 2: collectstatic ───────────────────────────────────────────
def collect_static():
    step(2, "Collect static files")
    out, err, code = run(f'"{PYTHON}" manage.py collectstatic --noinput')
    # Extract the summary line
    for line in (out + "\n" + err).splitlines():
        if "static file" in line.lower():
            ok(line.strip())
            return
    ok("Done")


# ── Step 3: Git add, commit, push ───────────────────────────────────
def git_push(commit_msg):
    step(3, "Git add → commit → push")

    # Check for changes
    out, _, _ = run("git status --porcelain", check=False)
    if not out.strip():
        warn("No changes to commit — pushing anyway in case of unpushed commits")
        _, _, code = run("git push", check=False)
        if code == 0:
            ok("Pushed (no new commit needed)")
        else:
            fail("Push failed — check your git remote / auth")
            return False
        return True

    # Stage all
    run("git add -A")
    ok(f"Staged {len(out.strip().splitlines())} file(s)")

    # Commit
    # Escape double quotes in commit message
    safe_msg = commit_msg.replace('"', '\\"')
    out, err, code = run(f'git commit -m "{safe_msg}"', check=False)
    if code != 0:
        if "nothing to commit" in (out + err):
            warn("Nothing to commit")
        else:
            fail(f"Commit failed: {err or out}")
            return False
    else:
        # Extract short hash
        hash_match = re.search(r"\[[\w-]+ ([a-f0-9]+)\]", out)
        short = hash_match.group(1) if hash_match else "?"
        ok(f"Committed ({short})")

    # Push
    out, err, code = run("git push", check=False)
    if code != 0:
        fail(f"Push failed: {err or out}")
        return False
    ok("Pushed to GitHub")
    return True


# ── Step 4: PythonAnywhere — pull + collectstatic ────────────────────
def pa_pull_and_collect(token):
    step(4, "PythonAnywhere — git pull + collectstatic")

    # Create a new temporary console to run commands
    import urllib.parse

    # First try to get existing consoles
    status, body = pa_api("GET", "consoles/", token=token)
    if status != 200:
        fail(f"Cannot list consoles (HTTP {status}): {body[:200]}")
        return False

    consoles = json.loads(body)
    console_id = None

    # Find an existing bash console or create one
    for c in consoles:
        if c.get("executable", "").endswith("bash"):
            console_id = c["id"]
            break

    if not console_id:
        # Create a new bash console
        status, body = pa_api("POST", "consoles/", data={"executable": "bash"}, token=token)
        if status not in (200, 201):
            fail(f"Cannot create console (HTTP {status}): {body[:200]}")
            return False
        console_id = json.loads(body)["id"]

    ok(f"Using console {console_id}")

    # Send the deploy commands
    cmd = f"cd {REMOTE_PROJECT} && git stash 2>/dev/null; git pull && python manage.py collectstatic --noinput\n"
    status, body = pa_api("POST", f"consoles/{console_id}/send_input/",
                          data={"input": cmd}, token=token)
    if status != 200:
        fail(f"Cannot send command (HTTP {status}): {body[:200]}")
        return False

    ok("Sent pull + collectstatic command")

    # Wait for command to finish by polling output
    time.sleep(3)
    for attempt in range(10):
        status, body = pa_api("GET", f"consoles/{console_id}/latest_output/", token=token)
        if status == 200:
            output = json.loads(body).get("output", "")
            if "static file" in output.lower() or "unmodified" in output.lower():
                # Find the summary line
                for line in output.splitlines():
                    if "static file" in line.lower():
                        ok(line.strip())
                        break
                else:
                    ok("Pull + collectstatic completed")
                return True
            if "error" in output.lower() and "merge" in output.lower():
                fail("Git merge conflict on PythonAnywhere — resolve manually")
                return False
        time.sleep(2)

    warn("Could not confirm completion — proceeding with reload anyway")
    return True


# ── Step 5: Reload webapp ────────────────────────────────────────────
def pa_reload(token):
    step(5, "PythonAnywhere — reload webapp")
    status, body = pa_api("POST", f"webapps/{PA_DOMAIN}/reload/", token=token)
    if status == 200:
        ok(f"Webapp reloaded at https://{PA_DOMAIN}")
        return True
    elif status == 401:
        fail("Invalid API token (401). Regenerate at:")
        fail(f"  https://www.pythonanywhere.com/user/{PA_USERNAME}/account/#api_token")
        return False
    elif status == 409:
        warn("Webapp is already reloading — waiting...")
        time.sleep(5)
        return True
    else:
        fail(f"Reload failed (HTTP {status}): {body[:200]}")
        return False


# ── Step 6: Verify ──────────────────────────────────────────────────
def verify_site():
    step(6, "Verify site is live")
    url = f"https://{PA_DOMAIN}/"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                ok(f"Site is UP — {url}")
                return True
            else:
                warn(f"Site returned HTTP {resp.status}")
                return True
    except Exception as e:
        fail(f"Site check failed: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────
def main():
    print(f"\n{C.BOLD}{'═' * 50}")
    print(f"  USContentHub — Deploy")
    print(f"{'═' * 50}{C.END}")

    # Get commit message
    if len(sys.argv) > 1:
        commit_msg = " ".join(sys.argv[1:])
    else:
        commit_msg = input(f"\n  {C.CYAN}Commit message:{C.END} ").strip()
        if not commit_msg:
            fail("No commit message provided. Aborting.")
            sys.exit(1)

    # Get API token
    token = get_api_token()
    if not token:
        warn("PA_API_TOKEN not set — will skip PythonAnywhere steps")
        warn("Set it: $env:PA_API_TOKEN = 'your_token'")
        warn(f"Get it: https://www.pythonanywhere.com/user/{PA_USERNAME}/account/#api_token")
        pa_enabled = False
    else:
        pa_enabled = True

    errors = []

    # Step 1
    try:
        bump_css_version()
    except Exception as e:
        fail(f"CSS bump failed: {e}")
        errors.append(("CSS bump", str(e)))

    # Step 2
    try:
        collect_static()
    except Exception as e:
        fail(f"collectstatic failed: {e}")
        errors.append(("collectstatic", str(e)))
        fail("Aborting — static files must collect before deploying")
        sys.exit(1)

    # Step 3
    try:
        if not git_push(commit_msg):
            errors.append(("git push", "see above"))
    except Exception as e:
        fail(f"Git failed: {e}")
        errors.append(("git", str(e)))

    # Steps 4–5 (PythonAnywhere)
    if pa_enabled and not errors:
        try:
            if not pa_pull_and_collect(token):
                errors.append(("PA pull", "see above"))
        except Exception as e:
            fail(f"PA pull failed: {e}")
            errors.append(("PA pull", str(e)))

        try:
            if not pa_reload(token):
                errors.append(("PA reload", "see above"))
        except Exception as e:
            fail(f"PA reload failed: {e}")
            errors.append(("PA reload", str(e)))
    elif not pa_enabled:
        print(f"\n{C.YELLOW}  ⚠ Skipped PythonAnywhere deploy (no API token){C.END}")
        print(f"  Run manually on PythonAnywhere console:")
        print(f"    cd {REMOTE_PROJECT} && git pull && python manage.py collectstatic --noinput")
        print(f"  Then reload the webapp from the Web tab.")

    # Step 6
    if pa_enabled:
        try:
            verify_site()
        except Exception as e:
            warn(f"Verify failed: {e}")

    # Summary
    print(f"\n{C.BOLD}{'─' * 50}{C.END}")
    if errors:
        print(f"  {C.RED}{C.BOLD}Deploy finished with {len(errors)} error(s):{C.END}")
        for name, detail in errors:
            print(f"    {C.RED}• {name}: {detail}{C.END}")
    else:
        print(f"  {C.GREEN}{C.BOLD}Deploy successful!{C.END} 🚀")
    print()


if __name__ == "__main__":
    import urllib.parse
    main()
