from flask import Flask, render_template, request
import requests
import sqlite3

app = Flask(__name__)

API_KEY = '53f368ce8cca117a6757854bed3e5b2a' 
BASE_URL = 'https://api.themoviedb.org/3'
IMG_URL = 'https://image.tmdb.org/t/p/w500'

# --- Database Banane Ka Code ---
def init_db():
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            user_name TEXT,
            review_text TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db() # App start hote hi database ban jayega
# -------------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    movies = []
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={search_query}"
    else:
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])
        
    return render_template('index.html', movies=movies, img_url=IMG_URL)

# GET (page dikhana) aur POST (review save karna) dono allow kiya
@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    
    # Agar user ne form submit kiya hai
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        review_text = request.form.get('review_text')
        
        # Review ko Database mein Save karo
        conn = sqlite3.connect('reviews.db')
        c = conn.cursor()
        c.execute('INSERT INTO reviews (movie_id, user_name, review_text) VALUES (?, ?, ?)', (movie_id, user_name, review_text))
        conn.commit()
        conn.close()

    # Movie Details Fetch
    detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}"
    movie_response = requests.get(detail_url).json()
    
    # Cast Fetch
    cast_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}"
    cast_response = requests.get(cast_url).json()
    cast = cast_response.get('cast', [])[:6]
    
    # Us specific movie ke purane reviews database se nikalna
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute('SELECT user_name, review_text FROM reviews WHERE movie_id = ?', (movie_id,))
    saved_reviews = c.fetchall()
    conn.close()
    
    return render_template('movie_detail.html', movie=movie_response, cast=cast, img_url=IMG_URL, reviews=saved_reviews)

if __name__ == '__main__':
    app.run(debug=True)