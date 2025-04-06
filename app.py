from flask import Flask, render_template, request, redirect, session, url_for, flash, get_flashed_messages
from db_config import get_db_connection
from utils.auth_helpers import hash_password,check_password

app=Flask(__name__)
app.secret_key = 'topsecret123'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=hash_password(request.form['password'])
        
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO Users (name, email, password_hash, points) VALUES (%s, %s, %s, %s)",
                       (username, email, password, 50))  # default 50 points
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/login')
    
    return render_template('signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password_input=request.form['password']
        
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password(password_input,user['password_hash']):
            session['user_id']=user['user_id']
            session['username']=user['name']
            return redirect('/dashboard')
        else:
            return "Invalid credentials", 401
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    username=session.get('username')
    return render_template('dashboard.html',username=username)


@app.route('/list-book', methods=['GET', 'POST'])
def list_book():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form.get('description')  # optional
        book_condition = request.form['condition']
        points = int(request.form['points'])
        image_url = request.form.get('image_url')  # optional
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Books (owner_id, title, author, description, book_condition, points, available, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, title, author, description, book_condition, points, 1, image_url))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Book listed successfully!")
        return redirect('/dashboard')

    return render_template('list_book.html')

@app.route('/my-books')
def my_books():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Books WHERE owner_id = %s ORDER BY book_id DESC", (user_id,))
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('my_books.html', books=books)


@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Books WHERE book_id = %s AND owner_id = %s", (book_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Book deleted successfully!')
    return redirect('/my-books')

@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Books WHERE book_id = %s AND owner_id = %s", (book_id, user_id))
    book = cursor.fetchone()

    if not book:
        cursor.close()
        conn.close()
        flash("Book not found or unauthorized access.")
        return redirect('/my-books')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form.get('description')
        condition = request.form['condition']
        points = int(request.form['points'])
        image_url = request.form.get('image_url')
        available = 1 if request.form.get('available') == 'on' else 0

        cursor.execute("""
            UPDATE Books
            SET title = %s, author = %s, description = %s, book_condition = %s,
                points = %s, available = %s, image_url = %s
            WHERE book_id = %s AND owner_id = %s
        """, (title, author, description, condition, points, available, image_url, book_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Book updated successfully!')
        return redirect('/my-books')

    cursor.close()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/browse-books')
def browse_books():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT B.*, U.name AS owner_name
        FROM books B
        JOIN users U ON B.owner_id = U.user_id
        WHERE B.available = 1 AND B.owner_id != %s
        ORDER BY B.book_id DESC
    """, (user_id,))

    books = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('browse_books.html', books=books)



from datetime import datetime
@app.route('/request-book/<int:book_id>', methods=['POST'])
def request_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')

    borrower_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if request already exists
    cursor.execute("""
        SELECT * FROM requests
        WHERE book_id = %s AND borrower_id = %s AND status = 'pending'
    """, (book_id, borrower_id))
    existing_request = cursor.fetchone()

    if existing_request:
        flash("You've already requested this book.", "warning")
    else:
        cursor.execute("""
            INSERT INTO requests (book_id, borrower_id, status, request_date)
            VALUES (%s, %s, 'pending', %s)
        """, (book_id, borrower_id, datetime.now()))
        conn.commit()
        flash("Book requested successfully!", "success")

    cursor.close()
    conn.close()
    return redirect('/browse-books')

@app.route('/requests', methods=['GET', 'POST'])
def handle_requests():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        action = request.form['action']
        request_id = request.form['request_id']
        cursor.execute("""
            SELECT R.*, B.points, B.owner_id, B.book_id, U.points as borrower_points
            FROM requests R
            JOIN books B ON R.book_id = B.book_id
            JOIN users U ON R.borrower_id = U.user_id
            WHERE R.request_id = %s
        """, (request_id,))
        req = cursor.fetchone()

        if req:
            if action == 'approve':
                if req['borrower_points'] >= req['points']:
                    cursor.execute("UPDATE requests SET status='approved', decision_date=NOW() WHERE request_id = %s", (request_id,))
                    cursor.execute("UPDATE books SET available=0 WHERE book_id = %s", (req['book_id'],))
                    cursor.execute("UPDATE users SET points = points - %s WHERE user_id = %s", (req['points'], req['borrower_id']))
                    cursor.execute("UPDATE users SET points = points + %s WHERE user_id = %s", (req['points'], req['owner_id']))
                    flash("Request approved and points transferred ✅", "success")
                else:
                    flash("Borrower doesn't have enough points ❌", "danger")
            elif action == 'reject':
                cursor.execute("UPDATE requests SET status='rejected', decision_date=NOW() WHERE request_id = %s", (request_id,))
                flash("Request rejected ❌", "info")
            conn.commit()

    cursor.execute("""
        SELECT R.request_id, R.status, R.request_date, R.decision_date,
               B.title, B.book_id, U.name as borrower_name, B.points
        FROM requests R
        JOIN books B ON R.book_id = B.book_id
        JOIN users U ON R.borrower_id = U.user_id
        WHERE B.owner_id = %s
        ORDER BY R.request_date DESC
    """, (user_id,))
    owner_requests = cursor.fetchall()

    cursor.execute("""
        SELECT R.status, R.request_date, R.decision_date,
               B.title, B.book_id, U.name as owner_name, B.points
        FROM requests R
        JOIN books B ON R.book_id = B.book_id
        JOIN users U ON B.owner_id = U.user_id
        WHERE R.borrower_id = %s
        ORDER BY R.request_date DESC
    """, (user_id,))
    my_requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('requests.html', owner_requests=owner_requests, my_requests=my_requests)



if __name__ == '__main__':
    app.run(debug=True)