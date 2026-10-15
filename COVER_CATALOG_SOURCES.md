# Book cover mapping and sources

This file documents the known cover assignments in the LibraryMS sample catalog. Existing supplied image files are used only for books whose title/author are readable on the front cover; other titles use a book-specific catalog image URL or the guarded runtime lookup.

## Local cover images (included in this ZIP)

| Catalog title | Author | Image file |
|---|---|---|
| HTML and CSS | Jon Duckett | `static/books/b2.jpg` |
| Head First Java | Kathy Sierra | `static/books/b3.jpg` |
| Software Engineering | Ian Sommerville | `static/books/b4.jpg` |
| Python for Data Analysis | Wes McKinney | `static/books/b5.jpg` |
| Fluent Python | Luciano Ramalho | `static/books/b6.jpg` |
| Designing Data-Intensive Applications | Martin Kleppmann | `static/books/b7.jpg` |
| Refactoring: Improving the Design of Existing Code | Martin Fowler | `static/books/b8.jpg` |
| Pattern Recognition and Machine Learning | Christopher M. Bishop | `static/books/b9.jpg` |
| Grokking Algorithms: An Illustrated Guide for Programmers and Other Curious People | Aditya Y. Bhargava | `static/books/b10.jpg` |
| Learning SQL: Generate, Manipulate, and Retrieve Data (3rd edition) | Alan Beaulieu | `static/books/b11.jpg` |
| Computer Networking: A Top-Down Approach (8th Global edition) | James F. Kurose, Keith W. Ross | `static/books/b12.jpg` |
| Modern Operating Systems (4th edition) | Andrew S. Tanenbaum, Herbert Bos | `static/books/b13.jpg` |
| Eloquent JavaScript: A Modern Introduction to Programming (3rd edition) | Marijn Haverbeke | `static/books/b14.jpg` |
| Artificial Intelligence: Foundations of Computational Agents | David L. Poole, Alan K. Mackworth | `static/books/b15.jpg` |
| Don't Make Me Think, Revisited | Steve Krug | `static/books/b16.jpg` |
| You Don't Know JS Yet: Get Started | Kyle Simpson | `static/books/b17.jpg` |

## Online cover sources already saved in the database

Online covers remain URLs so the app can use catalog-hosted artwork without bundling duplicate files. The cover lookup checks the title and author, preferring exact ISBN matches when an ISBN is available.

| Book | Source record |
|---|---|
| Python Crash Course | [Google Books](https://books.google.com/books?id=BkCQEAAAQBAJ) |
| Automate the Boring Stuff with Python | [Google Books](https://books.google.com/books?id=UEu0CAAAQBAJ) |
| Artificial Intelligence: A Modern Approach (4th edition) | [Google Books](https://books.google.com/books?id=koFptAEACAAJ) |
| Artificial Intelligence with Python — Prateek Joshi | [Packt publisher page](https://www.packtpub.com/en-us/product/artificial-intelligence-with-python-9781786464392) |
| Big Data: A Revolution That Will Transform How We Live, Work, and Think | [Edition/cover record](https://books.google.com/books?vid=ISBN9780544002692) |
| AI Engineering: Building Applications with Foundation Models | [Google Books](https://books.google.com/books?id=YLbT0AEACAAJ) |
| Designing Machine Learning Systems | [Google Books](https://books.google.com/books?id=BAy_zgEACAAJ) |
| Natural Language Processing with Python | [Google Books](https://books.google.com/books?id=KkKbAgAAQBAJ) |
| Data Science for Business | [Google Books](https://books.google.com/books?id=_1b4nAEACAAJ) |
| The Hundred-Page Machine Learning Book | [Google Books](https://books.google.com/books?id=ZF3KwQEACAAJ) |
| Practical Statistics for Data Scientists (2nd edition) | [Google Books](https://books.google.com/books?id=k2XcDwAAQBAJ) |

## How unmatched books behave

A book without a saved cover is searched in Google Books first, then Open Library. Candidates with weak title/author similarity are rejected. If neither service finds a valid image, the app leaves its placeholder visible; administrators can upload the correct front cover to `static/books/uploads/` and save it on that book.
