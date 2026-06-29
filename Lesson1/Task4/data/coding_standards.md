# NeuraStack Technologies — Coding Standards

## Overview
This document defines the coding standards and conventions followed across all NeuraStack engineering projects. All engineers are expected to adhere to these standards. Code that does not comply with these standards will be rejected during code review.

---

## 1. Naming Conventions

### Variables & Functions
- Use **camelCase** for variable names and function names in JavaScript/TypeScript.
  - ✅ `userName`, `fetchUserData()`, `isAuthenticated`
  - ❌ `user_name`, `FetchUserData()`, `is_authenticated`
- Use **snake_case** for variable names and function names in Python.
  - ✅ `user_name`, `fetch_user_data()`, `is_authenticated`
  - ❌ `userName`, `FetchUserData()`

### Classes & Interfaces
- Use **PascalCase** for class names, interfaces, and type aliases in all languages.
  - ✅ `UserService`, `IAuthProvider`, `ApiResponse`
  - ❌ `userService`, `iauthprovider`, `api_response`

### Constants
- Use **SCREAMING_SNAKE_CASE** for constants and environment variables.
  - ✅ `MAX_RETRY_COUNT`, `API_BASE_URL`, `DEFAULT_TIMEOUT_MS`
  - ❌ `maxRetryCount`, `apiBaseUrl`

### Files & Directories
- Python files: `snake_case.py` (e.g., `vector_store.py`, `user_service.py`)
- TypeScript/JavaScript files: `kebab-case.ts` (e.g., `auth-service.ts`, `user-model.ts`)
- React components: `PascalCase.tsx` (e.g., `UserProfile.tsx`, `NavBar.tsx`)
- Directories: `kebab-case` (e.g., `api-routes/`, `data-models/`)

---

## 2. Code Formatting

### Line Length
- Maximum line length is **120 characters** for all languages.
- Exceptions are allowed for URLs in comments or string literals.

### Indentation
- Use **2 spaces** for JavaScript, TypeScript, and JSON files.
- Use **4 spaces** for Python files.
- Never use tabs.

### Trailing Whitespace
- No trailing whitespace on any line.
- All files must end with a single newline character.

### Blank Lines
- Python: 2 blank lines between top-level definitions; 1 blank line between methods.
- TypeScript: 1 blank line between methods; no blank lines inside short functions.

---

## 3. Code Quality Rules

### Magic Numbers
- **Magic numbers are not allowed.** All numeric literals must be assigned to a named constant.
  - ❌ `if (retries > 3)`
  - ✅ `const MAX_RETRIES = 3; if (retries > MAX_RETRIES)`

### Functions
- Functions must have a **single responsibility** (Single Responsibility Principle).
- Maximum function length is **40 lines** of code (excluding comments and blank lines).
- Functions with more than **4 parameters** must use an options object or dataclass.

### Comments
- Write comments to explain **why**, not **what** the code does.
- Avoid obvious comments: `// increment i` above `i++` is not acceptable.
- All public functions and classes must have a docstring (Python) or JSDoc comment (TypeScript).

### Error Handling
- Never use bare `except` or `catch` without logging the error.
- All errors must be logged with at least the error message and the function name.
- User-facing error messages must never expose stack traces or internal details.

---

## 4. SOLID Principles

All NeuraStack code must follow the SOLID principles:

- **S — Single Responsibility:** Each class/module has one reason to change.
- **O — Open/Closed:** Classes are open for extension but closed for modification.
- **L — Liskov Substitution:** Subtypes must be substitutable for their base types.
- **I — Interface Segregation:** No client should depend on methods it does not use.
- **D — Dependency Inversion:** Depend on abstractions, not concrete implementations.

---

## 5. Testing Standards

- All new features must include unit tests before the PR is approved.
- Minimum test coverage threshold is **80%** for all services.
- Test files must be named `test_<module_name>.py` (Python) or `<module>.spec.ts` (TypeScript).
- Tests must not depend on external services or live databases; use mocks.
- Each test function must test **one scenario only** (no multi-assertion chaos tests).

---

## 6. Import Order

### Python (follow PEP 8 + isort)
1. Standard library imports
2. Third-party imports
3. Local application imports
Each group separated by a blank line.

### TypeScript
1. Node built-ins
2. External packages
3. Internal aliases (`@/...`)
4. Relative imports

---

## 7. Code Review Checklist
Before submitting a PR, self-review against this checklist:
- [ ] No magic numbers
- [ ] Functions are ≤ 40 lines
- [ ] Naming conventions followed
- [ ] All errors are handled and logged
- [ ] Unit tests added / updated
- [ ] No `console.log` or `print()` debug statements left in code
- [ ] No hardcoded secrets or credentials
- [ ] Docstrings/JSDoc added for public APIs
