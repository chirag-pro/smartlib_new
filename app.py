import os
import re
import uuid
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from database import (
    init_db, get_all_books, get_book_by_id, add_book, update_book, delete_book,
    get_categories, create_user, get_user_by_username, get_user_by_email,
    get_user_by_id, get_all_users, update_user, update_user_password, toggle_user_status,
    issue_book, return_book, get_user_issued_books, get_user_returned_books, get_user_stats,
    get_library_stats, get_books_by_category, get_monthly_issues, get_monthly_returns,
    get_most_borrowed_books, get_all_issued_books, get_overdue_books,
    get_active_borrowers, get_user_registrations_monthly, calculate_fine
)
from auth import login_required, admin_required, get_current_user

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'library-management-dev-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # Allow a 5 MB image plus multipart form fields
BOOK_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'books', 'uploads')
os.makedirs(BOOK_UPLOAD_DIR, exist_ok=True)
ALLOWED_COVER_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

class CoverUploadError(ValueError):
    """A user supplied cover file is not an accepted image."""


def save_cover_from_request(current_cover=''):
    """Save a validated uploaded cover or accept a selected HTTPS cover URL."""
    if request.form.get('remove_cover') == '1':
        return ''
    uploaded = request.files.get('cover_file')
    if uploaded and uploaded.filename:
        safe_name = secure_filename(uploaded.filename)
        extension = os.path.splitext(safe_name)[1].lower()
        if extension not in ALLOWED_COVER_EXTENSIONS:
            raise CoverUploadError('Cover must be JPG, JPEG, PNG, or WEBP.')
        uploaded.stream.seek(0, os.SEEK_END)
        file_size = uploaded.stream.tell()
        uploaded.stream.seek(0)
        if file_size > 5 * 1024 * 1024:
            raise CoverUploadError('Cover images must be no larger than 5 MB.')
        header = uploaded.stream.read(12)
        uploaded.stream.seek(0)
        valid_image = (
            (extension in {'.jpg', '.jpeg'} and header.startswith(b'\xff\xd8\xff')) or
            (extension == '.png' and header.startswith(b'\x89PNG\r\n\x1a\n')) or
            (extension == '.webp' and header.startswith(b'RIFF') and header[8:12] == b'WEBP')
        )
        if not valid_image:
            raise CoverUploadError('The uploaded file does not look like a valid JPG, PNG, or WEBP image.')
        filename = f'{uuid.uuid4().hex}{extension}'
        uploaded.save(os.path.join(BOOK_UPLOAD_DIR, filename))
        return f'uploads/{filename}'

    selected = (request.form.get('cover_image') or '').strip()
    if not selected:
        return current_cover or ''
    if selected.startswith('https://'):
        parsed = urlparse(selected)
        if parsed.netloc and not parsed.username and not parsed.password:
            return selected
        raise CoverUploadError('The selected cover URL is not valid.')
    # Local stored paths are restricted to a simple name or the uploads/ subfolder.
    normalized = selected.replace('\\', '/')
    if normalized.startswith('static/books/'):
        normalized = normalized[len('static/books/'):]
    if normalized.startswith('/static/books/'):
        normalized = normalized[len('/static/books/'):]
    parts = normalized.split('/')
    if any(part in {'', '.', '..'} for part in parts) or len(parts) > 2 or (len(parts) == 2 and parts[0] != 'uploads'):
        raise CoverUploadError('The selected cover filename is not valid.')
    if not all(part.replace('-', '').replace('_', '').replace('.', '').isalnum() for part in parts):
        raise CoverUploadError('The selected cover filename is not valid.')
    return normalized


def book_form_data(existing_cover=''):
    data = {
        'title': request.form.get('title', '').strip(),
        'author': request.form.get('author', '').strip(),
        'category': request.form.get('category', '').strip(),
        'isbn': request.form.get('isbn', '').strip(),
        'publisher': request.form.get('publisher', '').strip(),
        'publication_year': request.form.get('publication_year', '').strip(),
        'quantity': request.form.get('quantity', '1').strip(),
        'shelf': request.form.get('shelf', '').strip(),
        'description': request.form.get('description', '').strip(),
    }
    data['cover_image'] = save_cover_from_request(existing_cover)
    return data


def validate_book_form(data):
    if not data['title'] or not data['author'] or not data['category']:
        return 'Title, Author, and Category are required.'
    try:
        quantity = int(data['quantity'])
        if quantity < 1:
            raise ValueError
    except (TypeError, ValueError):
        return 'Quantity must be a positive whole number.'
    year = data.get('publication_year')
    if year:
        try:
            if not 1800 <= int(year) <= datetime.now().year + 5:
                raise ValueError
            data['publication_year'] = int(year)
        except (TypeError, ValueError):
            return 'Enter a valid publication year.'
    else:
        data['publication_year'] = 0
    data['quantity'] = quantity
    return None


# ── Context Processor ──────────────────────────────────────────────────────────

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user(), now=datetime.now())

# ── Public Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = get_library_stats()
    featured = get_all_books()[:6]
    return render_template('index.html', stats=stats, featured=featured)

@app.route('/books')
def books():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    availability = request.args.get('availability', '')
    sort = request.args.get('sort', 'title')
    books_list = get_all_books(search=search, category=category, availability=availability, sort=sort)
    categories = get_categories()
    return render_template('books.html', books=books_list, categories=categories,
                           search=search, category=category, availability=availability, sort=sort)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return render_template('404.html'), 404
    already_borrowed = False
    if 'user_id' in session:
        from database import get_db
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND book_id=? AND status='Issued'",
                  (session['user_id'], book_id))
        already_borrowed = c.fetchone()[0] > 0
        conn.close()
    return render_template('book_details.html', book=book, already_borrowed=already_borrowed)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ── Auth Routes ────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name','').strip()
        username  = request.form.get('username','').strip()
        email     = request.form.get('email','').strip()
        phone     = request.form.get('phone','').strip()
        password  = request.form.get('password','')
        confirm   = request.form.get('confirm_password','')

        errors = []
        if not all([full_name, username, email, password, confirm]):
            errors.append('All fields are required.')
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append('Please enter a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if get_user_by_username(username):
            errors.append('Username already exists.')
        if get_user_by_email(email):
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', form=request.form)

        create_user(full_name, username, email, generate_password_hash(password), phone)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form={})

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            if user['status'] != 'Active':
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return render_template('login.html')
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# ── Student Routes ─────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    user_id = session['user_id']
    stats = get_user_stats(user_id)
    issued = get_user_issued_books(user_id)
    returned = get_user_returned_books(user_id)[:5]
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('dashboard.html', stats=stats, issued=issued,
                           returned=returned, today=today, calculate_fine=calculate_fine)

@app.route('/my-books')
@login_required
def my_books():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    user_id = session['user_id']
    issued = get_user_issued_books(user_id)
    returned = get_user_returned_books(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('my_books.html', issued=issued, returned=returned,
                           today=today, calculate_fine=calculate_fine)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    if session.get('role') == 'admin':
        flash('Admins cannot borrow books.', 'warning')
        return redirect(url_for('book_details', book_id=book_id))
    success, msg = issue_book(session['user_id'], book_id)
    if success:
        flash(f'Book borrowed successfully! Due date: {msg}', 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/return/<int:issue_id>', methods=['POST'])
@login_required
def return_book_route(issue_id):
    success, fine = return_book(issue_id, session['user_id'])
    if success:
        if fine > 0:
            flash(f'Book returned successfully. Fine: ₹{fine}', 'warning')
        else:
            flash('Book returned successfully. No fine.', 'success')
    else:
        flash('Unable to process return. Please try again.', 'danger')
    return redirect(url_for('my_books'))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            full_name = request.form.get('full_name','').strip()
            email     = request.form.get('email','').strip()
            phone     = request.form.get('phone','').strip()
            if not full_name or not email:
                flash('Name and email are required.', 'danger')
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                flash('Invalid email address.', 'danger')
            else:
                existing = get_user_by_email(email)
                if existing and existing['id'] != session['user_id']:
                    flash('Email already in use.', 'danger')
                else:
                    update_user(session['user_id'], {'full_name':full_name,'email':email,'phone':phone})
                    session['full_name'] = full_name
                    flash('Profile updated successfully.', 'success')
        elif action == 'change_password':
            current  = request.form.get('current_password','')
            new_pw   = request.form.get('new_password','')
            confirm  = request.form.get('confirm_password','')
            if not check_password_hash(user['password_hash'], current):
                flash('Current password is incorrect.', 'danger')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            elif new_pw != confirm:
                flash('Passwords do not match.', 'danger')
            else:
                update_user_password(session['user_id'], generate_password_hash(new_pw))
                flash('Password changed successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

# ── Admin Routes ───────────────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = get_library_stats()
    cat_data = get_books_by_category()
    monthly_issues = get_monthly_issues()
    monthly_returns = get_monthly_returns()
    most_borrowed = get_most_borrowed_books()
    user_regs = get_user_registrations_monthly()
    return render_template('admin/dashboard.html', stats=stats,
                           cat_data=cat_data, monthly_issues=monthly_issues,
                           monthly_returns=monthly_returns, most_borrowed=most_borrowed,
                           user_regs=user_regs)

@app.route('/admin/books')
@admin_required
def admin_books():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    books_list = get_all_books(search=search, category=category)
    categories = get_categories()
    return render_template('admin/books.html', books=books_list, categories=categories,
                           search=search, category=category)

@app.route('/admin/books/add', methods=['GET','POST'])
@admin_required
def admin_add_book():
    if request.method == 'POST':
        try:
            data = book_form_data()
        except CoverUploadError as exc:
            flash(str(exc), 'danger')
            return render_template('admin/add_book.html', form=request.form)
        error = validate_book_form(data)
        if error:
            flash(error, 'danger')
            return render_template('admin/add_book.html', form=request.form)
        try:
            add_book(data)
        except Exception as exc:
            # Surface common catalog conflicts without exposing the database traceback.
            if 'UNIQUE constraint failed: books.isbn' in str(exc):
                flash('That ISBN is already assigned to another book. Please verify the ISBN.', 'danger')
                return render_template('admin/add_book.html', form=request.form)
            raise
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_books'))
    return render_template('admin/add_book.html', form={})


@app.route('/admin/books/edit/<int:book_id>', methods=['GET','POST'])
@admin_required
def admin_edit_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return render_template('404.html'), 404
    if request.method == 'POST':
        try:
            data = book_form_data(book['cover_image'] or '')
        except CoverUploadError as exc:
            flash(str(exc), 'danger')
            return render_template('admin/edit_book.html', book=book, form=request.form)
        error = validate_book_form(data)
        if error:
            flash(error, 'danger')
            return render_template('admin/edit_book.html', book=book, form=request.form)
        try:
            update_book(book_id, data)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('admin/edit_book.html', book=book, form=request.form)
        except Exception as exc:
            if 'UNIQUE constraint failed: books.isbn' in str(exc):
                flash('That ISBN is already assigned to another book. Please verify the ISBN.', 'danger')
                return render_template('admin/edit_book.html', book=book, form=request.form)
            raise
        flash('Book updated successfully.', 'success')
        return redirect(url_for('admin_books'))
    return render_template('admin/edit_book.html', book=book, form=book)


@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def admin_delete_book(book_id):
    success = delete_book(book_id)
    if success:
        flash('Book deleted successfully.', 'success')
    else:
        flash('Cannot delete a book with active loans or borrowing history.', 'danger')
    return redirect(url_for('admin_books'))

@app.route('/admin/users')
@admin_required
def admin_users():
    search = request.args.get('search', '')
    users = get_all_users(search=search)
    return render_template('admin/users.html', users=users, search=search)

@app.route('/admin/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_user(user_id):
    toggle_user_status(user_id)
    flash('User status updated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/issued-books')
@admin_required
def admin_issued():
    status_filter = request.args.get('status', '')
    issues = get_all_issued_books(status_filter)
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/issued_books.html', issues=issues,
                           status_filter=status_filter, today=today,
                           calculate_fine=calculate_fine)

@app.route('/admin/returns')
@admin_required
def admin_returns():
    issues = get_all_issued_books('Returned')
    return render_template('admin/returns.html', issues=issues)

@app.route('/admin/overdue')
@admin_required
def admin_overdue():
    overdues = get_overdue_books()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/overdue.html', overdues=overdues,
                           today=today, calculate_fine=calculate_fine)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    stats = get_library_stats()
    cat_data = get_books_by_category()
    most_borrowed = get_most_borrowed_books()
    active_borrowers = get_active_borrowers()
    monthly_issues = get_monthly_issues()
    monthly_returns = get_monthly_returns()
    return render_template('admin/reports.html', stats=stats, cat_data=cat_data,
                           most_borrowed=most_borrowed, active_borrowers=active_borrowers,
                           monthly_issues=monthly_issues, monthly_returns=monthly_returns)

# ── Error Handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
