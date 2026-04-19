# 🐛 Project Error Log

## 📌 General Information:
- **Project Name: ProntoERP**  
- **Lasted update: 18/04/2026**  

---

# Error #1: SQLAlchemy: Cannot import Projects Model

**Date: 18/04/2026**  
**Module:** User, Projects  
**Type:** Configuration

## 🔍 Description
It’s an **ORM configuration error** where SQLAlchemy fails to resolve a model name used in a relationship.

In simple terms: you defined a relationship using `"Projects"`, but when SQLAlchemy tried to set up the models, it couldn’t find any class with that name loaded in memory. Because of that, it raises an `InvalidRequestError`, saying it cannot locate `"Projects"`.


## 🧠 Root Cause
The root cause is that the `Projects` model was **not imported (and therefore not loaded into memory)** before SQLAlchemy attempted to configure the relationships.

Because SQLAlchemy only knows about models that have been executed/imported, it could not resolve the string `"Projects"` during mapper initialization, leading to the error.

## 🧪 How to Reproduce
Exact steps:
1. delete `from projects.projects_model import Projects` in `main.py`

## 🛠 Applied Solution
The solution is to **ensure the `Projects` model is imported before any database operation is executed**.

In practice, this means importing it during application startup (for example, in `main.py` or a central models file), so SQLAlchemy registers it in memory before it tries to resolve relationships.


## 📈 Future Improvement (optional but pro)
Import the model in another file and delete from main

## 📎 Relevant Code (optional)
...


# Error #2: Alembic: Target database is not up to date

**Date: 16/04/2026**  
**Module:** Alembic
**Type:** Configuration

---

## 🔍 Description
This error occurs when Alembic detects that the database schema version is behind the latest available migration.

In simple terms: Alembic expects the database to already have certain migrations applied, but the current state stored in the `alembic_version` table does not match the latest revision (head). Because of this mismatch, Alembic refuses to proceed with new operations and throws the error: “Target database is not up to date.”

## 🧠 Root Cause
The root cause is a desynchronization between migration files and the database state.

This typically happens when:
- Migration files are deleted or modified manually
- New migrations are created without applying previous ones
- The database was reset but Alembic history was not updated
- The `alembic_version` table contains a revision that does not match the current migration chain

As a result, Alembic detects inconsistency and blocks further actions.

## 🧪 How to Reproduce
Exact steps:
1. Create and apply a migration
2. Modify or delete a migration file in `versions/`
3. Attempt to generate or apply a new migration

Result: Alembic throws “Target database is not up to date.”

## 🛠 Applied Solution
The solution is to realign the database state with the migration history.

In development, this was solved by marking the database as up-to-date using:
- `alembic stamp head` → forces the database to match the latest revision without executing migrations

Alternatively, if migrations should be applied normally:
- `alembic upgrade head` → applies all pending migrations


## 📈 Future Improvement
- Avoid deleting or modifying migration files after they are created
- Always apply migrations before generating new ones
- Maintain a consistent migration history
- Use reset strategies (stamp or full rebuild) when the migration chain is broken

## 📎 Relevant Code (optional)
...
