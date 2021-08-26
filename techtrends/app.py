import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Global Database Connection Counter
db_conn_counter = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_conn_counter
    try:
        connection = sqlite3.connect('database.db')
        print(connection)
        connection.row_factory = sqlite3.Row
        connection.cursor()
        db_conn_counter += 1
        return connection
    except:
        return False

# Function to check the connection
def check_connection(conn):
    try:
        conn.cursor()
        return True
    except Exception as ex:
        return False

# Function to check if posts table exiists
def posts_table_exists(conn):
    c = conn.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='posts' ''')
    if c.fetchone()[0]==1 : 
        return True
    else:
        return False


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define healz endpoint for checking the app health
@app.route('/healz')
def health():
    default_status_text = "OK - healthy"
    default_status = 200
    connection = get_db_connection()
    # To check the failure in case connection to database closes
    # connection.close()

    # Check if the connection is good  -- Standout
    if not check_connection(connection) or not posts_table_exists(connection):
        default_status_text = "ERROR - unhealthy"
        default_status = 500

    response = app.response_class(
        response=json.dumps({"result":default_status_text}),
        status=default_status,
        mimetype='application/json'
    )

    return response

# Define the metrics endpoint

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
