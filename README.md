# MyBookAdda - A Peer-to-Peer Book Exchange Platform

A web-based platform where users can exchange books with one another. Built using **Flask**, **MySQL**, and **Tailwind CSS**, this system enables users to list books, request books from others, and manage borrow approvals — all within a points-based economy.

---

## Features

- User registration & login (with hashed passwords & sessions)
- List books you want to lend
- Browse books listed by other users
- Request to borrow books
- Approve or reject incoming requests for your books
- Point system to manage fair exchanges
- Book cover images via URL
- Clean and responsive UI using Tailwind CSS

---

## Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, Jinja2, Tailwind CSS
- **Database:** MySQL (mysql-connector)
- **Authentication:** Session-based login with hashed passwords

---

## Database Schema

### users
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    points INT DEFAULT 10
);
```
### books
```sql
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    description TEXT,
    image_url TEXT,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```
### requests
```sql
CREATE TABLE requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    borrower_id INT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    request_date DATE,
    decision_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (borrower_id) REFERENCES users(id)
);
```

---

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/book-exchange-platform.git
   cd book-exchange-platform
   ```
   
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
3. Install dependencies
   ```bash
   pip install -r requirements.txt
    ```
   
4. Setup MySQL Database
   - Create a database called book_exchange
   - Run the schema.sql script to create required tables
  
5. Configure DB credentials in db_config.py
   ```sql
   db_config = {
    'host': 'localhost',
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'database': 'book_exchange'
    };
   ```

6. Run the app
   ```bash
   python app.py
   ```

7. Visit **http://localhost:5000** in your browser

---

## Security

- Passwords are hashed using werkzeug.security
- Session-based authentication ensures user security
- Add CSRF protection and input validation for production use

---

## Author

**Veer Jain**  
  Email: [veertiarra123@email.com](mailto:veertiarra123@email.com)  
  [LinkedIn](https://www.linkedin.com/in/veerjain6805/)  
  [GitHub](https://github.com/vjn6805)






