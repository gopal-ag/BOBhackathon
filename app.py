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

def process_images(model_image_path, garment_image_path):
    with open(model_image_path, "rb") as model, open(garment_image_path, "rb") as garment:

        output = replicate.run(
            "viktorfa/oot_diffusion:9f8fa4956970dde99689af7488157a30aa152e23953526a605df1d77598343d7",
            input={
                "seed": 0,
                "steps": 20,
                "model_image": model,
                "garment_image": garment,
                "guidance_scale": 2
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
        output = process_images(model_image_path, garment_image_path)
        print (output)
        return render_template('index.html', model_image=model_image_path, garment_image=garment_image_path, output=output)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)