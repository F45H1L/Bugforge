### Ottergram - Some posts are archived.

## 1. Open the challenge

Open the Ottergram lab in your browser and log in with the account you created.

You don't need Kali, Nmap, curl, or any terminal.

## 2. Open Developer Tools

Press:

F12

Then go to:

Network → Fetch/XHR

This lets you see the API requests made by the website.

## 3. Create a normal post

Go to the Create Post page and upload any image and post it.

You should see a request similar to:

POST /api/posts

The response should say:
```json
{
  "message": "Post created successfully"
}
```
This confirms that the application is using the /api/posts API.

## 4. Capture the GET /api/posts request

In the Network tab, find:

GET /api/posts

Click it and open Response.

You should see a list similar to:
```json
id: 19
id: 18
id: 1
id: 2
id: 3
...
id: 16
```
Notice something unusual:

1, 2, 3, ... 16, 18, 19
Post 17 is missing.

This is the first major clue.

Think about the challenge description: Some posts are archived. Therefore, the missing 17 is suspicious.

Instead of assuming it doesn't exist, investigate whether the API still recognizes that object.

## 5. Use the captured request as a template

Find your earlier post request:

POST /api/posts

Right-click it and choose Edit and Resend (or use Replay/Edit and Resend, depending on your browser).

Change the request method from POST to PUT and change the URL from /api/posts to /api/posts/17. So the request becomes PUT /api/posts/17

For this lab, you don't need to add a request body.

## 6. Send the modified request

Send the request.

The server responds 200 OK with:
```json
{
  "message": "Post updated successfully",
  "post": {
    "id": 17,
    "user_id": 7,
    "image_url": "/uploads/otter3.png",
    "caption": ""Sponsor code (do not repost): bug{Vg52NcAyI3YIflLUZpMXRMhjCBNrbwbM}",
    "is_archived": 1,
    "created_at": "2026-09-07 08:21:28"
  }
}
```

This is the critical discovery. Your account is user_id: 10 but the returned post belongs to user_id: 7> Yet the server allowed you to access/update it.

The same response contains the caption: 
```json
Sponsor code (do not repost): bug{Vg52NcAyI3YIflLUZpMXRMhjCBNrbwbM}
```
That's the challenge flag.

## Attack flow

Authenticated as user 10
        │
        ▼
GET /api/posts
        │
        ▼
Notice 1–16, 18, 19
        │
        ▼
Post 17 is missing
        │
        ▼
Challenge says "Some posts are archived"
        │
        ▼
PUT /api/posts/17
        │
        ▼
Server returns post 17
        │
        ├── user_id = 7
        ├── is_archived = 1
        └── caption contains flag

That's the complete browser-only solution.