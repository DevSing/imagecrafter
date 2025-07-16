import os
import uuid
import img2pdf
import fitz  # PyMuPDF
import zipfile
from PIL import Image
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, session, send_from_directory
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import SiteStat

tools_bp = Blueprint('tools', __name__)

UPLOAD_FOLDER = 'static/temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Guest usage limiter
def increment_guest_usage():
    if not current_user.is_authenticated:
        session['guest_uses'] = session.get('guest_uses', 0) + 1
        if session['guest_uses'] > 5:
            flash("Guest usage limit reached. Please register or log in.")
            return False
    return True


def update_file_conversion_count(count=1):
    stat = SiteStat.query.first()
    if stat:
        stat.files_converted += count
        from models import db
        db.session.commit()


# ===== TOOL 1: Image Converter =====
@tools_bp.route('/tool/image-converter', methods=['GET', 'POST'])
def image_converter():
    if not increment_guest_usage():
        return redirect(url_for('dashboard'))

    max_files = 5 if not current_user.is_authenticated else 20

    if request.method == 'POST':
        files = request.files.getlist('images')
        output_format = request.form.get('format')

        if not files or files[0].filename == '':
            flash("Please select at least one image.")
            return redirect(request.url)

        if len(files) > max_files:
            flash(f"You can upload up to {max_files} files.")
            return redirect(request.url)

        try:
            converted_paths = []
            for image_file in files:
                img = Image.open(image_file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                converted_name = f"{uuid.uuid4().hex}.{output_format.lower()}"
                converted_path = os.path.join(UPLOAD_FOLDER, converted_name)

                img.save(converted_path, format=output_format.upper())
                converted_paths.append(converted_path)

            zip_filename = f"{uuid.uuid4().hex}_converted.zip"
            zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in converted_paths:
                    zipf.write(file_path, os.path.basename(file_path))

            update_file_conversion_count(len(converted_paths))

            return render_template('tools/image_converter.html',
                                   max_files=max_files,
                                   zip_filename=zip_filename)

        except Exception as e:
            flash(f"Conversion error: {str(e)}")
            return redirect(request.url)

    return render_template('tools/image_converter.html', max_files=max_files)


# ===== TOOL 2: Image to PDF =====
@tools_bp.route('/tool/image-to-pdf', methods=['GET', 'POST'])
def image_to_pdf():
    if not increment_guest_usage():
        return redirect(url_for('dashboard'))

    max_files = 5 if not current_user.is_authenticated else 20

    if request.method == 'POST':
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            flash("Please upload at least one image.")
            return redirect(request.url)

        if len(files) > max_files:
            flash(f"You can upload up to {max_files} files.")
            return redirect(request.url)

        try:
            pdf_paths = []
            for image_file in files:
                filename = f"{uuid.uuid4().hex}.jpg"
                img_path = os.path.join(UPLOAD_FOLDER, filename)

                img = Image.open(image_file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(img_path, "JPEG")

                pdf_filename = f"{uuid.uuid4().hex}.pdf"
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(img_path))

                pdf_paths.append(pdf_path)

            zip_filename = f"{uuid.uuid4().hex}_pdfs.zip"
            zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for pdf in pdf_paths:
                    zipf.write(pdf, os.path.basename(pdf))

            update_file_conversion_count(len(pdf_paths))

            return render_template('tools/image_to_pdf.html',
                                   max_files=max_files,
                                   zip_filename=zip_filename)

        except Exception as e:
            flash(f"Conversion error: {str(e)}")
            return redirect(request.url)

    return render_template('tools/image_to_pdf.html', max_files=max_files)


# ===== TOOL 3: PDF to Images =====
@tools_bp.route('/tool/pdf-to-images', methods=['GET', 'POST'])
def pdf_to_images():
    if not increment_guest_usage():
        return redirect(url_for('dashboard'))

    max_files = 5 if not current_user.is_authenticated else 20

    if request.method == 'POST':
        files = request.files.getlist('pdf_files')

        if not files or files[0].filename == '':
            flash("No PDF uploaded.")
            return redirect(request.url)

        if len(files) > max_files:
            flash(f"You can upload up to {max_files} PDF files.")
            return redirect(request.url)

        try:
            image_paths = []

            for file in files:
                pdf_filename = f"{uuid.uuid4().hex}.pdf"
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                file.save(pdf_path)

                doc = fitz.open(pdf_path)
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    pix = page.get_pixmap()
                    image_filename = f"{uuid.uuid4().hex}_p{page_number + 1}.png"
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    pix.save(image_path)
                    image_paths.append(image_path)

            zip_filename = f"{uuid.uuid4().hex}_images.zip"
            zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in image_paths:
                    zipf.write(img_path, os.path.basename(img_path))

            update_file_conversion_count(len(image_paths))

            return render_template('tools/pdf_to_images.html',
                                   zip_filename=zip_filename,
                                   max_files=max_files)

        except Exception as e:
            flash(f"Error processing PDF: {str(e)}")
            return redirect(request.url)

    return render_template('tools/pdf_to_images.html', max_files=max_files)


# ===== TOOL 4: Image Compressor =====
@tools_bp.route('/tool/image-compressor', methods=['GET', 'POST'])
def image_compressor():
    if not increment_guest_usage():
        return redirect(url_for('dashboard'))

    max_files = 5 if not current_user.is_authenticated else 20

    if request.method == 'POST':
        files = request.files.getlist('images')

        if not files or files[0].filename == '':
            flash("Please select at least one image.")
            return redirect(request.url)

        if len(files) > max_files:
            flash(f"You can upload up to {max_files} files.")
            return redirect(request.url)

        try:
            compressed_paths = []
            for image_file in files:
                img = Image.open(image_file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                filename = f"{uuid.uuid4().hex}_compressed.jpg"
                path = os.path.join(UPLOAD_FOLDER, filename)

                img.save(path, format="JPEG", quality=75, optimize=True)
                compressed_paths.append(path)

            zip_filename = f"{uuid.uuid4().hex}_compressed.zip"
            zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in compressed_paths:
                    zipf.write(img_path, os.path.basename(img_path))

            update_file_conversion_count(len(compressed_paths))

            return render_template('tools/image_compressor.html',
                                   max_files=max_files,
                                   zip_filename=zip_filename)

        except Exception as e:
            flash(f"Compression error: {str(e)}")
            return redirect(request.url)

    return render_template('tools/image_compressor.html', max_files=max_files)


# ===== Common Download Route =====
@tools_bp.route('/download/<filename>')
def download_zip(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
