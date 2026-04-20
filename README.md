# CoPilot Scheduler Authentication Bypass PoC

This repository contains a proof of concept for an **authentication bypass affecting the scheduler router** in CoPilot.

## Summary

The scheduler endpoints appear to be exposed without authentication checks. Based on testing against an authorized target, the following behavior was observed:

- `GET /api/scheduler` returned HTTP 200 without an `Authorization` header
- `POST /api/scheduler/jobs/run/<job_id>` was reachable without authentication
- In the provided test result, the POST request returned HTTP 500 rather than HTTP 401/403, which indicates the request passed the authentication boundary and reached server-side execution logic

## Impact

An unauthenticated attacker may be able to:

- Enumerate internal scheduled jobs
- Learn operational details about backend components and job cadence
- Attempt unauthorized execution of scheduler jobs
- Abuse job triggers to cause operational disruption, backend load, or workflow manipulation

## Affected Area

- `backend/app/schedulers/routes/scheduler.py`
- Router mounted at `/api/scheduler`

## PoC

### Requirements

```bash
pip install requests
```

### Enumerate jobs without auth

```bash
python 02_unauth_scheduler.py --target http://localhost:5000
```

### Attempt unauthorized job execution

```bash
python 02_unauth_scheduler.py --target http://localhost:5000 --run-job invoke_alert_creation_collect
```

## Expected Secure Behavior

Unauthenticated requests to scheduler endpoints should return `401 Unauthorized` or `403 Forbidden`.

## Notes on Current Validation State

This PoC **confirms missing authentication on the scheduler router**.

For `POST /api/scheduler/jobs/run/<job_id>`, the current result shows that the endpoint is not auth-gated, but the specific test run returned HTTP 500, so successful job completion should be treated as **not yet conclusively proven** from this single run.

## Recommended Remediation

- Apply authentication middleware/dependencies to all scheduler endpoints
- Restrict scheduler actions to administrative users only
- Add authorization checks for job execution endpoints
- Add audit logging for scheduler access and job execution attempts
- Consider rate limiting for execution endpoints

## Disclaimer

Run this PoC only against systems you own or are explicitly authorized to test.
