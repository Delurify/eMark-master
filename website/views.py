import json
import os
from pathlib import Path

from PIL import Image
from PIL import ImageFont, ImageDraw, ImageColor
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
        pic = request.files['image']
        filename = "website/static/image/watermarked.jpg"

        check = os.path.exists(filename)
        if check:
            os.remove(filename)

        # Saving the image
        pic.save(Path(filename))    

    # return redirect(url_for('views.canvas'))
    return render_template("canvas.html", user=current_user, image=Path(f"static/image/{pic}"))


def apply_watermark(raw_image, name, watermark_text, fontType, placement, color):
    # Guard clause to handle the error
    # Ref: https://subscription.packtpub.com/book/programming/9781788293181/6/06lvl1sec66/guard-clauses
    if (not raw_image) or not (allowed_file(name)):
        return

    original_image = Image.open(raw_image).convert("RGBA")
    image_with_text = Image.new('RGBA', original_image.size, (255, 255, 255, 0))

    # Creating draw object
    draw = ImageDraw.Draw(image_with_text)

    # Adjusing Font Size Corresponding to Image Size
    fontSize = 1
    
    # Portion of image width that you want the text width to be
    img_fraction = 0.50

    # Creating TestFont object
    testFont = ImageFont.truetype(str(Path('website/font/Arial.ttf')), fontSize)

    text_width, text_height = draw.textsize(watermark_text, testFont)

    while int(testFont.getsize(watermark_text)[0]) < img_fraction*original_image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontSize += 1
        testFont = ImageFont.truetype(str(Path('website/font/Arial.ttf')), fontSize)

    # Creating text and font object
    font = ImageFont.truetype(str(Path('website/font/' + fontType)), fontSize)

    # Positioning Text
    text_width, text_height = draw.textsize(watermark_text, font)
    width, height = original_image.size
    if placement == "center":
        x = (width-text_width) / 2
        y = (height-text_height) / 2
    elif placement == "top-left":
        x = 0
        y = 0
    elif placement == "top-right":
        x = width - text_width
        y = 0
    elif placement == "bottom-left":
        x = 0
        y = height - text_height
    else:
        x = width - text_width
        y = height - text_height        
    
    # Get the font color
    rgbColor = ImageColor.getrgb(color)
    rgbaColor = tuple(list(rgbColor) + [128])  # add alpha value of 128 (semi-transparent)

    # Applying Text
    draw.text((x, y), watermark_text, fill=rgbaColor, font=font)

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

        if not pic:
            pic = request.files['preview-img']
            
        watermark_text = request.form.get('watermark_text')
        fontType = request.form.get('fontFamily')
        placement = request.form.get('placement')
        color = request.form.get("colorpicker")
            
        if not pic:
            flash('no pic uploaded', category='error')
            return render_template("watermark.html", user=current_user)
        if len(watermark_text) < 1:
            flash('no text entered', category='error')
            return render_template("watermark.html", user=current_user)
        

        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        check = os.path.exists("website/static/image/" + filename + "-watermarked.png")
        if check:
            os.path.remove("website/static/image/" + filename + "-watermarked.png")
        else:
            img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
            watermarked_file = apply_watermark(pic, filename, watermark_text, fontType, placement, color)

            # db.session.add(img)
            # db.session.commit()
            return render_template("watermark.html", user=current_user, image=Path(f"static/image/{watermarked_file}"))

    return render_template("watermark.html", user=current_user)


@views.route('/get_image/<int:id>')
def get_img(id):
    img = Imge.query.filter_by(id=id).first()
    if not img:
        return flash('There are no image in the database.', category='error')

    return Response(img.image, mimetype=img.mimetype)
