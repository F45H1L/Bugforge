# Ottergram — ottergram-003 — File inclusion

## Overview

- **Challenge Name:** Ottergram
- **Platform:** BugForge
- **Category:** Web Application Security
- **Hint:** File Inclusion
- **Vulnerability:** Path Traversal / Arbitrary File Disclosure
- **Status:** Solved

## Objective

Identify and exploit a file inclusion vulnerability in the Ottergram web application to access a file outside the intended image directory and retrieve the challenge flag.

## Tools Used

- Web browser
- Burp Suite or browser Developer Tools
- HTTP request and response inspection

## Instructions to Reproduce

### Step 1: Register and Explore the Application

1. Open the assigned Ottergram challenge URL.
2. Register an account using test credentials.
3. Log in to the application.
4. Open a user profile and view one of its posts.
5. Inspect the image requests using the browser's Developer Tools or Burp Suite HTTP history.

### Step 2: Identify the Image Endpoint

During inspection, the following request was observed:

```http
GET /api/post/image?file=/uploads/otter4.png
```

The server returned:

- **HTTP Status:** `200 OK`
- **Content-Type:** `image/png`
- **Server Framework:** Express.js

This indicated that the application used the `file` parameter to retrieve image content.

### Step 3: Test the File Parameter

The `file` parameter was identified as a potential attack surface because its value appeared to determine which file the server returned.

The original request referenced an image:

```http
GET /api/post/image?file=/uploads/otter4.png
```

To test whether the application improperly handled file paths, the request was modified to include a parent-directory traversal sequence.

### Step 4: Exploit the Path Traversal Vulnerability

Send the following request to the challenge application:

```http
GET /api/post/image?file=../flag.txt
```

The server returned:

```http
HTTP/2 200
Content-Type: text/plain; charset=utf-8
Content-Length: 37
```

The response body contained the challenge flag.

**Captured flag:**

```text
bug{3bvOoV28pvIw1Vn7WJSZBYF9NLgELfqr}
```

### Step 5: Verify the Finding

The vulnerability was confirmed by the following observations:

1. The original image request returned image content.
2. Changing the `file` parameter to `../flag.txt` resulted in a successful response.
3. The response content type changed from `image/png` to `text/plain; charset=utf-8`.
4. The response body disclosed the contents of `flag.txt`, including the challenge flag.

These observations demonstrate that the application allowed access to a file outside its intended image directory.

## Technical Explanation

The endpoint accepts a user-controlled `file` parameter to determine which file to serve. The application appears to lack sufficient validation or containment checks on the requested path.

The payload:

```text
../flag.txt
```

uses `..` to navigate to the parent directory. If the application resolves this path without enforcing an appropriate directory boundary, a user may be able to access files outside the intended upload directory.

The vulnerable behavior can be represented conceptually as:

```javascript
const file = req.query.file;
// Unsafe if used without appropriate path validation.
```

This is an illustrative example, not the confirmed source code of Ottergram.

## Root Cause

The likely root cause is insufficient validation of user-controlled filesystem paths. The application does not adequately restrict the requested file to the intended directory and permitted file types.

## Security Impact

An attacker may be able to:

- Read files outside the intended uploads directory.
- Access sensitive application files if they are readable by the application process.
- Retrieve configuration files or other confidential data, depending on the deployment.
- Expose secrets that could enable further attacks.

The demonstrated impact in this challenge was unauthorized disclosure of the flag file.

## Recommended Mitigations

1. **Restrict file access to an approved directory.** Resolve requested paths against a dedicated uploads directory.
2. **Validate the resolved path.** Ensure the canonical path remains within the approved directory before serving the file.
3. **Use file identifiers instead of raw paths.** Map an opaque identifier to a server-controlled filename.
4. **Allow only expected file types.** Validate image formats and do not rely solely on file extensions.
5. **Apply least privilege.** Ensure the application process cannot read unnecessary sensitive files.
6. **Handle errors safely.** Avoid exposing filesystem paths, stack traces, or internal implementation details.

## Conclusion

The Ottergram challenge was solved by identifying an image-serving endpoint, inspecting its `file` parameter, and demonstrating that a parent-directory traversal payload could retrieve `flag.txt`.

The successful response confirmed a path traversal vulnerability resulting in arbitrary file disclosure.

**Result:** Challenge completed and flag captured.