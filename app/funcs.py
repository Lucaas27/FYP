from app import app, mail
from flask_mail import Message
import os
import binascii
from PIL import Image
from flask import url_for
import secrets

# save image file name


def save_pic(form_picture, pic_path_str):

    # generate a random hex string
    random_hex = secrets.token_hex(8)
    # split filename and extension
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = str(random_hex) + str(f_ext)
    picture_path = os.path.join(app.root_path, pic_path_str, picture_name)

    # resize image
    output_size = (300, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    # return image file
    return picture_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email]
                  )
    msg.body = f''' 
    
    Hi, {user.first_name}
    
    We got a request to reset your Lensify password.
    Please visit the following link:
    
    {url_for('request_token', token = token, _external = 'True')}

    If you did not make this request please ignore this message and no changes will be made.
    
    
    '''
    mail.send(msg)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    return False
