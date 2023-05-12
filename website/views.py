import json
import os
from pathlib import Path
import glob
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageColor
from flask import Blueprint, Flask, render_template, flash, request, jsonify
import flask
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import zipfile
from os.path import basename
from cv2 import imread,imwrite
from base64 import urlsafe_b64encode
from hashlib import md5
from cryptography.fernet import Fernet

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


@views.route('/watermark-text', methods=['GET', 'POST'])
@login_required
def watermark_text():
    if request.method == 'POST':
        pic = request.files['image']
        pics = flask.request.files.getlist('image-batch[]')
            
        watermark_text = request.form.get('watermark_text')
        fontType = request.form.get('fontFamily') 
        placement = request.form.get('placement')
        color = request.form.get("colorpicker")
        
        # if there are no image uploaded
        if not pic and len(pics) == 1 and 'application' in str(pics[0]):
            flash('no file uploaded', category='error')
            return render_template("watermark-text.html", user=current_user)
        # if there are no text written
        if len(watermark_text) < 1:
            flash('no text entered', category='error')
            return render_template("watermark-text.html", user=current_user)
        
        if pic:
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype

            files = glob.glob("website/static/image/*")
            for f in files:
                os.remove(f)

            img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
            watermarked_file = apply_watermark(pic, filename, watermark_text, fontType, placement, color, 'single', 1)

            flash('Digital Watermark embedded!', category='success')
            return render_template("watermark-text.html", user=current_user, image=Path(f"static/image/{watermarked_file}"))

        else:
            loop = 1
            files = glob.glob("website/static/image-batch/*")
            for f in files:
                os.remove(f)
            for img in pics:
                filename = secure_filename(img.filename)
                mimetype = img.mimetype

                # see whether the picture is already exist in the local storage, if yes delete the initial image in the storage
                # check = os.path.exists("website/static/image-batch/" + filename)
                # if check:
                #     os.path.remove("website/static/image-batch/" + filename)
                # else:
                Img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
                watermarked_file = apply_watermark(img, filename, watermark_text, fontType, placement, color, 'batch', loop)
                
                loop = loop + 1
                    # db.session.add(Img)
                    # db.session.commit()

        with zipfile.ZipFile('website/static/watermarked.zip','w', compression= zipfile.ZIP_DEFLATED) as zip:
            for img in pics:
                filename = secure_filename(img.filename)

                new_filename = filename.replace(' ', '_')

                # Get the name and extension parts of the filename
                name, ext = os.path.splitext(new_filename)

                #Change the extension to .png
                new_ext = ".png"

                new_filename = name + new_ext

                zip.write("website/static/image-batch/" + new_filename, basename("website/static/image-batch/" + new_filename))

        zip.close()
        flash('Digital Watermark embedded!', category='success')
        return render_template("watermark-text.html", user=current_user, image=Path(f"static/image-batch/{watermarked_file}"), zipfile=Path(f"static/watermarked.zip"))

    return render_template("watermark-text.html", user=current_user)


@views.route('/watermark-invisible', methods=['GET', 'POST'])
@login_required
def watermark_invisible():
    if request.method == 'POST':
        pic = request.files['image']
        pics = flask.request.files.getlist('image-batch[]')
            
        hidden_text = request.form.get('hidden_text')
        password = request.form.get('watermark_password')

        # if there are no image uploaded
        if not pic and len(pics) == 1 and 'application' in str(pics[0]):
            flash('no file uploaded', category='error')
            return render_template("watermark-invisible.html", user=current_user)
        
        if pic:
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype

            files = glob.glob("website/static/image/*")
            for f in files:
                os.remove(f)

            img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
            watermarked_file = apply_watermark(pic, filename, "     ", "Arial.ttf", "center", "#fff", 'single', 1)

            if not filename.endswith(".png"):
                prefix = filename.split(".")[0]
                PNGfilename = prefix + ".png"
                encode("website/static/image/" + PNGfilename, hidden_text,"website/static/image/" + PNGfilename, password)

            else:
                encode("website/static/image/" + filename, hidden_text,"website/static/image/" + filename, password)

            flash('Hidden message Encoded!', category='success')
            return render_template("watermark-invisible.html", user=current_user, image=Path(f"static/image/{watermarked_file}"))

        else:
            loop = 1
            files = glob.glob("website/static/image-batch/*")
            for f in files:
                os.remove(f)
            for img in pics:
                filename = secure_filename(img.filename)
                mimetype = img.mimetype

                Img = Imge(image=pic.read(), mimetype=mimetype, name=filename)
                
                
                #Encode invisible digital watermark into image with password same as text
                if not filename.endswith(".png"):
                    prefix = filename.split(".")[0]
                    PNGfilename = prefix + ".png"
                    encode("website/static/image-batch/" + PNGfilename, watermark_text,"website/static/image-batch/" + PNGfilename, watermark_text)

                else:
                    encode("website/static/image-batch/" + filename, watermark_text,"website/static/image-batch/" + filename, watermark_text)
                
                loop = loop + 1
                    # db.session.add(Img)
                    # db.session.commit()

        with zipfile.ZipFile('website/static/watermarked.zip','w', compression= zipfile.ZIP_DEFLATED) as zip:
            for img in pics:
                filename = secure_filename(img.filename)

                new_filename = filename.replace(' ', '_')

                # Get the name and extension parts of the filename
                name, ext = os.path.splitext(new_filename)

                #Change the extension to .png
                new_ext = ".png"

                new_filename = name + new_ext

                zip.write("website/static/image-batch/" + new_filename, basename("website/static/image-batch/" + new_filename))

        zip.close()
        flash('Hidden Text Encoded!', category='success')
        return render_template("watermark-invisible.html", user=current_user, image=Path(f"static/image-batch/" + new_filename), zipfile=Path(f"static/watermarked.zip"))

    return render_template("watermark-invisible.html", user=current_user)

# Apply watermark
fontSize = 1

def apply_watermark(raw_image, name, watermark_text, fontType, placement, color, type, loop):
    global fontSize
    # Guard clause to handle the error
    # Ref: https://subscription.packtpub.com/book/programming/9781788293181/6/06lvl1sec66/guard-clauses
    if (not raw_image) or not (allowed_file(name)):
        return

    original_image = Image.open(raw_image).convert("RGBA")
    image_with_text = Image.new('RGBA', original_image.size, (255, 255, 255, 0))

    # Creating draw object
    draw = ImageDraw.Draw(image_with_text)

    if loop == 1:
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
    
    if type == 'single':
        filename = Path(f"{Path(name).stem}.png")
        watermarked.save(Path('website/static/image', filename))
    else:
        filename = Path(f"{Path(name).stem}.png")
        watermarked.save(Path('website/static/image-batch', filename))

    return filename

# Image encryption: Steganography
def encrypt_decrypt(string,password,mode='enc'):
    _hash = md5(password.encode()).hexdigest() #get hash of password
    cipher_key = urlsafe_b64encode(_hash.encode()) #use the hash as the key of encryption
    cipher = Fernet(cipher_key) #get the cipher based on the cipher key
    if mode == 'enc':
        return cipher.encrypt(string.encode()).decode() #encrypt the data
    else:
        return cipher.decrypt(string.encode()).decode() #decrypt the data



def str2bin(string):
	return ''.join((bin(ord(i))[2:]).zfill(8) for i in string)

def encode(input_filepath,text,output_filepath,password=None):
    if password != None:
        data = encrypt_decrypt(text,password,'enc') #If password is provided, encrypt the data with given password
    else:
        data = text #else do not encrypt
    data_length = bin(len(data))[2:].zfill(32) #get length of data to be encoded
    bin_data = iter(data_length + str2bin(data)) #add length of data with actual data and get the binary form of whole thing
    img = imread(input_filepath,1) #read the cover image
    if img is None:
        flash('Please in', category='success')
        raise FileError("The image file '{}' is inaccessible".format(input_filepath)) #if image is not accessible, raise an exception
    height,width = img.shape[0],img.shape[1] #get height and width of cover image
    encoding_capacity = height*width*3 #maximum number of bits of data that the cover image can hide
    total_bits = 32+len(data)*8 #total bits in the data that needs to be hidden including 32 bits for specifying length of data
    if total_bits > encoding_capacity:
        raise DataError("The data size is too big to fit in this image!") #if cover image can't hide all the data, raise DataError exception
    completed = False
    modified_bits = 0
    
    #Run 2 nested for loops to traverse all the pixels of the whole image in left to right, top to bottom fashion
    for i in range(height):
        for j in range(width):
            pixel = img[i,j] #get the current pixel that is being traversed
            for k in range(3): #get next 3 bits from the binary data that is to be encoded in image
                try:
                    x = next(bin_data)
                except StopIteration: #if there is no data to encode, mark the encoding process as completed
                    completed = True
                    break
                if x == '0' and pixel[k]%2==1: #if the bit to be encoded is '0' and the current LSB is '1'
                    pixel[k] -= 1 #change LSB from 1 to 0
                    modified_bits += 1 #increment the modified bits count
                elif x=='1' and pixel[k]%2==0: #if the bit to be encoded is '1' and the current LSB is '0'
                    pixel[k] += 1 #change LSB from 0 to 1
                    modified_bits += 1 #increment the modified bits count
            if completed:
                break
        if completed:
            break

    written = imwrite(output_filepath,img) #create a new image with the modified pixels
    if not written:
        raise FileError("Failed to write image '{}'".format(output_filepath))
    
class FileError(Exception):
    pass

class DataError(Exception):
    pass

class PasswordError(Exception):
    pass