from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/react_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

UPLOAD_FOLDER = r'C:\Users\SPSOFT\Desktop\React\full-app\flask\public\static\images'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define Image class for SQLAlchemy
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)

# Home route to render the upload form
@app.route('/file_count')
def index():
    # Fetch total files count
    file_count = len(os.listdir(app.config['UPLOAD_FOLDER']))
    return jsonify("File Count : "+str(file_count))

# Route to handle image upload
@app.route('/', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('file')
    category = request.form.get('category')
    flag = request.form.get('flag')
    
    for file in uploaded_files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename.replace(' ', '_'))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename = secure_filename(file.filename)
        # Creating Image object and saving it to the database
        new_image = Image(filename=filename, category=category, flag=flag, path="/static/images/"+filename)
        db.session.add(new_image)
        db.session.commit()
        
    return redirect(url_for('index'))


@app.route('/get_all_paths_and_flags')
def get_all_paths_and_flags():
    paths_and_flags = [{'id':image.id,'filename': image.filename,'path': image.path, 'flag': image.flag} for image in Image.query.all()]
    # Print for debugging
    return jsonify(paths_and_flags)

@app.route('/get_image_paths')
def get_all_paths():
    paths = [{'flag': image.flag,'path': image.path} for image in Image.query.all()]
    # Print for debugging
    return jsonify(paths)


@app.route('/update_flag', methods=['POST'])
def update_flag():
    data = request.json
    image_path = data.get('imagePath')
    new_flag_value = data.get('newFlagValue')

    try:
        # Find the image by its path
        image = Image.query.filter_by(path=image_path).first()
        if image:
            # Update the flag value
            image.flag = new_flag_value
            db.session.commit()
            return jsonify({'message': 'Flag updated successfully'})
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
