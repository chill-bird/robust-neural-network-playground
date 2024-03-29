import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
import os

# Load external resources ---------------------------
path = os.path.abspath(os.getcwd()) + "/ui/resources/"

background_im  = Image.open(path + "background.png")
gameover_im    = Image.open(path + "gameover.png")
pole_im        = Image.open(path + "pole.png")
flame_im       = Image.open(path + "flame.png")
font_bold_path = path + "NotoSansMono-Bold.ttf"
font_path      = path + "NotoMono-Regular.ttf"
pole_im_w, pole_im_h = pole_im.size
flame_im_w, flame_im_h = flame_im.size

# Scaling Factors ---------------------------
width  = 600 
height = 400
x_offset = width/2
y_offset = height - height*0.3 # reversed y-axis
animation_width = 4.8
scale = 0.3 * width/animation_width
assert(width/height == background_im.size[0]/background_im.size[1]), "Background image must have ratio 3:2"

# Scaled Images ---------------------------
# Background
background_im = background_im.resize((width, height))
gameover_im   = gameover_im.resize((width, height))
# Cart
cart_length = 2 * scale
cart_height = 0.6 * cart_length
# Pole
pole_height = 3 * scale
resize_factor = pole_height / pole_im_h
pole_width = pole_im_w * resize_factor
pole_im = pole_im.resize((round(pole_width), round(pole_height)))
# Flame
flame_height = 3 * scale
resize_factor = flame_height / flame_im_h
flame_width = flame_im_w * resize_factor
flame_im = flame_im.resize((round(flame_width), round(flame_height)))

def render(x_cart: int, angle: float, game_over: bool, episode_num: int, score: int):
    """
    Receive x coordinate of a cart and angle(rad) of the pole and return an RGB array of the drawn scene.
    Coordinates start with (0.0) at the upper left corner of the background image.
    """

    assert(episode_num >= 0), "Episode_num must be positive integer"
    assert(score       >= 0), "Current frame number (= score) must be positive integer"

    # Scene ---------------------------
    if game_over:
        scene = gameover_im.copy()
    else:
        scene = background_im.copy()
    # Create draw object
    draw = ImageDraw.Draw(scene)

    # Cart ---------------------------
    x_cart = scale * x_cart + x_offset # Scale x_coordinate and add offset
    y_cart = y_offset

    # Draw cart
    l = round(x_cart - 0.5*cart_length)
    r = round(x_cart + 0.5*cart_length)
    t = round(y_cart - 0.5*cart_height)
    b = round(y_cart + 0.5*cart_height)
    draw.rectangle((l,t,r,b), fill=(0,0,0))

    # Draw cart center
    radius = scale * 0.05
    draw.ellipse((x_cart-radius, y_offset-radius, x_cart+radius, y_offset+radius), fill=(255,0,0))

    # Pole ---------------------------
    angle *= -1 # Use non-mathematical angle direction
    pole = pole_im.copy()
    pole = pole.rotate(math.degrees(angle), expand=1)
    # Pole vector
    # Vector pointing from the cart center to the center of the pole position
    rot_matrix = np.array([[math.cos(angle), -math.sin(angle)], \
                           [math.sin(angle),  math.cos(angle)]])
    pole_vector = rot_matrix @ np.array([0, - pole_height/2])

    # Pole upper left corner coordinates
    # Starting at the center of the pole, subtract edge length of new, rotated image
    pole_left  = x_cart - pole_vector[0] - (pole.size[0] / 2)
    pole_upper = y_cart + pole_vector[1] - (pole.size[1] / 2)

    # Placing image
    scene.paste(pole, (round(pole_left), round(pole_upper)), mask=pole)

    # Flame ---------------------------
    flame = flame_im.copy()
    # Flame upper left corner coordinates
    # Starting at the tip of the pole
    flame_x_offset = 0.03 * flame.size[0] # flame graphic is slightly off-centered
    flame_left  = x_cart - 2*pole_vector[0] - (flame.size[0] / 2) + flame_x_offset
    flame_upper = y_cart + 2*pole_vector[1] - (flame.size[0] / 2)

    # Placing image
    scene.paste(flame, (round(flame_left), round(flame_upper)), mask=flame)

    # Display angle & epsiode number
    c = width*0.73 # center x coordinate of text box
    t = -height*0.07 # top y coordinate of text box
    draw.text((c, t), "\nScore", fill=(0,0,0), font=ImageFont.truetype(font_bold_path, 20)) # paragraph inserted due to different alignments
    draw.text((c, t), f"             \n{score}", fill=(0,0,0), font=ImageFont.truetype(font_bold_path, 20), align="right")
    draw.text((c, t+30), "\nEpisode", fill=(0,0,0), font=ImageFont.truetype(font_path, 20)) # paragraph inserted due to different alignments
    draw.text((c, t+30), f"             \n{episode_num}", fill=(0,0,0), font=ImageFont.truetype(font_path, 20), align="right")
    draw.text((c, t+50), "\nAngle", fill=(0,0,0), font=ImageFont.truetype(font_path, 20)) # paragraph inserted due to different alignments
    draw.text((c, t+50), f"             \n{round(math.degrees(angle), 2)}°", fill=(0,0,0), font=ImageFont.truetype(font_path, 20), align="right")

    return np.array(scene)
