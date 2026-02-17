import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from cloudant.client import Cloudant
from PIL import Image # Keeping this just in case, though screenshot uses keras.preprocessing
from dotenv import load_dotenv

load_dotenv() # Load environment variables

app = Flask(__name__)
app.secret_key = "some_super_secret_key" # Change this for production
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



# --- Database Connection ---
# Authenticate using an IAM API key
USERNAME = os.getenv('CLOUDANT_USERNAME')
API_KEY = os.getenv('CLOUDANT_API_KEY')

try:
    client = Cloudant.iam(USERNAME, API_KEY, connect=True)
    # Create or get the database
    if 'my_database' in client:
        my_database = client['my_database']
    else:
        my_database = client.create_database('my_database')
    print("Database connected successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")
    my_database = None

# --- Model Loading Section ---
MODEL_PATH = os.path.join('model', 'Updated-Xception-diabetic-retinopathy.h5')

def load_my_model():
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}...")
        try:
            model = load_model(MODEL_PATH)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    else:
        print(f"Model not found at {MODEL_PATH}. Prediction will not work.")
        return None

model = load_my_model()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form['username']
        password = request.form['password']
        
        if my_database is not None:
            # Check if user exists (Username OR Email) AND Password matches
            selector = {
                '$and': [
                    {'$or': [{'username': {'$eq': user_input}}, {'email': {'$eq': user_input}}]},
                    {'password': {'$eq': password}}
                ]
            }
            docs = my_database.get_query_result(selector)
            user_exists = False
            found_username = None
            for doc in docs:
                user_exists = True
                found_username = doc.get('username')
                break
            
            if user_exists:
                session['user'] = found_username
                return redirect(url_for('prediction')) # Redirect to prediction after login
            else:
                flash('Invalid credentials')
        else:
             # Fallback for demo without DB
            if (user_input == "admin" or user_input == "admin@example.com") and password == "admin":
                 session['user'] = "admin"
                 return redirect(url_for('prediction'))
            flash('Database not connected. Use admin/admin for demo.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if my_database is not None:
            # Check if user already exists
            selector = {'username': {'$eq': username}}
            docs = my_database.get_query_result(selector)
            user_exists = False
            for doc in docs:
                user_exists = True
                break

            if user_exists:
                flash('Username already exists')
            else:
                data = {
                    'username': username,
                    'email': email,
                    'password': password
                }
                my_database.create_document(data)
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
        else:
            flash('Database not connected. Registration simulation: Success!')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath, 'uploads', filename)
            file.save(filepath)
            
            if model:
                try:
                    img = image.load_img(filepath, target_size=(299, 299))
                    x = image.img_to_array(img)
                    x = np.expand_dims(x, axis=0)
                    img_data = preprocess_input(x)
                    prediction_index = np.argmax(model.predict(img_data), axis=1)
                    
                    index = ['No Diabetic Retinopathy', 'Mild DR', 'Moderate DR', 'Severe DR', 'Proliferative DR']
                    result = str(index[prediction_index[0]])
                except Exception as e:
                    result = f"Error during prediction: {str(e)}"
            else:
                result = "Model not loaded. Please ensure the .h5 file is in the 'model' directory."
            
            return render_template('prediction.html', prediction=result, image_file=filename)

    return render_template('prediction.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)
