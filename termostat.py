from PIL import Image, ImageFont, ImageDraw
import ST7789 as ST7789
from gpiozero import LightSensor, Button, DigitalOutputDevice
from bisect import bisect_left

# global device on/off setting

power = False

# Declare display
lcd = ST7789.ST7789(port= 0, cs = ST7789.BG_SPI_CS_FRONT, dc = 25, rst = 27, backlight = 18, mode = 3, spi_speed_hz = 8000000)
pic = Image.open("start.bmp")
lcd.display(pic)
print("display declared")


# next few things are for drawing to the screen
def write_white_text(background, text, height, font):
    draw = ImageDraw.Draw(background)
    draw.text((10, height), text, font=font)
    return background

def write_gray_text(background, text, height, font):
    draw = ImageDraw.Draw(background)
    draw.text((20, height), text, font=font, fill=(128,128,128,255))
    return background

def make_blank_background(color):
    return Image.new('RGBA', (240, 240), color)

big_font = ImageFont.truetype("/home/pi/FreeSans.ttf",140)
small_font = ImageFont.truetype("/home/pi/FreeSans.ttf",80)

print("image functions and fonts OK")

# define the sensor and the global target starting value
target = 65
sensor = LightSensor(4, charge_time_limit=0.1, queue_len=5)
print("sensor declared")

# define the buttons and their functions
blackButton, greenButton, redButton = Button(14), Button(24,hold_repeat=True,hold_time=0.5), Button(23,hold_repeat=True,hold_time=0.5)

def master_power():
    global power
    power = not power

def increase_target():
    global target
    target += 1

def decrease_target():
    global target
    target -= 1

blackButton.when_pressed = master_power

redButton.when_pressed = increase_target
redButton.when_held = increase_target

greenButton.when_pressed = decrease_target
greenButton.when_held = decrease_target
print("buttons and functions defined")


# define the relay

relay = DigitalOutputDevice(17)

#relay.blink(n=10,background=False)

print("relay defined - ready to go")

# dictionary of sensor values corresponding to temperatures

calibrationTable = {20:0.2,60:0.43,61:0.45,62:0.47,63:0.49,64:0.51,65:0.54,66:0.56,67:0.58,68:0.60,69:0.62,70:0.64,77:0.75,100:1.0}


# some functions to translate from readings to temps
def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

def get_temp_from_reading(reading):
    #find the closest reading in the table
    close_reading = (take_closest(sorted(list(calibrationTable.values())),reading))

    #look it up
    for key, value in calibrationTable.items():
        if close_reading == value:
            return key




while True:
    #value = get_temp_from_reading(sensor.value)
    value = get_temp_from_reading(0.441)
    close_to_target = target - 10
    really_close_to_target = target - 5

    if not power:
        background = make_blank_background("black")
        relay.off()

    elif value == target:
        background = make_blank_background("green")
        relay.off()

    elif value >= target:
        background = make_blank_background("red")
        relay.off()

    elif value >= really_close_to_target:
        background = make_blank_background("turquoise")
        relay.blink(on_time=2, off_time=4, n=1, background=False)

    elif value >= close_to_target:
        background = make_blank_background("aqua")
        relay.blink(on_time=2, off_time=2, n=1, background=False)

    else:
        background = make_blank_background("blue")
        relay.on()



    image = write_white_text(background, (str(value))+u"\u00B0", 0, big_font)
    image = write_gray_text(background, (str(target))+u"\u00B0", 150, small_font)
    lcd.display(image)
