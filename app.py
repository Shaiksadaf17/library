from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import re
import os

app = Flask(__name__)

app.secret_key = 'abcd2123445'
DATABASE = 'library-system.db'

# Helper function to get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # For dict-like access to rows
    return db

# Close the database connection when the app context is closed
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['role']
            mesage = 'Logged in successfully!'
            return redirect(url_for('dashboard'))
        else:
            mesage = 'Please enter correct email / password!'
    return render_template('login.html', mesage=mesage)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''

    if request.method == 'POST':
        first_name = request.form.get('first_name')  # Updated
        last_name = request.form.get('last_name')    # Updated
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if all fields are filled
        if not first_name or not last_name or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor = get_db().cursor()
            cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
            account = cursor.fetchone()

            # Validate email format
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Invalid email address!'
            elif account:
                message = 'Account already exists!'
            else:
                # Insert new user into the database
                cursor.execute('INSERT INTO user (first_name, last_name, email, password) VALUES (?, ?, ?, ?)', (first_name, last_name, email, password))
                get_db().commit()
                message = 'You have successfully registered!'

            cursor.close()  # Close cursor after operation

    return render_template('register.html', message=message)



@app.route("/users", methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        return render_template("users.html", users=users)
    return redirect(url_for('login'))

@app.route("/save_user", methods=['GET', 'POST'])
def save_user():
    msg = ''
    if 'loggedin' in session:
        db = get_db()
        cursor = db.cursor()
        if request.method == 'POST' and 'role' in request.form and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            role = request.form['role']
            action = request.form['action']

            if action == 'updateUser':
                userId = request.form['userid']
                cursor.execute('UPDATE user SET first_name = ?, last_name = ?, email = ?, role = ? WHERE id = ?', (first_name, last_name, email, role, userId))
                db.commit()
            else:
                password = request.form['password']
                cursor.execute('INSERT INTO user (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)', (first_name, last_name, email, password, role))
                db.commit()

            return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return redirect(url_for('users'))
    return redirect(url_for('login'))


@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE id = ?', (editUserId,))
        users = cursor.fetchall()
        conn.close()
        return render_template("edit_user.html", users=users)
    return redirect(url_for('login'))

@app.route("/view_user", methods=['GET', 'POST'])
def view_user():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE id = ?', (viewUserId,))
        user = cursor.fetchone()
        conn.close()
        return render_template("view_user.html", user=user)
    return redirect(url_for('login'))

@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    mesage = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userId = request.form['userid']
            if not password or not confirm_pass:
                mesage = 'Please fill out the form!'
            elif password != confirm_pass:
                mesage = 'Confirm password is not equal!'
            else:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('UPDATE user SET password = ? WHERE id = ?', (password, userId))
                conn.commit()
                conn.close()
                mesage = 'Password updated!'
        elif request.method == 'POST':
            mesage = 'Please fill out the form!'
        return render_template("password_change.html", mesage=mesage, changePassUserId=changePassUserId)
    return redirect(url_for('login'))

@app.route("/delete_user", methods=['GET'])
def delete_user():
    if 'loggedin' in session:
        deleteUserId = request.args.get('userid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user WHERE id = ?', (deleteUserId,))
        conn.commit()
        conn.close()
        return redirect(url_for('users'))
    return redirect(url_for('login'))


# Delete book
@app.route("/delete_book", methods=['GET'])
def delete_book():
    if 'loggedin' in session:
        deleteBookId = request.args.get('bookid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM book WHERE bookid = ?', (deleteBookId,))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    return redirect(url_for('login'))
@app.route("/books", methods=['GET', 'POST'])
def books():
    if 'loggedin' in session:
        conn = get_db()  # Use the SQLite connection
        cursor = conn.cursor()
        
        # Fetching books with relevant joins
        cursor.execute("""
            SELECT book.bookid, book.picture, book.name, book.status, 
                   book.isbn, book.no_of_copy, book.updated_on, 
                   author.name as author_name, 
                   category.name AS category_name, 
                   rack.name AS rack_name, 
                   publisher.name AS publisher_name 
            FROM book 
            LEFT JOIN author ON author.authorid = book.authorid 
            LEFT JOIN category ON category.categoryid = book.categoryid 
            LEFT JOIN rack ON rack.rackid = book.rackid 
            LEFT JOIN publisher ON publisher.publisherid = book.publisherid
        """)
        books = cursor.fetchall()

        # Fetching authors
        cursor.execute("SELECT authorid, name FROM author")
        authors = cursor.fetchall()

        # Fetching publishers
        cursor.execute("SELECT publisherid, name FROM publisher")
        publishers = cursor.fetchall()

        # Fetching categories
        cursor.execute("SELECT categoryid, name FROM category")
        categories = cursor.fetchall()

        # Fetching racks
        cursor.execute("SELECT rackid, name FROM rack")
        racks = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return render_template("books.html", books=books, authors=authors, publishers=publishers, categories=categories, racks=racks)

    return redirect(url_for('login'))


# Manage issue book
@app.route("/list_issue_book", methods=['GET', 'POST'])
def list_issue_book():
    if 'loggedin' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid")
        issue_books = cursor.fetchall()

        cursor.execute("SELECT bookid, name FROM book")
        books = cursor.fetchall()

        cursor.execute("SELECT id, first_name, last_name FROM user")
        users = cursor.fetchall()

        conn.close()
        return render_template("issue_book.html", issue_books=issue_books, books=books, users=users)
    return redirect(url_for('login'))

# Save issue book

@app.route("/save_book", methods =['GET', 'POST'])
def save_book():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT book.bookid, book.picture, book.name, book.status, book.isbn, book.no_of_copy, book.updated_on, author.name as author_name, category.name AS category_name, rack.name As rack_name, publisher.name AS publisher_name FROM book LEFT JOIN author ON author.authorid = book.authorid LEFT JOIN category ON category.categoryid = book.categoryid LEFT JOIN rack ON rack.rackid = book.rackid LEFT JOIN publisher ON publisher.publisherid = book.publisherid")
        books = cursor.fetchall()
        if request.method == 'POST' and 'name' in request.form and 'author' in request.form and 'publisher' in request.form and 'category' in request.form and 'rack' in request.form :
            bookName = request.form['name']
            isbn = request.form['isbn']
            no_of_copy = request.form['no_of_copy']
            author = request.form['author']
            publisher = request.form['publisher']
            category = request.form['category']
            rack = request.form['rack']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateBook':
                bookId = request.form['bookid']
                cursor.execute('UPDATE book SET name= %s, status= %s, isbn= %s, no_of_copy= %s, categoryid= %s, authorid=%s, rackid= %s, publisherid= %s WHERE bookid = %s', (bookName, status, isbn, no_of_copy, category, author, rack, publisher, (bookId, ), ))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO book (`name`, `status`, `isbn`, `no_of_copy`, `categoryid`, `authorid`, `rackid`, `publisherid`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (bookName, status, isbn, no_of_copy, category
    , author, rack, publisher))
                mysql.connection.commit()
            return redirect(url_for('books'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("books.html", msg = msg, books = books)
    return redirect(url_for('login'))


@app.route("/save_issue_book", methods=['GET', 'POST'])
def save_issue_book():
    if 'loggedin' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid")
        issue_books = cursor.fetchall()

        if request.method == 'POST' and 'book' in request.form and 'users' in request.form and 'expected_return_date' in request.form and 'return_date' in request.form and 'status' in request.form:
            bookId = request.form['book']
            userId = request.form['users']
            expected_return_date = request.form['expected_return_date']
            return_date = request.form['return_date']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateIssueBook':
                issuebookid = request.form['issueBookId']
                cursor.execute('UPDATE issued_book SET bookid = ?, userid = ?, expected_return_date = ?, return_date_time = ?, status = ? WHERE issuebookid = ?', (bookId, userId, expected_return_date, return_date, status, issuebookid))
            else:
                cursor.execute('INSERT INTO issued_book (bookid, userid, expected_return_date, return_date_time, status) VALUES (?, ?, ?, ?, ?)', (bookId, userId, expected_return_date, return_date, status))
            conn.commit()
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        conn.close()
        return redirect(url_for('list_issue_book'))
    return redirect(url_for('login'))

# Edit issue book
@app.route("/edit_issue_book", methods=['GET', 'POST'])
def edit_issue_book():
    msg = ''
    if 'loggedin' in session:
        issuebookid = request.args.get('issuebookid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT issued_book.issuebookid, issued_book.issue_date_time, issued_book.expected_return_date, issued_book.return_date_time, issued_book.bookid, issued_book.userid, issued_book.status, book.name AS book_name, book.isbn, user.first_name, user.last_name FROM issued_book LEFT JOIN book ON book.bookid = issued_book.bookid LEFT JOIN user ON user.id = issued_book.userid WHERE issued_book.issuebookid = ?', (issuebookid,))
        issue_books = cursor.fetchall()

        cursor.execute("SELECT bookid, name FROM book")
        books = cursor.fetchall()

        cursor.execute("SELECT id, first_name, last_name FROM user")
        users = cursor.fetchall()

        conn.close()
        return render_template("edit_issue_book.html", issue_books=issue_books, books=books, users=users)
    return redirect(url_for('login'))

# Delete issue book
@app.route("/delete_issue_book", methods=['GET'])
def delete_issue_book():
    if 'loggedin' in session:
        issuebookid = request.args.get('issuebookid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM issued_book WHERE issuebookid = ?', (issuebookid,))
        conn.commit()
        conn.close()
        return redirect(url_for('list_issue_book'))
    return redirect(url_for('login'))



# Manage Category
@app.route("/category", methods=['GET', 'POST'])
def category():
    if 'loggedin' in session:
        conn = get_db()
        categories = conn.execute("SELECT categoryid, name, status FROM category").fetchall()
        conn.close()
        return render_template("category.html", categories=categories, addCategoryForm=0)
    return redirect(url_for('login'))

@app.route("/saveCategory", methods=['POST'])
def saveCategory():
    if 'loggedin' in session:
        conn = get_db()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateCategory':
                categoryId = request.form['categoryid']
                conn.execute('UPDATE category SET name = ?, status = ? WHERE categoryid = ?', (name, status, categoryId))
                conn.commit()
            else:
                conn.execute('INSERT INTO category (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('category'))
        else:
            msg = 'Please fill out the form !'
            conn.close()
            return redirect(url_for('category'))

    return redirect(url_for('login'))

@app.route("/editCategory", methods=['GET', 'POST'])
def editCategory():
    if 'loggedin' in session:
        categoryid = request.args.get('categoryid')
        conn = get_db()
        categories = conn.execute('SELECT categoryid, name, status FROM category WHERE categoryid = ?', (categoryid,)).fetchall()
        conn.close()
        return render_template("edit_category.html", categories=categories)
    return redirect(url_for('login'))

@app.route("/delete_category", methods=['GET'])
def delete_category():
    if 'loggedin' in session:
        categoryid = request.args.get('categoryid')
        conn = get_db()
        conn.execute('DELETE FROM category WHERE categoryid = ?', (categoryid,))
        conn.commit()
        conn.close()
        return redirect(url_for('category'))
    return redirect(url_for('login'))

# Manage Author
@app.route("/author", methods=['GET', 'POST'])
def author():
    if 'loggedin' in session:
        conn = get_db()
        authors = conn.execute("SELECT authorid, name, status FROM author").fetchall()
        conn.close()
        return render_template("author.html", authors=authors)
    return redirect(url_for('login'))

@app.route("/saveAuthor", methods=['POST'])
def saveAuthor():
    if 'loggedin' in session:
        conn = get_db()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updateAuthor':
                authorId = request.form['authorid']
                conn.execute('UPDATE author SET name = ?, status = ? WHERE authorid = ?', (name, status, authorId))
                conn.commit()
            else:
                conn.execute('INSERT INTO author (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('author'))
        else:
            msg = 'Please fill out the form !'
            conn.close()
            return redirect(url_for('author'))

    return redirect(url_for('login'))

@app.route("/editAuthor", methods=['GET', 'POST'])
def editAuthor():
    if 'loggedin' in session:
        authorid = request.args.get('authorid')
        conn = get_db()
        authors = conn.execute('SELECT authorid, name, status FROM author WHERE authorid = ?', (authorid,)).fetchall()
        conn.close()
        return render_template("edit_author.html", authors=authors)
    return redirect(url_for('login'))

@app.route("/delete_author", methods=['GET'])
def delete_author():
    if 'loggedin' in session:
        authorid = request.args.get('authorid')
        conn = get_db()
        conn.execute('DELETE FROM author WHERE authorid = ?', (authorid,))
        conn.commit()
        conn.close()
        return redirect(url_for('author'))
    return redirect(url_for('login'))

# Manage publishers
@app.route("/publisher", methods=['GET', 'POST'])
def publisher():
    if 'loggedin' in session:
        conn = get_db()
        publishers = conn.execute("SELECT publisherid, name, status FROM publisher").fetchall()
        conn.close()
        return render_template("publisher.html", publishers=publishers)
    return redirect(url_for('login'))

@app.route("/savePublisher", methods=['POST'])
def savePublisher():
    if 'loggedin' in session:
        conn = get_db()

        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            if action == 'updatePublisher':
                publisherid = request.form['publisherid']
                conn.execute('UPDATE publisher SET name = ?, status = ? WHERE publisherid = ?', (name, status, publisherid))
                conn.commit()
            else:
                conn.execute('INSERT INTO publisher (name, status) VALUES (?, ?)', (name, status))
                conn.commit()
            conn.close()
            return redirect(url_for('publisher'))
        else:
            msg = 'Please fill out the form !'
            conn.close()
            return redirect(url_for('publisher'))

    return redirect(url_for('login'))

@app.route("/editPublisher", methods=['GET', 'POST'])
def editPublisher():
    if 'loggedin' in session:
        publisherid = request.args.get('publisherid')
        conn = get_db()
        publishers = conn.execute('SELECT publisherid, name, status FROM publisher WHERE publisherid = ?', (publisherid,)).fetchall()
        conn.close()
        return render_template("edit_publisher.html", publishers=publishers)
    return redirect(url_for('login'))

@app.route("/delete_publisher", methods=['GET'])
def delete_publisher():
    if 'loggedin' in session:
        publisherid = request.args.get('publisherid')
        conn = get_db()
        conn.execute('DELETE FROM publisher WHERE publisherid = ?', (publisherid,))
        conn.commit()
        conn.close()
        return redirect(url_for('publisher'))
    return redirect(url_for('login'))

# Manage Rack
@app.route("/rack", methods=['GET', 'POST'])
def rack():
    if 'loggedin' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT rackid, name, status FROM rack")
        racks = cursor.fetchall()
        conn.close()
        return render_template("rack.html", racks=racks)
    return redirect(url_for('login'))

@app.route("/saveRack", methods=['GET', 'POST'])
def saveRack():
    if 'loggedin' in session:
        if request.method == 'POST' and 'name' in request.form and 'status' in request.form:
            name = request.form['name']
            status = request.form['status']
            action = request.form['action']

            conn = get_db()
            cursor = conn.cursor()

            if action == 'updateRack':
                rackid = request.form['rackid']
                cursor.execute('UPDATE rack SET name = ?, status = ? WHERE rackid = ?', (name, status, rackid))
                conn.commit()
            else:
                cursor.execute('INSERT INTO rack (name, status) VALUES (?, ?)', (name, status))
                conn.commit()

            conn.close()
            return redirect(url_for('rack'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return redirect(url_for('rack'))

    return redirect(url_for('login'))

@app.route("/editRack", methods=['GET', 'POST'])
def editRack():
    if 'loggedin' in session:
        rackid = request.args.get('rackid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT rackid, name, status FROM rack WHERE rackid = ?', (rackid,))
        racks = cursor.fetchall()
        conn.close()
        return render_template("edit_rack.html", racks=racks)
    return redirect(url_for('login'))

@app.route("/delete_rack", methods=['GET'])
def delete_rack():
    if 'loggedin' in session:
        rackid = request.args.get('rackid')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rack WHERE rackid = ?', (rackid,))
        conn.commit()
        conn.close()
        return redirect(url_for('rack'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()

