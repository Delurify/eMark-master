import json
from pathlib import Path

from PIL import Image
from PIL import ImageFont, ImageDraw
from flask import Blueprint, Flask, render_template, flash, request, jsonify, redirect, url_for, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import db
from .models import Note, Imge

src = "https://code.jquery.com/jquery-3.6.0.min.js"

views = Blueprint('views', __name__)
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/canvas', methods=['GET', 'POST'])
@login_required
def canvas():
    if request.method == "GET":
        return render_template("canvas.html", user=current_user)
    if request.method == "POST":
        # filename = request.form['save_fname']
        # data = request.form['save_cdata']
        # new_cert = Project(projName=filename, data=data, canvas_image=canvas_image, user_id=current_user.id)
        # db.session.add(new_cert)
        # db.session.commit()
        flash('Project added!', category='success')

    # return redirect(url_for('views.canvas'))
    return render_template("canvas.html", user=current_user)


def apply_watermark(raw_image, name, watermark_text):
    # Guard clause to handle the error
    # Ref: https://subscription.packtpub.com/book/programming/9781788293181/6/06lvl1sec66/guard-clauses
    if (not raw_image) or not (allowed_file(name)):
        return

    original_image = Image.open(raw_image).convert("RGBA")
    image_with_text = Image.new('RGBA', original_image.size, (255, 255, 255, 0))

    # Creating text and font object
    font = ImageFont.truetype(str(Path('website/font/Arial.ttf')), 82)

    # Creating draw object
    draw = ImageDraw.Draw(image_with_text)

    # Positioning Text
    text_width, text_height = draw.textsize(watermark_text, font)
    width, height = original_image.size
    x = width / 2 - text_width / 2
    y = height - text_height - 300

    # Applying Text
    draw.text((x, y), watermark_text, fill=(255, 255, 255, 125), font=font)

    # Saving the new image
    watermarked = Image.alpha_composite(original_image, image_with_text)
    filename = Path(f"{Path(name).stem}-watermarked.png")
    watermarked.save(Path('website/static/image', filename))
    flash('Digital Watermark embedded!', category='success')

    return filename


@views.route('/watermark', methods=['GET', 'POST'])
@login_required
def watermark():
    if request.method == 'POST':
        pic = request.files['image']
        watermark_text = request.form.get('text')
        
            
        if not pic:
            return flash('no pic uploaded', category='error')
        if not watermark_text:
            return flash('no text entered', category='error')
        

        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        check = Imge.query.filter_by(name=filename).first()
        if check:
            flash('Image already exist.', category='error')
        else:
            img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
            watermarked_file = apply_watermark(pic, filename, watermark_text)

            db.session.add(img)
            db.session.commit()
            flash('Image has been uploaded!', category='success')

            return render_template("watermark.html", user=current_user, image=Path(f"static/{watermarked_file}"))

    return render_template("watermark.html", user=current_user)


@views.route('/get_image/<int:id>')
def get_img(id):
    img = Imge.query.filter_by(id=id).first()
    if not img:
        return flash('There are no image in the database.', category='error')

    return Response(img.image, mimetype=img.mimetype)
