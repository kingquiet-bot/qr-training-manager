#!/usr/bin/env python3
"""
Training & Event Attendance Manager — Backend (stdlib only)
============================================================
Zero-dependency backend: uses only Python standard library modules.
Receives check-in data from the PWA frontend and persists it to SQLite.

Endpoints:
  POST   /api/checkin           — Record a check-in
  GET    /api/checkin?event_id= — List check-ins (optional event_id filter)
  GET    /api/events            — List all events
  POST   /api/events            — Create an event
  GET    /api/events/<id>       — Get event details with attendees
  DELETE /api/events/<id>       — Delete an event
  GET    /api/users             — List demo users
  GET    /api/analytics         — Dashboard stats
  GET    /api/health            — Health check
  GET    /                      — Serve index.html (PWA frontend)
"""

import sqlite3
import json
import os
import re
import uuid
import io
import csv
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Configuration ──────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "attendance.db")

# Load .env file if present (simple parser, no external deps)
_ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.isfile(_ENV_FILE):
    with open(_ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

# ── Database Initialization ────────────────────────────────────
def migrate_db(db):
    """Add missing columns to existing tables (safe to call repeatedly)."""
    try:
        db.execute("ALTER TABLE events ADD COLUMN status TEXT NOT NULL DEFAULT 'upcoming'")
    except sqlite3.OperationalError:
        pass  # column already exists
    try:
        db.execute("ALTER TABLE registered_attendees ADD COLUMN phone TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass


def init_db():
    """Create tables if they don't exist; seed demo users."""
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            date        TEXT NOT NULL,
            time        TEXT DEFAULT '',
            location    TEXT DEFAULT '',
            description TEXT DEFAULT '',
            status      TEXT NOT NULL DEFAULT 'upcoming',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id      TEXT PRIMARY KEY,
            pin     TEXT NOT NULL UNIQUE,
            name    TEXT NOT NULL,
            dept    TEXT DEFAULT '',
            active  INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id              TEXT PRIMARY KEY,
            event_id        TEXT NOT NULL,
            emp_code        TEXT NOT NULL,
            checkin_method  TEXT NOT NULL DEFAULT 'manual',
            timestamp       TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS registered_attendees (
            id        TEXT PRIMARY KEY,
            event_id  TEXT NOT NULL,
            emp_code  TEXT NOT NULL,
            name      TEXT NOT NULL DEFAULT '',
            dept      TEXT DEFAULT '',
            phone     TEXT DEFAULT '',
            status    TEXT NOT NULL DEFAULT 'registered',
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS active_qr_list (
            emp_id  TEXT NOT NULL,
            name    TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS attendance_history (
            id              TEXT PRIMARY KEY,
            emp_id          TEXT NOT NULL,
            name            TEXT NOT NULL DEFAULT '',
            event_id        TEXT DEFAULT '',
            checkin_method  TEXT NOT NULL DEFAULT 'manual',
            timestamp       TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_att_event   ON attendance(event_id);
        CREATE INDEX IF NOT EXISTS idx_att_emp     ON attendance(emp_code);
        CREATE INDEX IF NOT EXISTS idx_att_ts      ON attendance(timestamp);
        CREATE INDEX IF NOT EXISTS idx_reg_event   ON registered_attendees(event_id);
        CREATE INDEX IF NOT EXISTS idx_reg_emp     ON registered_attendees(emp_code);
        CREATE INDEX IF NOT EXISTS idx_hist_emp    ON attendance_history(emp_id);
        CREATE INDEX IF NOT EXISTS idx_hist_ts     ON attendance_history(timestamp);
    """)

    migrate_db(db)  # catch up existing databases

    demo_users = [
        ("U001", "1001", "Alice Johnson", "Engineering"),
        ("U002", "1002", "Bob Martinez",  "HR"),
        ("U003", "1003", "Carol Nguyen",  "Operations"),
        ("U004", "1004", "David Kim",     "Engineering"),
        ("U005", "1005", "Eva Patel",     "Finance"),
        ("U006", "2001", "Frank Okafor",  "Safety"),
        ("U007", "2002", "Grace Li",      "Safety"),
    ]
    db.executemany(
        "INSERT OR IGNORE INTO users (id, pin, name, dept) VALUES (?, ?, ?, ?)",
        demo_users,
    )
    db.commit()
    db.close()


# ── Helpers ────────────────────────────────────────────────────
def gen_id(prefix="id"):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def get_db():
    """Open a connection each request (simple, thread-safe enough for dev)."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def json_response(handler, data, status=200):
    """Send a JSON response."""
    body = json.dumps(data, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def read_json_body(handler):
    """Read JSON body from request."""
    try:
        length = int(handler.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = handler.rfile.read(length)
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}


# ── Route Handlers ─────────────────────────────────────────────

def handle_health(handler):
    return json_response(handler, {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def handle_list_users(handler):
    db = get_db()
    try:
        rows = db.execute(
            "SELECT id, pin, name, dept, active FROM users ORDER BY id"
        ).fetchall()
        return json_response(handler, [dict(r) for r in rows])
    finally:
        db.close()


def handle_list_events(handler):
    db = get_db()
    try:
        rows = db.execute("""
            SELECT e.*, COUNT(a.id) AS attendee_count
            FROM events e
            LEFT JOIN attendance a ON a.event_id = e.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
        """).fetchall()
        events = [dict(r) for r in rows]
        # Add explicit checkins_count for frontend dashboard compatibility
        for ev in events:
            ev["checkins_count"] = ev["attendee_count"]
        return json_response(handler, events)
    finally:
        db.close()


def handle_create_event(handler):
    body = read_json_body(handler)
    name = (body.get("name") or "").strip()
    date = (body.get("date") or "").strip()
    if not name or not date:
        return json_response(handler, {"error": "name and date are required"}, 400)

    event = {
        "id": gen_id("ev"),
        "name": name,
        "date": date,
        "time": (body.get("time") or "").strip(),
        "location": (body.get("location") or "").strip(),
        "description": (body.get("description") or "").strip(),
    }

    db = get_db()
    try:
        db.execute(
            """INSERT INTO events (id, name, date, time, location, description)
               VALUES (:id, :name, :date, :time, :location, :description)""",
            event,
        )
        db.commit()
    finally:
        db.close()
    event["attendee_count"] = 0
    return json_response(handler, event, 201)


def handle_get_event(handler, event_id):
    db = get_db()
    try:
        event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)

        attendees = db.execute(
            """SELECT a.id, a.emp_code, a.checkin_method, a.timestamp,
                      u.name AS user_name, u.dept AS user_dept
               FROM attendance a
               LEFT JOIN users u ON u.id = a.emp_code
               WHERE a.event_id = ?
               ORDER BY a.timestamp DESC""",
            (event_id,),
        ).fetchall()

        registered = db.execute(
            """SELECT id, emp_code, name, dept, phone, status
               FROM registered_attendees
               WHERE event_id = ?
               ORDER BY name""",
            (event_id,),
        ).fetchall()

        result = dict(event)
        result["attendees"] = [dict(a) for a in attendees]
        result["attendee_count"] = len(attendees)
        result["registered"] = [dict(r) for r in registered]
        result["registered_count"] = len(registered)
        return json_response(handler, result)
    finally:
        db.close()


def validate_phone(phone):
    """Return (is_valid, error_message). Phone must start with '09' and contain no spaces."""
    if not phone or not phone.strip():
        return True, ""  # phone is optional
    p = phone.strip()
    if " " in p:
        return False, f"Phone \"{p}\" must not contain spaces."
    if not p.startswith("09"):
        return False, f"Phone \"{p}\" must start with '09'."
    return True, ""


def handle_register_attendees(handler, event_id):
    """POST /api/events/<id>/register — bulk register attendees for an event."""
    db = get_db()
    try:
        event = db.execute("SELECT id, name FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)

        body = read_json_body(handler)
        attendees = body.get("attendees", [])
        if not isinstance(attendees, list) or len(attendees) == 0:
            return json_response(handler, {"error": "attendees array is required"}, 400)

        inserted = 0
        skipped = 0
        rejected = []  # rows rejected due to phone validation
        for att in attendees:
            raw_code = (att.get("emp_code") or "").strip()
            if not raw_code:
                skipped += 1
                continue

            # Strict phone validation
            raw_phone = (att.get("phone") or "").strip()
            phone_valid, phone_err = validate_phone(raw_phone if raw_phone else "")
            if not phone_valid:
                rejected.append({"emp_code": raw_code, "error": phone_err})
                continue

            # Resolve to canonical user ID (ID or PIN lookup)
            user = db.execute(
                "SELECT id, name, dept FROM users WHERE id = ? OR pin = ?",
                (raw_code, raw_code),
            ).fetchone()
            if user:
                emp_code = user["id"]
                name = user["name"]
                dept = user["dept"]
            else:
                # Unknown user — store as-is with provided name/dept
                emp_code = raw_code
                name = (att.get("name") or raw_code).strip()
                dept = (att.get("dept") or "").strip()

            # Check if already registered for this event
            existing = db.execute(
                "SELECT id FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
                (event_id, emp_code),
            ).fetchone()
            if existing:
                skipped += 1
                continue

            phone = att.get("phone", "")
            reg_id = gen_id("reg")
            db.execute(
                """INSERT INTO registered_attendees (id, event_id, emp_code, name, dept, phone)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (reg_id, event_id, emp_code, name, dept, phone),
            )
            # Auto-sync to active_qr_list so the Telegram bot instantly recognizes new users
            db.execute(
                "INSERT OR IGNORE INTO active_qr_list (emp_id, name) VALUES (?, ?)",
                (emp_code, name),
            )
            inserted += 1

        db.commit()
        resp = {
            "status": "ok",
            "event_id": event_id,
            "event_name": event["name"],
            "inserted": inserted,
            "skipped": skipped,
        }
        if rejected:
            resp["rejected"] = rejected
        return json_response(handler, resp, 201)
    finally:
        db.close()


def handle_get_registered(handler, event_id):
    """GET /api/events/<id>/registered — list registered attendees."""
    db = get_db()
    try:
        event = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)

        rows = db.execute(
            """SELECT id, emp_code, name, dept, phone, status
               FROM registered_attendees
               WHERE event_id = ?
               ORDER BY name""",
            (event_id,),
        ).fetchall()
        return json_response(handler, [dict(r) for r in rows])
    finally:
        db.close()


def handle_delete_registered(handler, event_id, emp_code):
    """DELETE /api/events/<id>/registered/<emp_code> — remove a registration."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT id FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        ).fetchone()
        if not row:
            return json_response(handler, {"error": "registration not found"}, 404)

        db.execute(
            "DELETE FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        )
        db.commit()
        return json_response(handler, {"status": "deleted", "emp_code": emp_code})
    finally:
        db.close()


def handle_delete_event(handler, event_id):
    db = get_db()
    try:
        event = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)
        db.execute("DELETE FROM registered_attendees WHERE event_id = ?", (event_id,))
        db.execute("DELETE FROM attendance WHERE event_id = ?", (event_id,))
        db.execute("DELETE FROM events WHERE id = ?", (event_id,))
        db.commit()
    finally:
        db.close()
    return json_response(handler, {"status": "deleted", "id": event_id})


def handle_checkin_list(handler, query):
    """GET /api/checkin?event_id=...  — list check-ins"""
    db = get_db()
    try:
        event_id = query.get("event_id", [None])[0]
        if event_id:
            rows = db.execute(
                """SELECT a.*, u.name AS user_name, u.dept AS user_dept
                   FROM attendance a
                   LEFT JOIN users u ON u.id = a.emp_code
                   WHERE a.event_id = ?
                   ORDER BY a.timestamp DESC""",
                (event_id,),
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT a.*, u.name AS user_name, u.dept AS user_dept
                   FROM attendance a
                   LEFT JOIN users u ON u.id = a.emp_code
                   ORDER BY a.timestamp DESC
                   LIMIT 100"""
            ).fetchall()
        return json_response(handler, [dict(r) for r in rows])
    finally:
        db.close()


def handle_checkin(handler):
    """POST /api/checkin — record a training attendance check-in.

    Accepts any alphanumeric emp_code (e.g., U001, FPB001, FPB123456).
    Gate-keeps via the registered_attendees list when one exists for the event.
    When no registration list exists, any code is accepted (backward compatible).
    """
    body = read_json_body(handler)

    emp_code = (body.get("emp_code") or "").strip()
    checkin_method = (body.get("checkin_method") or "manual").strip().lower()
    event_id = (body.get("event_id") or "").strip()
    timestamp = (body.get("timestamp") or datetime.now(timezone.utc).isoformat()).strip()

    # Validation
    errors = []
    if not emp_code:
        errors.append("emp_code is required")
    if checkin_method not in ("qr", "manual"):
        errors.append("checkin_method must be 'qr' or 'manual'")
    if not event_id:
        errors.append("event_id is required")
    if errors:
        return json_response(handler, {"error": "; ".join(errors)}, 400)

    db = get_db()
    try:
        # Verify event
        event = db.execute("SELECT id, name FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": f"Event not found: {event_id}"}, 404)

        # ── Resolve user identity ────────────────────────────
        user_name = emp_code
        user_dept = ""
        user_id = emp_code

        # Check if this event has a registration list
        reg_count = db.execute(
            "SELECT COUNT(*) AS n FROM registered_attendees WHERE event_id = ?",
            (event_id,),
        ).fetchone()["n"]

        if reg_count > 0:
            # ── Registration-gated event: user MUST be in the list ──
            reg = db.execute(
                "SELECT id, emp_code, name, dept, status FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
                (event_id, emp_code),
            ).fetchone()
            if not reg:
                return json_response(handler, {
                    "error": "not_registered",
                    "message": f"Code \"{emp_code}\" is not registered for this event.",
                }, 403)
            user_id = reg["emp_code"]
            user_name = reg["name"] or emp_code
            user_dept = reg["dept"] or ""
        else:
            # ── Open event: try to enrich from users table ──
            user_row = db.execute(
                "SELECT id, name, dept FROM users WHERE id = ? OR pin = ?",
                (emp_code, emp_code),
            ).fetchone()
            if user_row:
                user_id = user_row["id"]
                user_name = user_row["name"]
                user_dept = user_row["dept"] or ""

        # Duplicate check
        existing = db.execute(
            "SELECT id FROM attendance WHERE event_id = ? AND emp_code = ?",
            (event_id, user_id),
        ).fetchone()
        if existing:
            return json_response(handler, {
                "error": "duplicate",
                "message": f"{user_name} is already checked in for this event.",
                "user": {"id": user_id, "name": user_name, "dept": user_dept},
            }, 409)

        # Insert attendance record (main table)
        attendance_id = gen_id("at")
        db.execute(
            """INSERT INTO attendance (id, event_id, emp_code, checkin_method, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (attendance_id, event_id, user_id, checkin_method, timestamp),
        )

        # Insert into attendance_history (permanent audit log)
        history_id = gen_id("ah")
        db.execute(
            """INSERT INTO attendance_history (id, emp_id, name, event_id, checkin_method, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (history_id, user_id, user_name, event_id, checkin_method, timestamp),
        )

        # Update registration status if applicable
        db.execute(
            "UPDATE registered_attendees SET status = 'attended' WHERE event_id = ? AND emp_code = ?",
            (event_id, user_id),
        )
        db.commit()

        record = {
            "id": attendance_id,
            "event_id": event_id,
            "event_name": event["name"],
            "emp_code": user_id,
            "user_name": user_name,
            "user_dept": user_dept,
            "checkin_method": checkin_method,
            "timestamp": timestamp,
        }
        return json_response(handler, record, 201)
    finally:
        db.close()


def handle_active_qr_generate(handler):
    """POST /api/active-qr/generate — replace the active QR list with new IDs."""
    body = read_json_body(handler)
    attendees = body.get("attendees", [])
    if not isinstance(attendees, list):
        return json_response(handler, {"error": "attendees array is required"}, 400)

    db = get_db()
    try:
        db.execute("DELETE FROM active_qr_list")   # clear old list
        for att in attendees:
            emp_id = (att.get("emp_code") or att.get("emp_id") or "").strip()
            if not emp_id:
                continue
            name = (att.get("name") or "").strip()
            db.execute(
                "INSERT INTO active_qr_list (emp_id, name) VALUES (?, ?)",
                (emp_id, name),
            )
        db.commit()

        count = db.execute("SELECT COUNT(*) AS n FROM active_qr_list").fetchone()["n"]
        return json_response(handler, {"status": "ok", "count": count}, 201)
    finally:
        db.close()


def handle_active_qr_clear(handler):
    """DELETE /api/active-qr/clear — empty the active QR list."""
    db = get_db()
    try:
        db.execute("DELETE FROM active_qr_list")
        db.commit()
        return json_response(handler, {"status": "cleared"})
    finally:
        db.close()


def handle_active_qr_list(handler):
    """GET /api/active-qr/list — return current active QR list."""
    db = get_db()
    try:
        rows = db.execute(
            "SELECT emp_id, name FROM active_qr_list ORDER BY name"
        ).fetchall()
        return json_response(handler, [dict(r) for r in rows])
    finally:
        db.close()


def handle_email_report(handler, event_id):
    """POST /api/events/<id>/report/email — generate CSV and email it.

    Body:  {"email": "recipient@example.com"}
    Reads SMTP_EMAIL and SMTP_PASSWORD from env / .env file.
    Uses Gmail SMTP (smtp.gmail.com:587) with STARTTLS.
    """
    body = read_json_body(handler)
    to_email = (body.get("email") or "").strip()
    if not to_email:
        return json_response(handler, {"error": "email address is required"}, 400)

    db = get_db()
    try:
        event = db.execute("SELECT id, name, date FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)

        # ── Build the report CSV ─────────────────────────────
        reg_count = db.execute(
            "SELECT COUNT(*) AS n FROM registered_attendees WHERE event_id = ?",
            (event_id,),
        ).fetchone()["n"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Employee ID", "Name", "Department", "Status"])

        if reg_count > 0:
            # Gated event: every registered person appears with Attended/Absent
            rows = db.execute(
                """SELECT emp_code, name, dept,
                          CASE WHEN status = 'attended' THEN 'Attended' ELSE 'Absent' END AS final_status
                   FROM registered_attendees
                   WHERE event_id = ?
                   ORDER BY name""",
                (event_id,),
            ).fetchall()
            for r in rows:
                writer.writerow([r["emp_code"], r["name"], r["dept"], r["final_status"]])
        else:
            # Open event: list everyone who checked in
            rows = db.execute(
                """SELECT a.emp_code, a.emp_code AS name, '' AS dept
                   FROM attendance a
                   WHERE a.event_id = ?
                   ORDER BY a.timestamp DESC""",
                (event_id,),
            ).fetchall()
            for r in rows:
                writer.writerow([r["emp_code"], r["name"], r["dept"], "Attended"])

            if len(rows) == 0:
                writer.writerow(["(no check-ins)", "", "", ""])

        csv_content = output.getvalue()
        output.close()

        # ── Send via Gmail SMTP ──────────────────────────────
        smtp_user = os.environ.get("SMTP_EMAIL", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")

        if not smtp_user or not smtp_pass:
            return json_response(handler, {
                "error": "SMTP not configured",
                "message": "Set SMTP_EMAIL and SMTP_PASSWORD in .env file.",
            }, 500)

        msg = EmailMessage()
        msg["Subject"] = f"Attendance Report: {event['name']} — {event['date']}"
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg.set_content(
            f"Attached is the attendance report for:\n\n"
            f"  {event['name']}\n"
            f"  Date: {event['date']}\n\n"
            f"Generated by Training Attendance Manager.\n"
        )
        msg.add_attachment(
            csv_content.encode("utf-8"),
            maintype="text",
            subtype="csv",
            filename=f"attendance_{event['name'].replace(' ', '_')}_{event['date']}.csv",
        )

        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError:
            return json_response(handler, {
                "error": "SMTP authentication failed",
                "message": "Check SMTP_EMAIL and SMTP_PASSWORD. For Gmail, use an App Password.",
            }, 500)
        except smtplib.SMTPException as e:
            return json_response(handler, {
                "error": "SMTP send failed",
                "message": str(e),
            }, 500)

        return json_response(handler, {
            "status": "sent",
            "to": to_email,
            "event": event["name"],
            "records": len(rows) if reg_count > 0 else (len(rows) if len(rows) > 0 and rows[0]["emp_code"] != "(no check-ins)" else 0),
        })
    finally:
        db.close()


def handle_event_status(handler, event_id):
    """POST /api/events/<id>/status — update event status (upcoming / live / closed)."""
    body = read_json_body(handler)
    new_status = (body.get("status") or "").strip().lower()
    if new_status not in ("upcoming", "live", "closed"):
        return json_response(handler, {"error": "status must be 'upcoming', 'live', or 'closed'"}, 400)

    db = get_db()
    try:
        event = db.execute("SELECT id, name FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)
        db.execute("UPDATE events SET status = ? WHERE id = ?", (new_status, event_id))
        db.commit()
        return json_response(handler, {"event_id": event_id, "event_name": event["name"], "status": new_status})
    finally:
        db.close()


def handle_self_checkin_page(handler, query):
    """GET /self-checkin?event_id=<id> — serve the employee self-check-in portal page.

    Returns a complete styled HTML page with the event name, status badge, and a
    form that POSTs to /api/checkin/self.
    """
    event_id = (query.get("event_id", [None])[0] or "").strip()

    event_name = "Unknown Event"
    event_status = "upcoming"
    event_date = ""

    if event_id:
        db = get_db()
        try:
            event = db.execute(
                "SELECT name, status, date FROM events WHERE id = ?", (event_id,)
            ).fetchone()
            if event:
                event_name = event["name"]
                event_status = event["status"].lower() if event["status"] else "upcoming"
                event_date = event["date"] or ""
        finally:
            db.close()

    # Status-specific UI state
    status_config = {
        "upcoming": {
            "badge_class": "bg-amber-100 text-amber-800 border-amber-300",
            "badge_text": "⏳ Upcoming — Not Started",
            "warning": "Event has not started yet. Please wait until the admin starts the session.",
            "disabled": "disabled",
            "btn_text": "Check-in Unavailable",
        },
        "live": {
            "badge_class": "bg-emerald-100 text-emerald-800 border-emerald-300",
            "badge_text": "🟢 Live — Check-in Open",
            "warning": "",
            "disabled": "",
            "btn_text": "✅ Check In",
        },
        "closed": {
            "badge_class": "bg-red-100 text-red-800 border-red-300",
            "badge_text": "🔒 Closed — Ended",
            "warning": "This event has ended. Check-in is closed.",
            "disabled": "disabled",
            "btn_text": "Check-in Unavailable",
        },
    }
    cfg = status_config.get(event_status, status_config["upcoming"])

    warning_html = ""
    if cfg["warning"]:
        warning_html = (
            f'<div class="msg msg-warning show">{cfg["warning"]}</div>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <meta name="theme-color" content="#4f46e5" />
  <title>Self Check-in — Training Attendance</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f8fafc; display: flex; align-items: center; justify-content: center;
      min-height: 100vh; padding: 20px;
    }}
    .card {{
      max-width: 440px; width: 100%; background: #fff;
      border-radius: 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.06);
      padding: 40px 32px; text-align: center;
    }}
    .logo {{ font-size: 40px; margin-bottom: 8px; }}
    h1 {{ font-size: 20px; color: #1e293b; margin-bottom: 4px; }}
    .subtitle {{ font-size: 13px; color: #64748b; margin-bottom: 24px; }}
    .event-name {{ font-size: 16px; font-weight: 700; color: #4f46e5; margin-bottom: 6px; }}
    .event-date {{ font-size: 12px; color: #94a3b8; margin-bottom: 16px; }}
    .status-badge {{
      display: inline-block; padding: 4px 14px; border-radius: 9999px;
      font-size: 12px; font-weight: 700; margin-bottom: 24px;
    }}
    .form-group {{ margin-bottom: 16px; text-align: left; }}
    .form-group label {{
      display: block; font-size: 12px; font-weight: 600;
      color: #64748b; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;
    }}
    .form-group input {{
      width: 100%; border: 1px solid #d1d5db; border-radius: 12px;
      padding: 12px 16px; font-size: 15px; font-family: 'Courier New', monospace;
      outline: none; transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .form-group input:focus {{
      border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
    }}
    .btn {{
      width: 100%; padding: 14px; border: none; border-radius: 12px;
      font-size: 15px; font-weight: 700; cursor: pointer;
      transition: all 0.15s; color: #fff; margin-top: 4px;
    }}
    .btn-primary {{ background: #4f46e5; box-shadow: 0 2px 8px rgba(79,70,229,0.3); }}
    .btn-primary:hover {{ background: #4338ca; }}
    .btn-primary:active {{ transform: scale(0.98); }}
    .btn-primary:disabled {{ background: #d1d5db; cursor: not-allowed; box-shadow: none; }}
    .msg {{
      margin-top: 16px; padding: 12px 16px; border-radius: 12px;
      font-size: 14px; font-weight: 600; display: none; text-align: center;
    }}
    .msg.show {{ display: block; }}
    .msg-success {{ background: #ecfdf5; color: #065f46; border: 1px solid #6ee7b7; }}
    .msg-error {{ background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }}
    .msg-warning {{ background: #fffbeb; color: #92400e; border: 1px solid #fcd34d; }}
    .msg-loading {{ background: #eff6ff; color: #1e40af; border: 1px solid #93c5fd; }}
    .spinner {{
      display: inline-block; width: 16px; height: 16px;
      border: 2px solid #e2e8f0; border-top-color: #4f46e5;
      border-radius: 50%; animation: spin 0.6s linear infinite; margin-right: 8px; vertical-align: middle;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .footer {{ margin-top: 20px; font-size: 11px; color: #94a3b8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">📋</div>
    <h1>Self Check-in</h1>
    <p class="subtitle">Training Attendance Manager</p>

    <div id="event-info">
      <p class="event-name">{event_name}</p>
      <p class="event-date">{event_date}</p>
      <span class="status-badge {cfg['badge_class']}">{cfg['badge_text']}</span>
    </div>

    <div id="checkin-form">
      <div class="form-group">
        <label for="emp-code">Employee ID</label>
        <input type="text" id="emp-code" placeholder="Enter your Employee ID" autocomplete="off" autocapitalize="off" {cfg['disabled']} />
      </div>
      <button class="btn btn-primary" id="btn-checkin" {cfg['disabled']}>{cfg['btn_text']}</button>
    </div>

    <div class="msg" id="message"></div>
    {warning_html}
    <div class="footer">Training Attendance Manager</div>
  </div>

  <script>
    (function() {{
      var eventId = '{event_id}';
      var btn = document.getElementById('btn-checkin');
      var input = document.getElementById('emp-code');
      var msgEl = document.getElementById('message');

      function showMsg(text, type) {{
        msgEl.textContent = text;
        msgEl.className = 'msg show msg-' + type;
      }}

      btn.addEventListener('click', function() {{
        var code = input.value.trim();
        if (!code) {{
          showMsg('Please enter your Employee ID.', 'error');
          return;
        }}
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Checking in…';
        msgEl.className = 'msg';

        fetch('/api/checkin/self', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ emp_code: code, event_id: eventId }})
        }})
        .then(function(r) {{ return r.json(); }})
        .then(function(resp) {{
          if (resp.status === 'ok') {{
            showMsg(resp.message || 'Check-in successful!', 'success');
            input.value = '';
            btn.disabled = true;
            btn.textContent = '✅ Done!';
          }} else if (resp.error === 'already_checked_in') {{
            showMsg(resp.message || 'Already checked in.', 'warning');
            btn.disabled = false;
            btn.textContent = '✅ Check In';
          }} else {{
            showMsg(resp.error || resp.message || 'Check-in failed.', 'error');
            btn.disabled = false;
            btn.textContent = '✅ Check In';
          }}
        }})
        .catch(function() {{
          showMsg('Network error. Please try again.', 'error');
          btn.disabled = false;
          btn.textContent = '✅ Check In';
        }});
      }});

      input.addEventListener('keydown', function(e) {{
        if (e.key === 'Enter') {{ e.preventDefault(); btn.click(); }}
      }});

      setTimeout(function() {{ input.focus(); }}, 500);
    }})();
  </script>
</body>
</html>"""
    body_bytes = html.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body_bytes)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body_bytes)


def handle_self_checkin_info(handler, event_id):
    """GET /api/events/<id>/self-checkin-info — lightweight event info for self-checkin page."""
    db = get_db()
    try:
        event = db.execute("SELECT id, name, status, date FROM events WHERE id = ?",
                           (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "event not found"}, 404)

        reg_count = db.execute(
            "SELECT COUNT(*) AS n FROM registered_attendees WHERE event_id = ?",
            (event_id,),
        ).fetchone()["n"]

        return json_response(handler, {
            "event_id": event["id"],
            "event_name": event["name"],
            "event_status": event["status"],
            "event_date": event["date"],
            "registered_count": reg_count,
        })
    finally:
        db.close()


def handle_self_checkin(handler):
    """POST /api/checkin/self — employee self-check-in via master link.

    Body: { emp_code, event_id }
    Validates registration, gatekeeps on event status, marks attendance.
    """
    body = read_json_body(handler)
    emp_code = (body.get("emp_code") or "").strip()
    event_id = (body.get("event_id") or "").strip()

    if not emp_code:
        return json_response(handler, {"error": "Employee ID is required."}, 400)
    if not event_id:
        return json_response(handler, {"error": "Event ID is required."}, 400)

    db = get_db()
    try:
        event = db.execute("SELECT id, name, status FROM events WHERE id = ?",
                           (event_id,)).fetchone()
        if not event:
            return json_response(handler, {"error": "Event not found."}, 404)

        status = event["status"].lower()

        # ── State gatekeeping ──────────────────────────────────
        if status == "upcoming":
            return json_response(handler, {"error": "Event has not started yet."}, 403)
        if status == "closed":
            return json_response(handler, {"error": "Event has ended. Check-in is closed."}, 403)

        # ── Validate registration ─────────────────────────────
        reg = db.execute(
            "SELECT id, emp_code, name, dept FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        ).fetchone()

        if not reg:
            return json_response(handler, {
                "error": "Employee ID not registered for this event.",
            }, 404)

        user_name = reg["name"] or emp_code

        # ── Duplicate check ────────────────────────────────────
        existing = db.execute(
            "SELECT id FROM attendance WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        ).fetchone()
        if existing:
            return json_response(handler, {
                "error": "already_checked_in",
                "message": f"{user_name} is already checked in for this event.",
            }, 409)

        # ── Mark as attended ───────────────────────────────────
        attendance_id = gen_id("at")
        db.execute(
            """INSERT INTO attendance (id, event_id, emp_code, checkin_method, timestamp)
               VALUES (?, ?, ?, 'self', datetime('now'))""",
            (attendance_id, event_id, emp_code),
        )

        history_id = gen_id("ah")
        db.execute(
            """INSERT INTO attendance_history (id, emp_id, name, event_id, checkin_method, timestamp)
               VALUES (?, ?, ?, ?, 'self', datetime('now'))""",
            (history_id, emp_code, user_name, event_id),
        )

        db.execute(
            "UPDATE registered_attendees SET status = 'attended' WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        )
        db.commit()

        return json_response(handler, {
            "status": "ok",
            "message": f"Check-in successful for {user_name}!",
            "user_name": user_name,
            "event_name": event["name"],
        })
    finally:
        db.close()


def handle_remote_checkin(handler, query):
    """GET /api/checkin/remote?emp_code=X&event_id=Y — self check-in link.

    Returns a styled HTML page depending on event status:
      - upcoming: "Event has not started yet."
      - closed:   "This event has ended. Check-in is closed."
      - live:     Marks user as attended; shows success page with their name.
    """
    emp_code = (query.get("emp_code", [None])[0] or "").strip()
    event_id = (query.get("event_id", [None])[0] or "").strip()

    if not emp_code or not event_id:
        return html_page(handler, "Missing Parameters",
                         "Both emp_code and event_id are required.", "error")

    db = get_db()
    try:
        event = db.execute("SELECT id, name, status, date FROM events WHERE id = ?",
                           (event_id,)).fetchone()
        if not event:
            return html_page(handler, "Event Not Found",
                             f"No event found with ID: {event_id}", "error")

        # ── Resolve the user from registered_attendees ──────────
        reg = db.execute(
            "SELECT id, emp_code, name, dept FROM registered_attendees WHERE event_id = ? AND emp_code = ?",
            (event_id, emp_code),
        ).fetchone()

        if not reg:
            return html_page(handler, "Not Registered",
                             f"Code \"{emp_code}\" is not registered for this event.", "error")

        user_name = reg["name"] or emp_code

        # ── State gatekeeping ──────────────────────────────────
        status = event["status"].lower()

        if status == "upcoming":
            return html_page(handler, "Event Has Not Started",
                             f"<strong>{event['name']}</strong> has not started yet. "
                             f"Please wait until the admin starts the session.",
                             "upcoming")

        if status == "closed":
            return html_page(handler, "Event Has Ended",
                             f"<strong>{event['name']}</strong> has ended. Check-in is closed.",
                             "closed")

        if status == "live":
            # ── Mark as attended ─────────────────────────────────
            # Check for duplicate
            existing = db.execute(
                "SELECT id FROM attendance WHERE event_id = ? AND emp_code = ?",
                (event_id, emp_code),
            ).fetchone()

            if existing:
                return html_page(handler, "Already Checked In",
                                 f"You are already checked in for <strong>{event['name']}</strong>!",
                                 "success")

            # Insert attendance
            attendance_id = gen_id("at")
            db.execute(
                """INSERT INTO attendance (id, event_id, emp_code, checkin_method, timestamp)
                   VALUES (?, ?, ?, 'remote', datetime('now'))""",
                (attendance_id, event_id, emp_code),
            )

            # Insert attendance history
            history_id = gen_id("ah")
            db.execute(
                """INSERT INTO attendance_history (id, emp_id, name, event_id, checkin_method, timestamp)
                   VALUES (?, ?, ?, ?, 'remote', datetime('now'))""",
                (history_id, emp_code, user_name, event_id),
            )

            # Update registration status
            db.execute(
                "UPDATE registered_attendees SET status = 'attended' WHERE event_id = ? AND emp_code = ?",
                (event_id, emp_code),
            )
            db.commit()

            return html_page(handler, "Check-in Successful!",
                             f"Check-in Successful for <strong>{user_name}</strong>! "
                             f"Welcome to {event['name']}.",
                             "success")

        # Shouldn't reach here
        return html_page(handler, "Unknown Status",
                         f"Event status '{status}' is not recognized.", "error")

    finally:
        db.close()


def html_page(handler, title, message, page_type):
    """Render a styled HTML page for remote check-in responses."""
    colors = {
        "upcoming": {"bg": "#fff7ed", "border": "#fdba74", "text": "#9a3412", "icon": "⏳"},
        "closed":   {"bg": "#fef2f2", "border": "#fca5a5", "text": "#991b1b", "icon": "🔒"},
        "success":  {"bg": "#f0fdf4", "border": "#86efac", "text": "#166534", "icon": "✅"},
        "error":    {"bg": "#fef2f2", "border": "#fca5a5", "text": "#991b1b", "icon": "❌"},
    }
    style = colors.get(page_type, colors["error"])
    css = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      display: flex; align-items: center; justify-content: center;
      min-height: 100vh; background: #f8fafc;
    }
    .card {
      max-width: 420px; margin: 20px; padding: 40px 32px;
      border-radius: 20px; text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    .icon { font-size: 48px; margin-bottom: 16px; }
    h1 { font-size: 22px; margin-bottom: 12px; }
    p { font-size: 15px; line-height: 1.6; opacity: 0.85; }
    .footer { margin-top: 24px; font-size: 11px; opacity: 0.5; }
    """
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="card" style="background:{style['bg']}; border:2px solid {style['border']}; color:{style['text']};">
    <div class="icon">{style['icon']}</div>
    <h1>{title}</h1>
    <p>{message}</p>
    <div class="footer">Training Attendance Manager</div>
  </div>
</body>
</html>"""
    body_bytes = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body_bytes)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body_bytes)


def handle_analytics(handler):
    db = get_db()
    try:
        total_events = db.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
        total_checkins = db.execute("SELECT COUNT(*) AS n FROM attendance").fetchone()["n"]
        unique_attendees = db.execute(
            "SELECT COUNT(DISTINCT emp_code) AS n FROM attendance"
        ).fetchone()["n"]

        event_stats = db.execute("""
            SELECT e.id, e.name, e.date, COUNT(a.id) AS checkins
            FROM events e
            LEFT JOIN attendance a ON a.event_id = e.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
            LIMIT 10
        """).fetchall()

        return json_response(handler, {
            "total_events": total_events,
            "total_checkins": total_checkins,
            "unique_attendees": unique_attendees,
            "event_breakdown": [dict(r) for r in event_stats],
        })
    finally:
        db.close()


def serve_static(handler, path):
    """Serve static files (index.html, self-checkin.html)."""
    if path in ("/", "/index.html"):
        file_path = os.path.join(BASE_DIR, "index.html")
    elif path in ("/self-checkin", "/self-checkin.html"):
        file_path = os.path.join(BASE_DIR, "self-checkin.html")
    elif path.startswith("/self-checkin"):
        file_path = os.path.join(BASE_DIR, "self-checkin.html")
    else:
        json_response(handler, {"error": "not found"}, 404)
        return

    if os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.send_header("Content-Length", str(len(content)))
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(content)
    else:
        json_response(handler, {"error": "not found"}, 404)


# ── URL Router ─────────────────────────────────────────────────
ROUTES = [
    # (method, pattern, handler)
    # Pattern groups: /api/events/<id> captures the ID
]

API_PATTERNS = [
    (r"^/api/health$"),
    (r"^/api/users$"),
    (r"^/api/events$"),
    (r"^/api/events/([a-zA-Z0-9_]+)$"),
    (r"^/api/checkin$"),
    (r"^/api/analytics$"),
]


def route_request(handler, method, path, query):
    """Simple regex-based router for API endpoints."""

    # /api/health
    if method == "GET" and re.match(r"^/api/health$", path):
        return handle_health(handler)

    # /api/users
    if method == "GET" and re.match(r"^/api/users$", path):
        return handle_list_users(handler)

    # /api/events (collection)
    if re.match(r"^/api/events$", path):
        if method == "GET":
            return handle_list_events(handler)
        if method == "POST":
            return handle_create_event(handler)

    # /api/events/<id>/report/email  (POST email report)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/report/email$", path)
    if m:
        event_id = m.group(1)
        if method == "POST":
            return handle_email_report(handler, event_id)

    # /api/events/<id>/registered/<emp_code>  (DELETE one registration)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/registered/([a-zA-Z0-9_-]+)$", path)
    if m:
        event_id, emp_code = m.group(1), m.group(2)
        if method == "DELETE":
            return handle_delete_registered(handler, event_id, emp_code)

    # /api/events/<id>/status  (POST update event status)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/status$", path)
    if m:
        event_id = m.group(1)
        if method == "POST":
            return handle_event_status(handler, event_id)

    # /api/events/<id>/self-checkin-info  (GET event info for self-checkin page)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/self-checkin-info$", path)
    if m:
        event_id = m.group(1)
        if method == "GET":
            return handle_self_checkin_info(handler, event_id)

    # /api/events/<id>/register  (POST bulk register)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/register$", path)
    if m:
        event_id = m.group(1)
        if method == "POST":
            return handle_register_attendees(handler, event_id)

    # /api/events/<id>/registered  (GET list registered)
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)/registered$", path)
    if m:
        event_id = m.group(1)
        if method == "GET":
            return handle_get_registered(handler, event_id)

    # /api/events/<id>
    m = re.match(r"^/api/events/([a-zA-Z0-9_-]+)$", path)
    if m:
        event_id = m.group(1)
        if method == "GET":
            return handle_get_event(handler, event_id)
        if method == "DELETE":
            return handle_delete_event(handler, event_id)

    # /api/active-qr/generate  (POST replace active QR list)
    if method == "POST" and re.match(r"^/api/active-qr/generate$", path):
        return handle_active_qr_generate(handler)

    # /api/active-qr/clear  (DELETE empty active QR list)
    if method == "DELETE" and re.match(r"^/api/active-qr/clear$", path):
        return handle_active_qr_clear(handler)

    # /api/active-qr/list  (GET active QR list)
    if method == "GET" and re.match(r"^/api/active-qr/list$", path):
        return handle_active_qr_list(handler)

    # /api/checkin/self  (employee self check-in from master link)
    if method == "POST" and re.match(r"^/api/checkin/self$", path):
        return handle_self_checkin(handler)

    # /api/checkin/remote  (self check-in link — legacy, kept for existing distributed links)
    if method == "GET" and re.match(r"^/api/checkin/remote$", path):
        return handle_remote_checkin(handler, query)

    # /api/checkin
    if re.match(r"^/api/checkin$", path):
        if method == "GET":
            return handle_checkin_list(handler, query)
        if method == "POST":
            return handle_checkin(handler)

    # /api/analytics
    if method == "GET" and re.match(r"^/api/analytics$", path):
        return handle_analytics(handler)

    # /self-checkin — employee self-check-in portal (dedicated route)
    if method == "GET" and re.match(r"^/self-checkin", path):
        return handle_self_checkin_page(handler, query)

    # Static files (index.html for PWA)
    if method == "GET":
        return serve_static(handler, path)

    # Fallback
    return json_response(handler, {"error": "not found"}, 404)


# ── HTTP Request Handler ───────────────────────────────────────
class RequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        route_request(self, "GET", parsed.path, query)

    def do_POST(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        route_request(self, "POST", parsed.path, query)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        route_request(self, "DELETE", parsed.path, query)

    def log_message(self, format, *args):
        """Nicer log output."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


# ── Main ───────────────────────────────────────────────────────
def main():
    init_db()
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"📋 Database: {DATABASE}")
    print(f"🚀 Attendance Manager API running at http://{HOST}:{PORT}")
    print(f"   PWA frontend:  http://localhost:{PORT}")
    print(f"   API health:    http://localhost:{PORT}/api/health")
    print(f"   Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
