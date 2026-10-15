# 📚 LibraryMS — Library Management System

> **Smart, Simple and Efficient Library Management**
> A fully functional college minor project built with Python Flask, SQLite, Bootstrap 5, and Chart.js.

---

## 📋 Project Description

LibraryMS is a complete web-based Library Management System that allows students to browse, borrow, and return books, while administrators can manage the entire library — books, users, transactions, fines, and analytics — through a professional dashboard.

---

## 🎯 Objectives

- Provide a digital platform for library operations
- Enable students to search and borrow books online
- Automate fine calculation for overdue returns
- Give administrators real-time insights through charts and reports
- Demonstrate core full-stack web development concepts

---

## ✨ Features

### Public / Visitor
- Professional home page with library statistics
- Browse complete book collection
- Search by title, author, ISBN, category
- Filter by category and availability
- Sort by various criteria
- View detailed book information

### Student
- Register with full validation
- Secure login with session management
- Personal dashboard with statistics
- Borrow books (max 3 active, 14-day period)
- Return books with automatic fine calculation
- View borrowing history
- Edit profile and change password

### Admin
- Comprehensive admin dashboard with 8 statistics
- 5 interactive Chart.js visualizations (real data)
- Full CRUD for books (Add / Edit / Delete / View)
- User management (activate / deactivate)
- View all issued books with status
- Return history with fine tracking
- Overdue books with dynamic fine calculation
- Detailed reports and analytics
- Print report functionality

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Database | SQLite (via sqlite3) |
| Charts | Chart.js |
| Icons | Font Awesome 6 |
| Fonts | Google Fonts (Playfair Display, Inter) |
| Auth | Werkzeug (password hashing) |
| Templates | Jinja2 |

---

## 📁 Project Structure

```
library_management_system/
│
├── app.py              ← Flask application, all routes
├── database.py         ← Database functions (CRUD)
├── auth.py             ← Decorators: login_required, admin_required
├── requirements.txt    ← Python dependencies
├── README.md
├── library.db          ← SQLite database (auto-created)
│
├── templates/
│   ├── base.html           ← Public layout (navbar, footer)
│   ├── index.html          ← Home page
│   ├── books.html          ← Book listing with search/filter
│   ├── book_details.html   ← Individual book page + borrow
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html      ← Student dashboard
│   ├── my_books.html       ← Borrowed + history tabs
│   ├── profile.html        ← Edit profile + change password
│   ├── about.html
│   ├── contact.html
│   ├── 404.html
│   ├── 500.html
│   └── admin/
│       ├── base_admin.html ← Admin layout (sidebar)
│       ├── dashboard.html  ← Admin dashboard + charts
│       ├── books.html      ← Book management table
│       ├── add_book.html
│       ├── edit_book.html
│       ├── users.html      ← User management
│       ├── issued_books.html
│       ├── returns.html
│       ├── overdue.html
│       └── reports.html
│
└── static/
    ├── css/style.css   ← All custom styles
    ├── js/script.js    ← JS: alerts, charts, confirm, sidebar
    └── images/         ← Place library images here
```

---

## ⚙️ System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for Bootstrap/Font Awesome CDN)

---

## 🚀 Installation & Setup

### 1. Clone or extract the project
```bash
cd library_management_system
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
python app.py
```

### 6. Open in browser
```
http://127.0.0.1:5000
```

The database (`library.db`) and all sample data are created automatically on first run.

---




> ⚠️ These are demo credentials for educational use. Change them before any real deployment.

---

## 📊 Database Tables

### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| full_name | TEXT | Student's full name |
| username | TEXT UNIQUE | Login username |
| email | TEXT UNIQUE | Email address |
| password_hash | TEXT | Werkzeug hashed password |
| role | TEXT | 'admin' or 'student' |
| phone | TEXT | Phone number |
| registration_date | TEXT | ISO datetime |
| status | TEXT | 'Active' or 'Inactive' |

### `books`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| title | TEXT | Book title |
| author | TEXT | Author name |
| category | TEXT | Subject category |
| isbn | TEXT UNIQUE | ISBN number |
| publisher | TEXT | Publisher name |
| publication_year | INTEGER | Year published |
| quantity | INTEGER | Total copies |
| available_quantity | INTEGER | Currently available |
| shelf | TEXT | Physical shelf location |
| description | TEXT | Book description |
| cover_image | TEXT | Local cover filename or HTTPS image URL |
| added_date | TEXT | Date added |

### `issued_books`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | References users.id |
| book_id | INTEGER FK | References books.id |
| issue_date | TEXT | Date issued |
| due_date | TEXT | Due date (issue + 14 days) |
| return_date | TEXT | Actual return date (NULL if active) |
| status | TEXT | 'Issued' or 'Returned' |
| fine | REAL | Fine amount (₹5/day) |

---

## 📖 Business Rules

- **Borrow limit:** Maximum 3 active books per student
- **Borrow period:** 14 days
- **Fine rate:** ₹5 per day after due date
- **Overdue condition:** `current_date > due_date` AND `return_date IS NULL`
- **Availability:** Cannot borrow if `available_quantity <= 0`
- **Duplicate prevention:** Cannot borrow the same book twice while already borrowed
- **Delete protection:** Books with active issues cannot be deleted

---

## 🎓 How to Explain This Project in Viva

### 1. What is the Library Management System?
A web application that digitizes library operations — students can borrow/return books online and admins can manage the entire library from a single dashboard.

### 2. Why Flask was used?
Flask is a lightweight Python web framework. It's easy to learn, has minimal boilerplate, and is perfect for small-to-medium projects like this college minor project.

### 3. Why SQLite was used?
SQLite is a serverless, file-based database. It requires zero configuration, is built into Python (`sqlite3` module), and is perfect for small applications where simplicity matters more than scalability.

### 4. What is CRUD?
CRUD stands for Create, Read, Update, Delete — the four basic database operations. This project uses CRUD for books (`add_book`, `get_all_books`, `update_book`, `delete_book`) and users.

### 5. How does registration work?
The user fills a form → Flask validates all fields (required fields, email format, unique username/email, password length, password match) → `generate_password_hash()` hashes the password → user record is inserted into the `users` table → redirect to login.

### 6. How does password hashing work?
We use Werkzeug's `generate_password_hash()` to create a secure hash (bcrypt/sha256). The plain password is never stored. On login, `check_password_hash(stored_hash, entered_password)` returns True/False.

### 7. How do login sessions work?
Flask's `session` is a signed cookie stored in the browser. After successful login, we store `session['user_id']`, `session['role']`, etc. On each protected page, we check if `session['user_id']` exists using the `@login_required` decorator.

### 8. How does role-based access work?
Two decorators: `@login_required` checks if logged in, `@admin_required` additionally checks if `session['role'] == 'admin'`. Students cannot access `/admin/*` routes.

### 9. How are books issued?
Student clicks "Borrow" → checks: (a) user has < 3 active books, (b) book not already borrowed by this user, (c) available_quantity > 0 → inserts record into `issued_books` with `status='Issued'` and `due_date = today + 14 days` → decrements `available_quantity` by 1.

### 10. How is a book returned?
Student clicks "Return" → finds the issue record → sets `return_date = today` and `status = 'Returned'` → calculates fine → increments `available_quantity` by 1.

### 11. How is the fine calculated?
```python
fine = max(0, days_between(due_date, return_date) * 5)
```
If returned on or before due date: fine = ₹0. Otherwise: ₹5 × number of late days.

### 12. How do database relationships work?
`issued_books` has two foreign keys: `user_id` references `users.id` and `book_id` references `books.id`. This is a many-to-many relationship (one student can borrow many books, one book can be borrowed by many students over time).

### 13. How are dashboard statistics generated?
SQL aggregate functions: `COUNT(*)`, `SUM()`, `MAX()`, `MIN()` combined with WHERE filters to count active issues, total fines, overdue books, etc. These are passed from Flask to the Jinja2 template as Python dictionaries.

### 14. How is Chart.js used?
The Flask route passes database query results (category counts, monthly data) as Python lists → Jinja2 renders them as JavaScript arrays in `<script>` tags → Chart.js uses these arrays to render doughnut, line, and bar charts on `<canvas>` elements.

### 15. What future improvements can be made?
- Email notifications for due dates
- Book reservation/waitlist system
- QR code scanning for book check-out
- PDF export for reports
- Multiple library branch support
- Book rating and review system
- REST API with JWT authentication
- Docker deployment

---

## 📝 Future Enhancements

1. Email reminders for overdue books
2. Book reservation / hold queue
3. QR code-based book tracking
4. PDF report export
5. Mobile app (React Native / Flutter)
6. Book recommendation engine
7. Multiple library branches
8. Student ID card integration
9. REST API for third-party access
10. Online fine payment gateway

---

## 🏁 Conclusion

LibraryMS demonstrates a complete, production-ready web application covering:
- Full-stack development (Python + HTML/CSS/JS)
- Relational database design and SQL
- User authentication and authorization
- CRUD operations
- Session management
- Role-based access control
- Data visualization with Chart.js
- Responsive design with Bootstrap 5
- Security best practices (password hashing, parameterized queries)

---

*Built as a College Minor Project | Flask + SQLite + Bootstrap 5*


## Verified Book Covers and Catalog Additions

- The bundled database now contains 58 books, including 18 additional AI, machine-learning, Python, NLP, data-science, database, networking, algorithms, JavaScript, and software-engineering titles.
- Sixteen supplied cover files in `static/books/` are mapped only to catalog entries whose visible title/author match those covers. Eleven other entries have cover URLs selected from book-specific Google Books or publisher/catalog records.
- Public book cards and details first use the saved cover. When none is saved, the browser searches Google Books and then Open Library by ISBN (when provided), title, and author. A candidate is displayed only when title and author match closely; category-only or random cover matches are not accepted.
- Administrators can find and preview a matching cover on Add/Edit Book, save the selected cover, or upload the exact front cover as JPG, PNG, or WEBP (maximum 5 MB). Uploads are kept in `static/books/uploads/`. Read `COVER_CATALOG_SOURCES.md` for the cover mapping and online source details.
- If no sufficiently close match is found or the browser is offline, the branded book placeholder remains visible instead of assigning a random cover. The admin upload control can be used to add the correct edition manually.
- Database upgrades are idempotent: re-running `init_db()` does not add duplicate catalog rows or overwrite a cover that an administrator has manually selected. It also corrects several known title/ISBN/category metadata errors in the original sample catalog.

### Uploading an exact cover

1. Log in as an administrator and open **Books → Add Book** or edit an existing book.
2. Enter the exact title and author, then select **Find matching cover**.
3. Check the visible preview before saving. If the edition is wrong or no correct result appears, upload a JPG/PNG/WEBP of the front cover instead.
4. Click **Add Book** or **Save Changes**. The cover remains attached to that book record.
- Set `SECRET_KEY` in the deployment environment before production use. Set `DATABASE_PATH` when the SQLite database should live outside the project directory.

Cover metadata comes from the Google Books and Open Library public catalog APIs. Edition availability and images depend on those providers; administrators should inspect the preview before saving.
