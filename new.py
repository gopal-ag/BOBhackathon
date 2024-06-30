from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import replicate

app = Flask(__name__)

#export REPLICATE_API_TOKEN=r8_OcWQFHzj3thmE8jV3bkf2XKITYbIIQs0lIuLU
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_images(model_image_path, garment_image_path, category):
    with open(model_image_path, "rb") as model, open(garment_image_path, "rb") as garment:
        output = replicate.run(
            "k-amir/ootdifussiondc:3d375cf5aa238751a8e4342eda56a11f960964bb1023f8610ee052b5fbdc69ea",
            input={
                "category": category,
                "vton_img": model,
                "garm_img": garment,
            }
        )
    return output

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'model_image' not in request.files or 'garment_image' not in request.files:
            return render_template('index.html', error='No file part')
        
        model_image = request.files['model_image']
        garment_image = request.files['garment_image']
        category = request.form['category']

        if model_image.filename == '' or garment_image.filename == '':
            return render_template('index.html', error='No selected file')

        if not allowed_file(model_image.filename) or not allowed_file(garment_image.filename):
            return render_template('index.html', error='File type not allowed')

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        model_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(model_image.filename))
        garment_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(garment_image.filename))
        model_image.save(model_image_path)
        garment_image.save(garment_image_path)
        output = process_images(model_image_path, garment_image_path, category)
        return render_template('index.html', model_image=model_image_path, garment_image=garment_image_path, output=output)

    return render_template('index1.html')

if __name__ == '__main__':
    app.run(debug=True)
