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
[['SELECT ENNEMIS.Nom, HEROS.Nom FROM ENNEMIS INNER JOIN HEROS',
  'ON ENNEMIS.Ville LIKE "%City%" and HEROS.Ville LIKE "%City%" ...'], ...]
```

---

## To do

* Rewrite the interpreter
* Create the function to run and show in the terminal the request.
* Add a better step-by-step view
* Optional: add a simple interface

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

