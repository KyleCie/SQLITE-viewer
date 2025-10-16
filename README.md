# SQL Request Viewer (Prototype)

A small tool that helps you **understand SQL queries step by step**.
It connects to a SQLite database and tries to **show how SQL commands are built and executed**.

---

## What it does

* Connects to a local SQLite database
* Reads and parses SQL commands
* Breaks complex queries into smaller parts
* Shows how `WHERE`, `ON`, and nested queries work

> ⚠️ The interpreter is still a **prototype**.

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

interpreter = Interpreter(db) # initiate with the database.
interpreter.interpret("SELECT * FROM users WHERE age > 30;") # parsing.
interpreter.run() # the actual run of sql commands
```

---

## Project files

* **`File`** – handles the SQLite connection
* **`DatabaseSystem`** – runs SQL commands
* **`Interpreter`** – reads and breaks SQL queries into smaller parts

---

## Example output

Example of what it prints:

```
FOR: SELECT SUM(HEROS.Age)/count(HEROS.Titre) FROM HEROS:
[(34,)] 

FOR: SELECT SUM(HEROS.Age)/count(HEROS.Titre) FROM HEROS WHERE HEROS.Ville = "Alberta":
[(36,)]

FOR: SELECT HEROS.Id FROM HEROS:
[(1,), (3,), (4,), (5,), (6,), (7,), (8,), (9,), (10,), (11,), (12,)]

FOR: SELECT HEROS.Id FROM HEROS WHERE HEROS.Titre = "Wolverine":
...

Done in 0. ... ms, initiated in 0. ... ms, and runned in 0. ... ms.
TOTAL: 0. ... ms.
```

---

## To do

* Add a better step-by-step view
* Optional: add a simple interface

---

---

## updates

* 16/10/25, [see commit](https://github.com/KyleCie/SQLITE-viewer/commit/f0bc0aaf75793113a5ee1952db7355bffb57f6f4) :
  Added the function to run and show in the terminal the request, and another function to traduct the dict to a list of usable sql commands.
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
## Authors

- [@KyleCie](https://www.github.com/KyleCie)


## Badges


[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

