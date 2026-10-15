import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'library.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    create_tables()
    seed_data()
    ensure_catalog_enhancements()

def create_tables():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            phone TEXT,
            registration_date TEXT,
            status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT UNIQUE,
            publisher TEXT,
            publication_year INTEGER,
            quantity INTEGER NOT NULL,
            available_quantity INTEGER NOT NULL,
            shelf TEXT,
            description TEXT,
            cover_image TEXT,
            added_date TEXT
        );

        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL,
            fine REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        );
    ''')
    conn.commit()
    conn.close()

def seed_data():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Admin
    c.execute('''INSERT INTO users (full_name,username,email,password_hash,role,phone,registration_date,status)
                 VALUES (?,?,?,?,?,?,?,?)''',
              ('Administrator', 'admin', 'admin@library.com',
               generate_password_hash('admin123'), 'admin', '9999999999', today, 'Active'))

    # Demo student
    c.execute('''INSERT INTO users (full_name,username,email,password_hash,role,phone,registration_date,status)
                 VALUES (?,?,?,?,?,?,?,?)''',
              ('Demo Student', 'student', 'student@library.com',
               generate_password_hash('student123'), 'student', '8888888888', today, 'Active'))

    books = [
        # ── Original 20 books ──────────────────────────────────────────────────
        ('Python Crash Course','Eric Matthes','Python','978-1-59327-928-8','No Starch Press',2023,5,5,'A-1','A fast-paced, hands-on introduction to programming with Python.',''),
        ('Automate the Boring Stuff with Python','Al Sweigart','Python','978-1-59327-599-0','No Starch Press',2020,4,4,'A-2','Learn Python while automating real-world tasks.',''),
        ('Hands-On Machine Learning','Aurélien Géron','Machine Learning','978-1-09-812555-6','O\'Reilly',2022,3,3,'B-1','Using Scikit-Learn, Keras and TensorFlow.',''),
        ('Artificial Intelligence: A Modern Approach','Stuart Russell','Artificial Intelligence','978-0-13-468599-1','Pearson',2020,3,3,'B-2','The leading textbook in Artificial Intelligence.',''),
        ('Data Structures and Algorithms Made Easy','Narasimha Karumanchi','Data Structures','978-8-19-245734-9','CareerMonk',2020,6,6,'C-1','700+ algorithmic problems and data structure questions.',''),
        ('Database System Concepts','Abraham Silberschatz','DBMS','978-0-07-802215-9','McGraw-Hill',2020,4,4,'D-1','The standard text for database systems.',''),
        ('Computer Networks','Andrew S. Tanenbaum','Computer Networks','978-0-13-212695-3','Pearson',2021,3,3,'E-1','A top-down approach to computer networking.',''),
        ('Operating System Concepts','Abraham Silberschatz','Operating Systems','978-1-11-906333-0','Wiley',2018,4,4,'F-1','The dinosaur book — the OS standard reference.',''),
        ('Clean Code','Robert C. Martin','Software Engineering','978-0-13-235088-4','Prentice Hall',2008,5,5,'G-1','A handbook of agile software craftsmanship.',''),
        ('HTML and CSS','Jon Duckett','Web Development','978-1-11-899402-0','Wiley',2011,4,4,'H-1','Design and build websites the professional way.',''),
        ('Introduction to Algorithms','Thomas H. Cormen','Data Structures','978-0-26-204630-5','MIT Press',2022,3,3,'C-2','CLRS — the definitive algorithms textbook.',''),
        ('The Pragmatic Programmer','David Thomas','Software Engineering','978-0-13-595705-9','Addison-Wesley',2019,4,4,'G-2','Your journey to mastery — timeless programming wisdom.',''),
        ('Deep Learning','Ian Goodfellow','Machine Learning','978-0-26-203561-3','MIT Press',2016,3,3,'B-3','The authoritative deep learning reference.',''),
        ('Computer Organization and Architecture','William Stallings','Computer Networks','978-0-13-461026-5','Pearson',2021,3,3,'E-2','Designing for performance at every level.',''),
        ('Head First Java','Kathy Sierra','Java','978-0-59-600712-6','O\'Reilly',2005,5,5,'A-3','A brain-friendly guide to Java programming.',''),
        ('Effective Java','Joshua Bloch','Java','978-0-13-468599-2','Addison-Wesley',2018,3,3,'A-4','Best practices for the Java platform.',''),
        ('C++ Primer','Stanley B. Lippman','C++','978-0-32-171411-4','Addison-Wesley',2012,4,4,'A-5','The definitive introduction to C++.',''),
        ('Discrete Mathematics','Kenneth H. Rosen','Mathematics','978-0-07-338309-5','McGraw-Hill',2018,5,5,'I-1','Foundations of computer science mathematics.',''),
        ('Software Engineering','Ian Sommerville','Software Engineering','978-0-13-703515-1','Pearson',2015,4,4,'G-3','A comprehensive guide to software engineering practice.',''),
        ('JavaScript: The Good Parts','Douglas Crockford','Web Development','978-0-59-651774-8','O\'Reilly',2008,4,4,'H-2','Unearthing the excellence in JavaScript.',''),
        # ── 20 Additional books ────────────────────────────────────────────────
        ('Design Patterns','Gang of Four','Software Engineering','978-0-20-163361-5','Addison-Wesley',1994,4,4,'G-4','Reusable solutions to common software design problems.',''),
        ('The Art of Computer Programming','Donald E. Knuth','Data Structures','978-0-20-13567-0','Addison-Wesley',2011,2,2,'C-3','The definitive multi-volume reference on algorithms.',''),
        ('Structure and Interpretation of Computer Programs','Harold Abelson','Python','978-0-26-251087-5','MIT Press',1996,3,3,'A-6','The classic MIT programming and computation textbook.',''),
        ('Computer Science: An Overview','J. Glenn Brookshear','Computer Networks','978-0-13-359162-9','Pearson',2018,4,4,'E-3','A comprehensive introduction to computer science concepts.',''),
        ('Linear Algebra and Its Applications','Gilbert Strang','Mathematics','978-0-03-010567-8','Thomson Brooks',2006,3,3,'I-2','Clear and intuitive explanation of linear algebra.',''),
        ('Probability and Statistics for Engineering','Jay L. Devore','Mathematics','978-1-30-570906-8','Cengage',2016,4,4,'I-3','Engineering and science statistical methods.',''),
        ('Digital Design','M. Morris Mano','Operating Systems','978-0-13-198045-0','Pearson',2013,3,3,'F-2','Fundamental principles of digital logic design.',''),
        ('Signals and Systems','Alan V. Oppenheim','Artificial Intelligence','978-0-13-814757-0','Prentice Hall',1996,3,3,'B-4','Continuous and discrete signal processing.',''),
        ('Modern Operating Systems','Andrew S. Tanenbaum','Operating Systems','978-0-13-359162-8','Pearson',2015,4,4,'F-3','A thorough and authoritative look at operating systems.',''),
        ('Cryptography and Network Security','William Stallings','Computer Networks','978-0-13-335469-0','Pearson',2017,3,3,'E-4','Principles and practice of network security.',''),
        ('Compilers: Principles, Techniques, and Tools','Alfred V. Aho','Software Engineering','978-0-32-148681-3','Addison-Wesley',2006,2,2,'G-5','The Dragon Book — the standard compiler reference.',''),
        ('Programming in C','Stephen G. Kochan','C++','978-0-32-177698-3','Addison-Wesley',2014,5,5,'A-7','A complete and thorough introduction to C programming.',''),
        ('React: Up and Running','Stoyan Stefanov','Web Development','978-1-49-195282-4','O\'Reilly',2022,4,4,'H-3','Build maintainable and high-performing web apps with React.',''),
        ('Node.js Design Patterns','Mario Casciaro','Web Development','978-1-83921-520-9','Packt',2020,3,3,'H-4','Master best practices for building Node.js applications.',''),
        ('Learning Python','Mark Lutz','Python','978-1-44-939571-8','O\'Reilly',2013,4,4,'A-8','The definitive Python learning resource — 1500+ pages.',''),
        ('Flask Web Development','Miguel Grinberg','Python','978-1-49-195690-7','O\'Reilly',2018,3,3,'A-9','Developing web applications with Python and Flask.',''),
        ('Machine Learning Yearning','Andrew Ng','Machine Learning','978-0-00-000000-1','DeepLearning.AI',2018,5,5,'B-5','Technical strategy for AI engineers and ML teams.',''),
        ('Artificial Intelligence with Python','Prateek Joshi','Artificial Intelligence','978-1-78355-240-1','Packt',2017,4,4,'B-6','Build intelligent apps using Python and AI techniques.',''),
        ('Data Science from Scratch','Joel Grus','Machine Learning','978-1-49-194064-1','O\'Reilly',2019,4,4,'B-7','First principles of data science with Python.',''),
        ('Big Data: A Revolution','Viktor Mayer-Schönberger','DBMS','978-0-54-400232-1','Houghton Mifflin',2013,3,3,'D-2','How big data is transforming the way we live and work.',''),
    ]
    for b in books:
        c.execute('''INSERT INTO books (title,author,category,isbn,publisher,publication_year,quantity,available_quantity,shelf,description,cover_image,added_date)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],today))

    conn.commit()
    conn.close()

# ── Safe catalog migration for existing installations ──────────────────────────
def ensure_catalog_enhancements():
    """Add recommended CS/AI titles to old databases without overwriting records."""
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    recommended = [
        ('AI Engineering: Building Applications with Foundation Models', 'Chip Huyen', 'Artificial Intelligence', '9781098166304', "O'Reilly Media", 2025, 2, 2, 'B-8', 'A practical guide to building applications with foundation models.', 'https://books.google.com/books/content?id=YLbT0AEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('Designing Machine Learning Systems', 'Chip Huyen', 'Machine Learning', '9781098107963', "O'Reilly Media", 2022, 3, 3, 'B-9', 'Designing reliable, scalable, maintainable, and production-ready ML systems.', 'https://books.google.com/books/content?id=BAy_zgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('Python for Data Analysis', 'Wes McKinney', 'Data Science', '9781098104030', "O'Reilly Media", 2022, 3, 3, 'J-1', 'Hands-on data wrangling and analysis with pandas, NumPy, and Jupyter.', 'b5.jpg'),
        ('Natural Language Processing with Python', 'Steven Bird, Ewan Klein, Edward Loper', 'Natural Language Processing', '9780596516499', "O'Reilly Media", 2009, 3, 3, 'J-2', 'An introduction to language technologies and NLP with the NLTK toolkit.', 'https://books.google.com/books/content?id=KkKbAgAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('Data Science for Business', 'Foster Provost, Tom Fawcett', 'Data Science', '9781449361327', "O'Reilly Media", 2013, 3, 3, 'J-3', 'Understand data mining and data-analytic thinking for business decisions.', 'https://books.google.com/books/content?id=_1b4nAEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('The Hundred-Page Machine Learning Book', 'Andriy Burkov', 'Machine Learning', '9781999579500', 'Andriy Burkov', 2019, 3, 3, 'B-10', 'A concise, practical introduction to key machine learning concepts.', 'https://books.google.com/books/content?id=ZF3KwQEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('Fluent Python', 'Luciano Ramalho', 'Python', '9781492056355', "O'Reilly Media", 2022, 3, 3, 'A-10', 'Effective Python programming through idiomatic language features and patterns.', 'b6.jpg'),
        ('Practical Statistics for Data Scientists', 'Peter Bruce, Andrew Bruce, Peter Gedeck', 'Data Science', '9781492072911', "O'Reilly Media", 2020, 3, 3, 'J-4', 'Practical statistical methods for data analysis and data science workflows.', 'https://books.google.com/books/content?id=k2XcDwAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
        ('Designing Data-Intensive Applications', 'Martin Kleppmann', 'Data Engineering', '9781449373320', "O'Reilly Media", 2017, 2, 2, 'J-5', 'Practical guidance for designing reliable, scalable, and maintainable data systems.', 'b7.jpg'),
        ('Refactoring: Improving the Design of Existing Code', 'Martin Fowler', 'Software Engineering', '9780134757599', 'Addison-Wesley Professional', 2019, 2, 2, 'G-6', 'Techniques for restructuring code while preserving its behavior.', 'b8.jpg'),
        ('Pattern Recognition and Machine Learning', 'Christopher M. Bishop', 'Machine Learning', '9780387310732', 'Springer', 2006, 2, 2, 'B-11', 'A foundational statistical approach to pattern recognition and machine learning.', 'b9.jpg'),
        ('Grokking Algorithms: An Illustrated Guide for Programmers and Other Curious People', 'Aditya Y. Bhargava', 'Algorithms', '9781617292231', 'Manning Publications', 2016, 3, 3, 'C-4', 'Illustrated, beginner-friendly explanations of common algorithms and data structures.', 'b10.jpg'),
        ('Learning SQL: Generate, Manipulate, and Retrieve Data', 'Alan Beaulieu', 'DBMS', '9781492057611', "O'Reilly Media", 2020, 3, 3, 'D-2', 'Learn practical SQL queries for relational databases and data management.', 'b11.jpg'),
        ('Computer Networking: A Top-Down Approach', 'James F. Kurose, Keith W. Ross', 'Computer Networks', '9781292405469', 'Pearson Education', 2022, 3, 3, 'E-5', 'An eighth-edition, global-edition introduction to networking protocols and layered design.', 'b12.jpg'),
        ('Eloquent JavaScript: A Modern Introduction to Programming', 'Marijn Haverbeke', 'JavaScript', '9781593279509', 'No Starch Press', 2018, 3, 3, 'H-5', 'A modern introduction to JavaScript and practical programming techniques.', 'b14.jpg'),
        ('Artificial Intelligence: Foundations of Computational Agents', 'David L. Poole, Alan K. Mackworth', 'Artificial Intelligence', '9781107195394', 'Cambridge University Press', 2017, 2, 2, 'B-12', 'A formal and engineering-oriented introduction to AI and intelligent agents.', 'b15.jpg'),
        ("Don't Make Me Think, Revisited: A Common Sense Approach to Web Usability", 'Steve Krug', 'UI/UX Design', '9780321965516', 'New Riders', 2014, 2, 2, 'H-6', 'A practical guide to intuitive web navigation and usability.', 'b16.jpg'),
        ("You Don't Know JS Yet: Get Started", 'Kyle Simpson', 'JavaScript', '9781098110772', "O'Reilly Media", 2020, 2, 2, 'H-7', 'An introduction to JavaScript fundamentals and the language itself.', 'b17.jpg'),
    ]
    conn = get_db()
    c = conn.cursor()
    corrections = [
        ('9780134610993', 'Artificial Intelligence: A Modern Approach', 'Stuart Russell, Peter Norvig', 'Pearson', 2020, 'Artificial Intelligence'),
        ('9781786464392', 'Artificial Intelligence with Python', 'Prateek Joshi', 'Packt Publishing', 2017, 'Artificial Intelligence'),
        ('9780544002692', 'Big Data: A Revolution That Will Transform How We Live, Work, and Think', 'Viktor Mayer-Schönberger, Kenneth Cukier', 'Houghton Mifflin Harcourt', 2013, 'Data Science'),
        (None, 'Machine Learning Yearning', 'Andrew Ng', 'DeepLearning.AI', 2018, 'Machine Learning'),
        ('9780201896831', 'The Art of Computer Programming', 'Donald E. Knuth', 'Addison-Wesley', 1997, 'Data Structures'),
    ]
    for isbn, title, author, publisher, year, category in corrections:
        row = c.execute('SELECT id FROM books WHERE title=?', (title,)).fetchone()
        if not row and title.startswith('Big Data:'):
            row = c.execute("SELECT id FROM books WHERE title LIKE 'Big Data:%' AND author LIKE 'Viktor Mayer%'").fetchone()
        if row:
            if isbn and c.execute('SELECT id FROM books WHERE isbn=? AND id<>?', (isbn, row['id'])).fetchone():
                isbn_to_write = None
            else:
                isbn_to_write = isbn
            if title.startswith('Big Data:'):
                c.execute("UPDATE books SET title=?, author=?, isbn=?, publisher=?, publication_year=?, category=? WHERE id=?",
                          (title, author, isbn_to_write, publisher, year, category, row['id']))
            else:
                c.execute("UPDATE books SET author=?, isbn=?, publisher=?, publication_year=?, category=? WHERE id=?",
                          (author, isbn_to_write, publisher, year, category, row['id']))
    for book in recommended:
        title, author, category, isbn, publisher, year, qty, available, shelf, description, cover = book
        if c.execute('SELECT 1 FROM books WHERE lower(title)=lower(?)', (title,)).fetchone():
            continue
        if c.execute('SELECT 1 FROM books WHERE isbn=?', (isbn,)).fetchone():
            continue
        c.execute("INSERT INTO books (title,author,category,isbn,publisher,publication_year,quantity,available_quantity,shelf,description,cover_image,added_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  (title, author, category, isbn, publisher, year, qty, available, shelf, description, cover, today))
    # Correct the earlier seed ISBN to the documented second-edition ISBN.
    stats_row = c.execute("SELECT id, isbn FROM books WHERE title='Practical Statistics for Data Scientists'").fetchone()
    if stats_row and stats_row['isbn'] == '9781098102364' and not c.execute("SELECT 1 FROM books WHERE isbn='9781492072911' AND id<>?", (stats_row['id'],)).fetchone():
        c.execute("UPDATE books SET isbn='9781492072911' WHERE id=?", (stats_row['id'],))

    ai_agents_row = c.execute("SELECT id, isbn FROM books WHERE title='Artificial Intelligence: Foundations of Computational Agents'").fetchone()
    if ai_agents_row and not ai_agents_row['isbn'] and not c.execute("SELECT 1 FROM books WHERE isbn='9781107195394'").fetchone():
        c.execute("UPDATE books SET isbn='9781107195394' WHERE id=?", (ai_agents_row['id'],))

    # Seed only edition/title-confirmed cover endpoints. Keep any cover manually saved by an admin.
    verified_covers = {
        'Python Crash Course': 'https://books.google.com/books/content?id=BkCQEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'HTML and CSS': 'b2.jpg',
        'Head First Java': 'b3.jpg',
        'Software Engineering': 'b4.jpg',
        'Python for Data Analysis': 'b5.jpg',
        'Fluent Python': 'b6.jpg',
        'Modern Operating Systems': 'b13.jpg',
        'Designing Data-Intensive Applications': 'b7.jpg',
        'Refactoring: Improving the Design of Existing Code': 'b8.jpg',
        'Pattern Recognition and Machine Learning': 'b9.jpg',
        'Grokking Algorithms: An Illustrated Guide for Programmers and Other Curious People': 'b10.jpg',
        'Learning SQL: Generate, Manipulate, and Retrieve Data': 'b11.jpg',
        'Computer Networking: A Top-Down Approach': 'b12.jpg',
        'Eloquent JavaScript: A Modern Introduction to Programming': 'b14.jpg',
        'Artificial Intelligence: Foundations of Computational Agents': 'b15.jpg',
        "Don't Make Me Think, Revisited: A Common Sense Approach to Web Usability": 'b16.jpg',
        "You Don't Know JS Yet: Get Started": 'b17.jpg',
        'Automate the Boring Stuff with Python': 'https://books.google.com/books/content?id=UEu0CAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Artificial Intelligence: A Modern Approach': 'https://books.google.com/books/content?id=koFptAEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Artificial Intelligence with Python': 'https://static.fnac-static.com/multimedia/PE/Images/FR/MC/b6/c0/ff/50315446/1507-1/tsp20240620234345/Artificial-Intelligence-with-Python-by-Prateek-Joshi.jpg',
        'Big Data: A Revolution That Will Transform How We Live, Work, and Think': 'https://d3525k1ryd2155.cloudfront.net/f/692/002/9780544002692.HO.0.x.jpg',
        'AI Engineering: Building Applications with Foundation Models': 'https://books.google.com/books/content?id=YLbT0AEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Designing Machine Learning Systems': 'https://books.google.com/books/content?id=BAy_zgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Natural Language Processing with Python': 'https://books.google.com/books/content?id=KkKbAgAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Data Science for Business': 'https://books.google.com/books/content?id=_1b4nAEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'The Hundred-Page Machine Learning Book': 'https://books.google.com/books/content?id=ZF3KwQEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Practical Statistics for Data Scientists': 'https://books.google.com/books/content?id=k2XcDwAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
    }
    old_generated_covers = {
        'Python for Data Analysis': 'https://books.google.com/books/content?id=PZvwzgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
        'Fluent Python': 'https://books.google.com/books/content?id=H1SXzQEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
    }
    for title, cover_url in verified_covers.items():
        previous_generated = old_generated_covers.get(title)
        if previous_generated:
            c.execute("UPDATE books SET cover_image=? WHERE title=? AND (cover_image IS NULL OR trim(cover_image)='' OR cover_image=?)", (cover_url, title, previous_generated))
        else:
            c.execute("UPDATE books SET cover_image=? WHERE title=? AND (cover_image IS NULL OR trim(cover_image)='')", (cover_url, title))

    c.execute("UPDATE books SET category='Computer Organization' WHERE title='Computer Organization and Architecture'")
    c.execute("UPDATE books SET category='Digital Logic' WHERE title='Digital Design'")
    c.execute("UPDATE books SET category='C' WHERE title='Programming in C'")
    c.execute("UPDATE books SET isbn=NULL WHERE title='Machine Learning Yearning' AND isbn='978-0-00-000000-1'")
    conn.commit()
    conn.close()


# ── Book functions ─────────────────────────────────────────────────────────────

def get_all_books(search='', category='', availability='', sort='title'):
    conn = get_db()
    c = conn.cursor()
    q = "SELECT * FROM books WHERE 1=1"
    params = []
    if search:
        q += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?)"
        s = f'%{search}%'
        params += [s,s,s,s]
    if category:
        q += " AND category=?"
        params.append(category)
    if availability == 'available':
        q += " AND available_quantity>0"
    elif availability == 'unavailable':
        q += " AND available_quantity<=0"
    sort_map = {'title':'title ASC','author':'author ASC','newest':'publication_year DESC','availability':'available_quantity DESC'}
    q += f" ORDER BY {sort_map.get(sort,'title ASC')}"
    c.execute(q, params)
    books = c.fetchall()
    conn.close()
    return books

def get_book_by_id(book_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = c.fetchone()
    conn.close()
    return book

def add_book(data):
    conn = get_db()
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO books (title,author,category,isbn,publisher,publication_year,quantity,available_quantity,shelf,description,cover_image,added_date)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
              (data['title'],data['author'],data['category'],(data.get('isbn') or None),
               data.get('publisher',''),data.get('publication_year',0),
               int(data['quantity']),int(data['quantity']),
               data.get('shelf',''),data.get('description',''),
               data.get('cover_image','default.jpg'),today))
    conn.commit()
    conn.close()

def update_book(book_id, data):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM books WHERE id=?", (book_id,))
    if not c.fetchone():
        conn.close()
        return False

    new_qty = int(data['quantity'])
    c.execute("SELECT COUNT(*) FROM issued_books WHERE book_id=? AND status='Issued'", (book_id,))
    active_loans = c.fetchone()[0]
    if new_qty < active_loans:
        conn.close()
        raise ValueError(f"Total quantity cannot be less than the {active_loans} currently issued copies.")

    # Calculate availability from active loans to preserve the stock invariant.
    new_avail = new_qty - active_loans
    c.execute('''UPDATE books SET title=?,author=?,category=?,isbn=?,publisher=?,publication_year=?,
                 quantity=?,available_quantity=?,shelf=?,description=?,cover_image=? WHERE id=?''',
              (data['title'],data['author'],data['category'],(data.get('isbn') or None),
               data.get('publisher',''),data.get('publication_year',0),
               new_qty,new_avail,data.get('shelf',''),data.get('description',''),
               data.get('cover_image','default.jpg'),book_id))
    conn.commit()
    conn.close()
    return True

def delete_book(book_id):
    conn = get_db()
    c = conn.cursor()
    # Preserve history because issued_books references books via a foreign key.
    c.execute("SELECT COUNT(*) FROM issued_books WHERE book_id=?", (book_id,))
    history_count = c.fetchone()[0]
    if history_count > 0:
        conn.close()
        return False
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return True

def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM books ORDER BY category")
    cats = [r['category'] for r in c.fetchall()]
    conn.close()
    return cats

# ── User functions ─────────────────────────────────────────────────────────────

def create_user(full_name, username, email, password_hash, phone):
    conn = get_db()
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO users (full_name,username,email,password_hash,role,phone,registration_date,status)
                 VALUES (?,?,?,?,?,?,?,?)''',
              (full_name,username,email,password_hash,'student',phone,today,'Active'))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    u = c.fetchone()
    conn.close()
    return u

def get_user_by_email(email):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    u = c.fetchone()
    conn.close()
    return u

def get_user_by_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    conn.close()
    return u

def get_all_users(search=''):
    conn = get_db()
    c = conn.cursor()
    if search:
        c.execute("SELECT * FROM users WHERE role='student' AND (full_name LIKE ? OR username LIKE ? OR email LIKE ?) ORDER BY id DESC",
                  (f'%{search}%',f'%{search}%',f'%{search}%'))
    else:
        c.execute("SELECT * FROM users WHERE role='student' ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    return users

def update_user(user_id, data):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET full_name=?,email=?,phone=? WHERE id=?",
              (data['full_name'],data['email'],data.get('phone',''),user_id))
    conn.commit()
    conn.close()

def update_user_password(user_id, new_hash):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user_id))
    conn.commit()
    conn.close()

def toggle_user_status(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status FROM users WHERE id=?", (user_id,))
    cur = c.fetchone()['status']
    new_status = 'Inactive' if cur == 'Active' else 'Active'
    c.execute("UPDATE users SET status=? WHERE id=?", (new_status, user_id))
    conn.commit()
    conn.close()

# ── Issue / Return functions ───────────────────────────────────────────────────

def calculate_fine(due_date_str, return_date_str=None):
    due = datetime.strptime(due_date_str, '%Y-%m-%d')
    ref = datetime.strptime(return_date_str, '%Y-%m-%d') if return_date_str else datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    days_late = (ref - due).days
    return max(0, days_late * 5)

def issue_book(user_id, book_id):
    conn = get_db()
    c = conn.cursor()

    # Check active borrows
    c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND status='Issued'", (user_id,))
    if c.fetchone()[0] >= 3:
        conn.close()
        return False, "You have reached the maximum limit of 3 active borrowed books."

    # Check duplicate
    c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND book_id=? AND status='Issued'", (user_id,book_id))
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "You have already borrowed this book."

    # Check availability
    c.execute("SELECT available_quantity FROM books WHERE id=?", (book_id,))
    book = c.fetchone()
    if not book or book['available_quantity'] <= 0:
        conn.close()
        return False, "This book is currently unavailable."

    today = datetime.now()
    due = today + timedelta(days=14)
    c.execute('''INSERT INTO issued_books (user_id,book_id,issue_date,due_date,status,fine)
                 VALUES (?,?,?,?,?,?)''',
              (user_id, book_id, today.strftime('%Y-%m-%d'), due.strftime('%Y-%m-%d'), 'Issued', 0))
    c.execute("UPDATE books SET available_quantity=available_quantity-1 WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return True, due.strftime('%d %B %Y')

def return_book(issue_id, user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM issued_books WHERE id=? AND user_id=? AND status='Issued'", (issue_id, user_id))
    issue = c.fetchone()
    if not issue:
        conn.close()
        return False, 0
    today = datetime.now().strftime('%Y-%m-%d')
    fine = calculate_fine(issue['due_date'], today)
    c.execute("UPDATE issued_books SET return_date=?,status='Returned',fine=? WHERE id=?",
              (today, fine, issue_id))
    c.execute("UPDATE books SET available_quantity=available_quantity+1 WHERE id=?", (issue['book_id'],))
    conn.commit()
    conn.close()
    return True, fine

def get_user_issued_books(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT ib.*,b.title,b.author,b.cover_image,b.category
                 FROM issued_books ib JOIN books b ON ib.book_id=b.id
                 WHERE ib.user_id=? AND ib.status='Issued' ORDER BY ib.issue_date DESC''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_returned_books(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT ib.*,b.title,b.author,b.cover_image,b.category
                 FROM issued_books ib JOIN books b ON ib.book_id=b.id
                 WHERE ib.user_id=? AND ib.status='Returned' ORDER BY ib.return_date DESC''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_stats(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND status='Issued'", (user_id,))
    active = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND status='Returned'", (user_id,))
    returned = c.fetchone()[0]
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM issued_books WHERE user_id=? AND status='Issued' AND due_date<?", (user_id,today))
    overdue = c.fetchone()[0]
    c.execute('''SELECT COALESCE(SUM(CASE WHEN status='Issued' THEN
                 MAX(0,(julianday('now') - julianday(due_date))*5)
                 ELSE fine END),0) FROM issued_books WHERE user_id=?''', (user_id,))
    fine = c.fetchone()[0]
    conn.close()
    return {'active':active,'returned':returned,'overdue':overdue,'fine':round(fine,2)}

# ── Admin functions ────────────────────────────────────────────────────────────

def get_library_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(quantity),0) FROM books")
    total_copies = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(available_quantity),0) FROM books")
    available = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM issued_books WHERE status='Issued'")
    active_issues = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM issued_books WHERE status='Returned'")
    returned = c.fetchone()[0]
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM issued_books WHERE status='Issued' AND due_date<?", (today,))
    overdue = c.fetchone()[0]
    c.execute('''SELECT COALESCE(SUM(CASE WHEN status='Issued' THEN
                 MAX(0,(julianday('now')-julianday(due_date))*5) ELSE fine END),0)
                 FROM issued_books''')
    total_fines = round(c.fetchone()[0], 2)
    conn.close()
    return {'total_books':total_books,'total_copies':total_copies,'available':available,
            'users':users,'active_issues':active_issues,'returned':returned,
            'overdue':overdue,'total_fines':total_fines}

def get_books_by_category():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) as cnt FROM books GROUP BY category ORDER BY cnt DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly_issues():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT strftime('%Y-%m', issue_date) as month, COUNT(*) as cnt
                 FROM issued_books GROUP BY month ORDER BY month DESC LIMIT 12''')
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def get_monthly_returns():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT strftime('%Y-%m', return_date) as month, COUNT(*) as cnt
                 FROM issued_books WHERE status='Returned' GROUP BY month ORDER BY month DESC LIMIT 12''')
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def get_most_borrowed_books():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT b.title, COUNT(ib.id) as cnt
                 FROM issued_books ib JOIN books b ON ib.book_id=b.id
                 GROUP BY ib.book_id ORDER BY cnt DESC LIMIT 10''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_issued_books(status_filter=''):
    conn = get_db()
    c = conn.cursor()
    q = '''SELECT ib.*,u.full_name,u.username,b.title as book_title
           FROM issued_books ib
           JOIN users u ON ib.user_id=u.id
           JOIN books b ON ib.book_id=b.id'''
    params = []
    if status_filter:
        q += " WHERE ib.status=?"
        params.append(status_filter)
    q += " ORDER BY ib.issue_date DESC"
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_overdue_books():
    conn = get_db()
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''SELECT ib.*,u.full_name,u.username,b.title as book_title
                 FROM issued_books ib
                 JOIN users u ON ib.user_id=u.id
                 JOIN books b ON ib.book_id=b.id
                 WHERE ib.status='Issued' AND ib.due_date<? ORDER BY ib.due_date ASC''', (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_active_borrowers():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT u.full_name,u.username,COUNT(ib.id) as cnt
                 FROM issued_books ib JOIN users u ON ib.user_id=u.id
                 GROUP BY ib.user_id ORDER BY cnt DESC LIMIT 10''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_registrations_monthly():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT strftime('%Y-%m', registration_date) as month, COUNT(*) as cnt
                 FROM users WHERE role='student' GROUP BY month ORDER BY month DESC LIMIT 12''')
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))
