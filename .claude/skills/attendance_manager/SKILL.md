---
name: attendance_manager
description: >
  Skill for analyzing the Training & Event Attendance Manager database.
  Understands the schema, business rules, and provides query patterns
  for reporting on training attendance, employee participation, and
  event metrics. Use this skill whenever asked to explore, query, or
  interpret the attendance data.
---

# Attendance Manager — Database Schema & Analysis Rules

## Overview

This is a training and event attendance tracking system. A PWA frontend
(index.html) handles QR scanning and manual check-in, while a Flask backend
(app.py) persists records to a local SQLite database (`attendance.db`).

The MCP server `mcp-server-sqlite` is configured in `.mcp.json` to connect
directly to `attendance.db` for read-only queries.

## Database Schema

### Table: `events`

Stores training events / sessions that employees can attend.

| Column      | Type    | Notes                                              |
|-------------|---------|----------------------------------------------------|
| id          | TEXT PK | e.g. `ev_a1b2c3d4e5f6`                             |
| name        | TEXT    | Event title, required                              |
| date        | TEXT    | ISO date `YYYY-MM-DD`, required                    |
| time        | TEXT    | `HH:MM` format, optional                           |
| location    | TEXT    | Room or venue name, optional                       |
| description | TEXT    | Free text, optional                                |
| created_at  | TEXT    | ISO datetime, auto-set on creation                 |

### Table: `users`

Pre-seeded demo employees who can check into events.

| Column | Type    | Notes                              |
|--------|---------|------------------------------------|
| id     | TEXT PK | Employee code, e.g. `U001`         |
| pin    | TEXT    | Numeric PIN for manual entry       |
| name   | TEXT    | Full name                          |
| dept   | TEXT    | Department (Engineering, HR, etc.) |
| active | INTEGER | 1 = active, 0 = inactive           |

### Table: `attendance`

Records individual check-in actions. One row per employee per event.

| Column         | Type    | Notes                                          |
|----------------|---------|------------------------------------------------|
| id             | TEXT PK | e.g. `at_x1y2z3w4v5u6`                         |
| event_id       | TEXT FK | References `events(id)` — CASCADE on delete    |
| emp_code       | TEXT    | References `users(id)`                         |
| checkin_method | TEXT    | `'qr'` or `'manual'`                           |
| timestamp      | TEXT    | ISO datetime of check-in                       |

### Table: `registered_attendees`

Pre-registration list for events. When populated, only registered users can check
in to that event. Events with an empty registration list accept anyone.

| Column   | Type    | Notes                                              |
|----------|---------|----------------------------------------------------|
| id       | TEXT PK | e.g. `reg_a1b2c3d4e5f6`                            |
| event_id | TEXT FK | References `events(id)` — CASCADE on delete        |
| emp_code | TEXT    | Canonical user ID (resolved from ID or PIN at upload time) |
| name     | TEXT    | Full name (enriched from `users` table if known)   |
| dept     | TEXT    | Department (enriched from `users` table if known)  |
| status   | TEXT    | `'registered'` or `'attended'`                     |

The `emp_code` is always resolved to the canonical user ID during bulk upload.
If a PIN is uploaded (e.g., `1003`), it is looked up and stored as `U003`.

### Key Indexes

- `idx_attendance_event` on `attendance(event_id)` — fast per-event queries
- `idx_attendance_emp_code` on `attendance(emp_code)` — fast per-user lookups
- `idx_attendance_timestamp` on `attendance(timestamp)` — time-range scans
- `idx_reg_event` on `registered_attendees(event_id)` — fast registration lookups
- `idx_reg_emp` on `registered_attendees(emp_code)` — fast per-user reg checks

## Business Rules

1. **Duplicate prevention**: An employee can check into a given event only
   once. The API returns HTTP 409 if a duplicate is attempted.

2. **User lookup**: Check-in accepts either an employee ID (`U001`) or their
   PIN (`1001`). The QR scanner encodes the ID; manual entry accepts either.

3. **Event lifecycle**: Deleting an event cascades to remove all its
   attendance records (foreign key with `ON DELETE CASCADE`).

4. **Registration gating**: If an event has any rows in `registered_attendees`,
   only those registered users can check in. The API returns HTTP 403 with
   `"error": "not_registered"` for unregistered users. Events with an empty
   registration list accept anyone (backward compatible).

5. **Automatic status flip**: When a registered user checks in, their
   `registered_attendees.status` is updated from `'registered'` to `'attended'`.

6. **PIN-to-ID resolution**: During bulk upload, codes like `1003` are
   resolved through the `users` table and stored as canonical IDs (`U003`).
   Unknown codes are stored as-is with the provided name/dept.

7. **No check-in without an event**: The `event_id` FK constraint ensures
   attendance records always reference a valid event. The API also validates
   the user exists before inserting.

## Common Query Patterns

### Attendance count per event
```sql
SELECT e.name, e.date, COUNT(a.id) AS checkins
FROM events e
LEFT JOIN attendance a ON a.event_id = e.id
GROUP BY e.id
ORDER BY e.date DESC;
```

### Unique employees who attended any event
```sql
SELECT COUNT(DISTINCT emp_code) AS unique_attendees
FROM attendance;
```

### Employees who haven't attended a specific event
```sql
SELECT u.id, u.name, u.dept
FROM users u
WHERE u.active = 1
  AND u.id NOT IN (
    SELECT emp_code FROM attendance WHERE event_id = ?
  );
```

### Check-in method breakdown per event
```sql
SELECT e.name,
       SUM(CASE WHEN a.checkin_method = 'qr' THEN 1 ELSE 0 END) AS qr_count,
       SUM(CASE WHEN a.checkin_method = 'manual' THEN 1 ELSE 0 END) AS manual_count
FROM events e
LEFT JOIN attendance a ON a.event_id = e.id
GROUP BY e.id;
```

### Department participation ranking
```sql
SELECT u.dept, COUNT(DISTINCT a.emp_code) AS attendees
FROM attendance a
JOIN users u ON u.id = a.emp_code
GROUP BY u.dept
ORDER BY attendees DESC;
```

### Time-of-day attendance heatmap
```sql
SELECT SUBSTR(a.timestamp, 12, 2) AS hour, COUNT(*) AS checkins
FROM attendance a
GROUP BY hour
ORDER BY hour;
```

### Registration coverage per event
```sql
SELECT e.name, e.date,
       COUNT(r.id) AS registered,
       SUM(CASE WHEN r.status = 'attended' THEN 1 ELSE 0 END) AS attended,
       ROUND(100.0 * SUM(CASE WHEN r.status = 'attended' THEN 1 ELSE 0 END) / COUNT(r.id), 1) AS rate_pct
FROM events e
LEFT JOIN registered_attendees r ON r.event_id = e.id
GROUP BY e.id
HAVING registered > 0
ORDER BY e.date DESC;
```

### No-shows (registered but didn't attend)
```sql
SELECT r.name, r.emp_code, r.dept, e.name AS event_name, e.date
FROM registered_attendees r
JOIN events e ON e.id = r.event_id
WHERE r.status = 'registered'
ORDER BY e.date, r.name;
```

### Events with registration gating enabled
```sql
SELECT e.id, e.name, COUNT(r.id) AS registered_count
FROM events e
JOIN registered_attendees r ON r.event_id = e.id
GROUP BY e.id
HAVING registered_count > 0;
```

## Analysis Guidelines

When interpreting attendance data:

- **Attendance rate** = (unique attendees / total active users) — scores
  above 80% are considered good for mandatory training.

- **No-show analysis**: Compare `users` against `attendance` per event to
  identify departments or individuals with low participation.

- **Method preference**: Track the ratio of QR vs manual check-ins. A high
  manual ratio may indicate QR scanning issues (lighting, camera access).

- **Time patterns**: Group check-in timestamps by hour to find peak check-in
  windows and optimize staffing for in-person events.

- **Trend detection**: Compare event attendance counts over time. A
  declining trend across consecutive events may signal engagement issues.

Always run queries through the `mcp-server-sqlite` MCP server. Consult the
schema above for correct table and column names.
