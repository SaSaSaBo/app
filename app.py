from flask import Flask, request, render_template
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Klasör yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def enhance_image(image):
    # Basit bir iyileştirme işlemi
    enhanced = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    return enhanced

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Dosya seçilmedi'
        
        file = request.files['file']
        filter_type = request.form.get('filter_type', 'sharpen')
        
        if file.filename == '':
            return 'Dosya seçilmedi'

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Görüntüyü işle
            original_image = cv2.imread(filepath)
            
            # Filtre seçimi
            if filter_type == 'sharpen':
                # Keskinleştirme filtresi
                kernel = np.array([[-1,-1,-1],
                                 [-1, 9,-1],
                                 [-1,-1,-1]])
                processed_image = cv2.filter2D(original_image, -1, kernel)
                prefix = 'sharpen_'
            elif filter_type == 'gaussian':
                # Gaussian filtresi
                processed_image = cv2.GaussianBlur(original_image, (5,5), 0)
                prefix = 'gaussian_'
            elif filter_type == 'median':
                # Median filtresi
                processed_image = cv2.medianBlur(original_image, 5)
                prefix = 'median_'
            elif filter_type == 'sharpen_median':
                # Önce median filtre uygula
                median_image = cv2.medianBlur(original_image, 5)
                # Sonra keskinleştirme filtresi
                kernel = np.array([[-1,-1,-1],
                                 [-1, 9,-1],
                                 [-1,-1,-1]])
                processed_image = cv2.filter2D(median_image, -1, kernel)
                prefix = 'sharpen_median_'
            
            # İşlenmiş görüntüyü kaydet
            output_filename = prefix + filename
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            cv2.imwrite(output_filepath, processed_image)
            
            return render_template('result.html', 
                                original=filename,
                                enhanced=output_filename)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)