### Sokudo - Broken Authentication. Tokens are fun!

## 1. Register/login normally

Open:

Sokudo lab

Create a normal account and log in.

Then open DevTools → Application/Storage → Local Storage.

Look for something like:

token = 20260905020538

The important observation is that the token looks like:

YYYYMMDDHHMMSS

It's essentially the login timestamp rather than a cryptographically random session token.

## 2. Find the admin's last login

Go to the Stats / Leaderboard section.

In Burp Suite, inspect the request made when loading the leaderboard. The interesting endpoint should be:

GET /api/stats/leaderboard

The response should contain users and their last_login, approximately:
```json
[
  {
    "username": "admin",
    "last_login": "2026-09-05T08:xx:xx.xxxZ"
  }
]
```

The challenge leaks the admin's login timestamp through this endpoint.

## 3. Convert the admin timestamp into the token

If you see:

2026-09-05T08:42:17.123Z

the token format is:

20260905084217

So:

2026 09 05 08 42 17
│    │  │  │  │  │
Y    M  D  H  M  S
## 4. Verify the forged token

Send a request to:

GET /api/verify-token
Authorization: Bearer 20260905084217

If the token is correct, the response should identify you as the admin. This endpoint is specifically mentioned in the published Sokudo walkthroughs.

## 5. Replace your browser token

In Local Storage, replace your normal token with the forged admin token:

20260905084217

Then refresh the application.

You should gain access to the Admin functionality.

The flag is typically exposed through:

GET /api/admin/users

or through the /admin interface.

Let's do it interactively. Send me the response from:

GET /api/stats/leaderboard