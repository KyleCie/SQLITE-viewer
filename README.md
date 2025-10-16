# SQL Request Viewer (Prototype)

A small tool that helps you **understand SQL queries step by step**.
It connects to a SQLite database and tries to **show how SQL commands are built and executed**.

---

## What it does

* Connects to a local SQLite database
* Reads and parses SQL commands
* Breaks complex queries into smaller parts
* Shows how `WHERE`, `ON`, and nested queries work

> ⚠️ The interpreter is still a **prototype**. It works, but will be **rewritten later**.

---

## How to use

1. Make sure you have **Python 3.10+** installed.
2. Run the script:

   ```bash
   python SQLviewer.py
   ```
3. It will print out how it understood the example SQL query.

You can also use it in your own code:

```python
from SQLviewer import DatabaseSystem, Interpreter

db = DatabaseSystem()
db.connect("your_database.db")

interpreter = Interpreter()
result = interpreter.interpret("SELECT * FROM users WHERE age > 30;")

print(result)
```

---

## Project files

* **`File`** – handles the SQLite connection
* **`DatabaseSystem`** – runs SQL commands
* **`Interpreter`** – reads and breaks SQL queries into smaller parts

---

## Example output

Example of what it prints:

```python
{
    "condition": ["WHERE HEROS.Id IN (@9) ORDER BY puissance_totale DESC  "],
    "name": "@0",
    "request": " SELECT HEROS.Titre, (@1) AS nb_villes, (@6) AS puissance_totale FROM HEROS ",
    "sub-request": [
        {
            "condition": [],
            "name": "@1",
            "request":  ...
```

---

## To do

* Create the function to run and show in the terminal the request.
* Add a better step-by-step view
* Optional: add a simple interface

---

---

## updates

* 16/10/25, [see commit](https://github.com/KyleCie/SQLITE-viewer/commit/ff70c2ed625ad0e7124bcfcc473b553f1eedc89b) :
  The entire Interpreter system (the parsing) has been rewirted, and change the list system to an entire dict system.
* 15/10/25, [see commit](https://github.com/KyleCie/SQLITE-viewer/commit/3dfe477d4d256c47d2bbe3ac2edc48fff9f0d87e) :
  initial commit.

---

## Requirements

Only uses Python’s standard libraries:
`sqlite3`, `warnings`, `pprint`, `time`, `typing`

---

## License

MIT License. Free to use and modify.

---