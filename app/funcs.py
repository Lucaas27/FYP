from app import app
import os, binascii
from PIL import Image
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

