# Validation report — LibraryMS cover/catalog update

## Checks completed

- Python syntax compilation passed for `app.py`, `database.py`, `auth.py`, and `wsgi.py`.
- JavaScript syntax validation passed for `static/js/book_covers.js`.
- SQLite `PRAGMA integrity_check` returned `ok`.
- Catalog migration is idempotent: a second migration run leaves the catalog at 58 books.
- The packaged catalog has 27 saved cover assignments: 16 local image files included in the project and 11 HTTPS cover URLs. All referenced local cover files exist. The other 31 books use ISBN/title/author-checked runtime lookup and retain a placeholder when no credible image is returned.
- No duplicate non-null ISBN values were found in the packaged catalog.
- Temporary-database tests passed for borrowing, duplicate-borrow prevention, the three-active-book limit, restoring availability on return, blocking a quantity reduction below current loans, correct availability after quantity changes, and refusing deletion when borrowing history references a book.

## Environment limitation

The inspection container did not have Flask/Werkzeug installed and could not reach external image hosts, so an end-to-end Flask browser session and live HTTP image fetch could not be executed here. Install the project's requirements and run the application locally to check provider availability. The uploaded-cover flow and catalog routes are present in the code; live image availability depends on the provider and the user's internet connection.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`. Set a strong `SECRET_KEY` environment variable before deployment. See `README.md` and `COVER_CATALOG_SOURCES.md` for more details.
