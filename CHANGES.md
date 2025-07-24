
# 🔧 All Changes Needed/Observed

## 🚩 Concerns

- **SQL Injection Risk**  
  Using string formatters in SQL statements is vulnerable to SQL injection.  
  **Bad Example:**
  ```python
  f"SELECT * FROM users WHERE name = {name}"
  ```

- **Insecure Password Storage**  
  Passwords were being stored in plain text in the database. This is not secure and can compromise user data.

- **Improper JSON Handling**  
  Previously used:
  ```python
  data = request.get_data()
  data = json.loads(data)
  ```
  🔁 Now replaced with:
  ```python
  data = request.get_json()
  ```
  which is the recommended method in Flask for handling JSON requests.

- **Unstructured API Responses**  
  GET APIs returned string data, reducing readability and not conforming to standard REST practices.

---

## ✅ Fixes

- **SQL Queries Secured**  
  Replaced formatters with parameterized queries:  
  ```python
  "UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id)
  ```

- **Password Security with `werkzeug.security`**  
  Passwords are now hashed for storage:

  1. `generate_password_hash(password)`  
     - Encrypts the password before storing it in the database.

  2. `check_password_hash(stored_hash, input_password)`  
     - Compares hashed password with user input during login.

- **Proper JSON Parsing**  
  All payloads are now handled with:
  ```python
  data = request.get_json()
  ```

- **Structured API Responses**  
  Introduced a model class to define a consistent response structure for better readability and maintainability.

---

## 🔧 Additional Changes

- Replaced all `print` statements with `logging` for production readiness.
- HTTP status codes are now sent along with API responses.
- Wrapped inputs in `try-except` blocks to handle and validate errors gracefully.

---

## 🤖 AI Usage

- Used **ChatGPT** to:
  - Generate unit test cases for the written APIs.
  - Assist in writing developer-facing documentation for the project.

---
