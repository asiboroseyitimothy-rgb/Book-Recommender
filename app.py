from flask import Flask, render_template, request, redirect, session, url_for
import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)
import os
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-for-local")

# Session config
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"

# ---------- LOAD BOOKS FROM EXCEL (single source) ----------
import os, pandas as pd

BOOKS_CSV = os.path.join(os.path.dirname(__file__), "data", "books.csv")

if os.path.exists(BOOKS_CSV):
    books_df = pd.read_csv(BOOKS_CSV)
else:
    books_df = pd.DataFrame(columns=['book_id','Title','Author','Link','Description','Genre'])

# Normalize column names and ensure book_id exists
books_df.columns = [str(c).strip() for c in books_df.columns]
if 'book_id' not in books_df.columns:
    books_df.insert(0, 'book_id', range(1, len(books_df) + 1))

books_list = books_df.to_dict(orient='records')


# ✅ Session configuration (add these two lines only once)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"


# Load users if file exists, otherwise create empty DataFrame
import os
if not os.path.exists('data/users.csv'):
    users_df = pd.DataFrame(columns=['user_id','username','password'])
    users_df.to_csv('data/users.csv', index=False)
else:
    users_df = pd.read_csv('data/users.csv')
import re  # ✅ Add this near the top of app.py (for regex password validation)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ Password strength validation
        if (len(password) < 8 or
            not re.search(r"[A-Z]", password) or
            not re.search(r"[a-z]", password) or
            not re.search(r"[0-9]", password) or
            not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
            error = "Password must have at least 8 characters, including one uppercase, one lowercase, one number, and one special character."
            return render_template('register.html', error=error)

        # ✅ Load users.csv
        users_df = pd.read_csv('data/users.csv')

        # ✅ Check if username already exists
        if username in users_df['username'].values:
            error = "Username already exists. Please choose another."
            return render_template('register.html', error=error)

        # ✅ Add new user
        new_id = len(users_df) + 1
        users_df.loc[len(users_df)] = [new_id, username, password]
        users_df.to_csv('data/users.csv', index=False)

        return render_template('success.html', username=username)

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users_df = pd.read_csv('data/users.csv')

        user_row = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if not user_row.empty:
            session['user_id'] = int(user_row.iloc[0]['user_id'])
            session['username'] = str(user_row.iloc[0]['username'])
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


# Load book data
books_df = pd.read_excel('books.xlsx')

# Optional: check column names to make sure
print(books_df.columns)
# ---------- HOME PAGE ----------
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Pass the preloaded books (from Excel)
    return render_template('index.html', books=books_list)

from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ---------- RECOMMENDATION LOGIC ----------
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@app.route('/recommend', methods=['GET','POST'])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Read books_df fresh to ensure consistent types (optional)
    # (If you used preloaded books_list above, you can use that instead)
    # books_df = pd.DataFrame(books_list)  # or re-read from Excel

    if request.method == 'POST':
        selected = request.form.getlist('book')  # checkbox values (book_id)
        if not selected:
            return render_template('recommend.html', rec_books=[], error="Please select at least one book.")

        selected_ids = [int(x) for x in selected]

        # Try collaborative approach if ratings DataFrame exists
        try:
            # ensure ratings variable exists in your app (ratings = pd.read_csv('data/ratings.csv'))
            user_item_matrix = ratings.pivot(index='user_id', columns='book_id', values='rating').fillna(0)
            new_user_vector = pd.Series(0, index=user_item_matrix.columns)
            for book_id in selected_ids:
                if book_id in new_user_vector.index:
                    new_user_vector[book_id] = 5
            temp_matrix = user_item_matrix.copy()
            temp_matrix.loc[999999] = new_user_vector
            sim = cosine_similarity(temp_matrix)
            new_user_sim = sim[-1][:-1]
            scores = np.dot(new_user_sim, user_item_matrix.values)
            for book_id in selected_ids:
                if book_id in user_item_matrix.columns:
                    idx = list(user_item_matrix.columns).index(book_id)
                    scores[idx] = -1
            recommended_indices = np.argsort(scores)[::-1][:10]
            recommended_ids = [user_item_matrix.columns[i] for i in recommended_indices]
        except Exception:
            # fallback: list top books by order (excluding selected)
            df_ids = [int(b['book_id']) for b in books_list]
            recommended_ids = [bid for bid in df_ids if bid not in selected_ids][:10]

        # Filter books_df to these IDs and convert to list of dicts
        recommended_books_df = books_df[books_df['book_id'].isin(recommended_ids)]
        rec_books_list = recommended_books_df.to_dict(orient='records')
        return render_template('recommend.html', rec_books=rec_books_list, error=None)

    # GET — show empty
    return render_template('recommend.html', rec_books=[], error=None)


# ---------- RUN APP ----------
if __name__ == '__main__':
    app.run(debug=True)
