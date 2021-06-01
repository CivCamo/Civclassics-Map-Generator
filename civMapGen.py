import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import json
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from adjustText import adjust_text
from blend_modes import multiply
from datetime import datetime
import requests

def matPlotGenerate(mapType, dpiRes):

    fig = plt.figure()

    # Allow for plotting to a single subplot, so multiple windows for nation don't pop up
    # figsize is a little weird when working in conjunction with the padding output:
    #    "... pad_inches = -0.685)".
    # This is to align and overlay the claims later, figsize=(15,15) seems to align right.
    # Idk why, but something tells me "Metric is better"

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,15))

    texts = []

    def parseJSONData(alpha):

        response = requests.get("https://raw.githubusercontent.com/ccmap/data/master/land_claims.civmap.json")
        data = json.loads(response.text)

        for item in data["features"]:

            # try, except to catch errors in data, will pass if so

            try:

                # Default size for names on the graph.
                nameSize = 5
                colour = str(item["color"]).replace(" ","")

                for polygon in item["polygon"]:
                    coord = polygon
                    coord.append(coord[0])
                    xs, ys = zip(*coord)

                    # Polygon filling, if alpha is True land will be filled, 
                    # otherwise text will be generated separately, on transparent land ... (Yes,I know)

                    if alpha:
                        ax.fill(xs, ys, colour, alpha=1)

                    else:

                        # Name sizing is arbitrary atm and based on land mass,
                        # dividing by 80,000 seemed to produce decent results

                        area = 0.5*np.abs(np.dot(xs, np.roll(ys, 1))-np.dot(ys,np.roll(xs, 1)))
                        nameSize = int(round(area/(nameSize*80000)))

                        # Some names are still either too big or too small

                        if nameSize <= 5: 
                            nameSize = 5
                        if nameSize >= 30: 
                            nameSize = 30

                        matplotlib.rcParams["font.serif"] = "Times"
                        matplotlib.rcParams["font.family"] = "serif"

                        ax.fill(xs, ys, color=colour, alpha=0)
                        centerOfPolygon = (max(xs)+min(xs))/2., (max(ys)+min(ys))/2.
                        txt = ax.text(centerOfPolygon[0],centerOfPolygon[1],item["name"], size=nameSize, color="black", horizontalalignment="center", verticalalignment="center")
                        texts.append(txt)

            except Exception as ex:
                print(ex)
                print(item['name'])
                pass

    def setMatplotLib():

        # Invert y axis, otherwise using Minecraft's coordinates will be invert the map vertically

        plt.gca().invert_yaxis()

        # Matplotlib settings to remove axis' and whitespace from image

        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax.get_xaxis().set_visible(False)
        ax.axis("tight")
        ax.axis("off")
        ax.set_aspect(1)

    if mapType is "textMap":

        parseJSONData(alpha=False)
        setMatplotLib()

        # TODO: Better text generation, currently this keeps them from overlapping,
        # it's also really resource hungry to do this.

        adjust_text(texts,
                    expand_text=(0.5, 0.5),
                    force_text=(0.01, 0.1))

        plt.savefig("textMap.png",
                    dpi=dpiRes,
                    transparent=True)

    elif mapType is "polygons":

        parseJSONData(alpha=True)

        setMatplotLib()
        plt.savefig("polygons.png",
                    dpi=dpiRes,
                    transparent=True,
                    bbox_inches="tight",
                    pad_inches = -0.685)

def resizeImage(inputPath, outputPath, width, height):

    # Set max amount pixels to None, otherwise pillow will log a warning.

    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(inputPath)
    img = img.convert("RGBA")
    img = img.resize((width, height), Image.ANTIALIAS)
    img.save(outputPath)

def removeWater(inputPath, outputPath):

    img = Image.open(inputPath)
    if "A" in img.getbands():

        # Just checking, and converting to rgba if it isn't already
        img = img.convert("RGBA")

    # Then convert to HSV, as its way easier to work with

    HSVim = img.convert("HSV")
    RGBna = np.array(img)
    HSVna = np.array(HSVim)
    H = HSVna[:,:,0]

    # HSV values for blue

    lo,hi = 170, 250

    # Convert HSV to back to RGBA

    lo = int((lo * 255) / 360)
    hi = int((hi * 255) / 360)
    blue = np.where((H>lo) & (H<hi))
    RGBna[blue] = [0, 0, 0, 0]

    Image.fromarray(RGBna).save(outputPath)

def multiplyMaps(backgroundImage, foregroundImage, opacity=0.6):

    # From the blend_modes library.

    background_img_float = cv2.imread(backgroundImage,-1).astype(float)
    foreground_img_float = cv2.imread(foregroundImage,-1).astype(float)
    blended_img_float = multiply(background_img_float, foreground_img_float, opacity)
    blended_img_uint8 = blended_img_float.astype(np.uint8)
    cv2.imwrite("overlayMap.png", blended_img_uint8)

def createImage(height, width, colour, typeOfimage, textColour="white", font="Times"):

    img = Image.new("RGBA", (width, height), (255, 0, 0, 0))
    x, y =  img.size
    eX, eY = width, height
    bbox =  (x/2 - eX/2, y/2 - eY/2, x/2 + eX/2, y/2 + eY/2)

    draw = ImageDraw.Draw(img)

    if typeOfimage is "ocean":
        draw.ellipse(bbox, fill=colour)

    elif typeOfimage is "background":
        draw.rectangle(bbox, fill=colour)

        # TODO: Convert text, and text placements to percentages

        smallFont = ImageFont.truetype(font, 90)
        mediumFont = ImageFont.truetype(font, 140)
        fntSymbols = ImageFont.truetype(font, 350)

        draw.text((100,100), "Claims map organised by\nThe Unified map project", font=mediumFont, fill=textColour)
        draw.text((100, 350), "discord.gg/hKJ9hQXB5S", font=smallFont, fill=textColour)
        draw.text((width-1200, 100), "Base map by Gjum", font=mediumFont, fill=textColour)
        draw.text((width-700, 250), "ccmap.github.io", font=smallFont, fill=textColour)

        draw.text((200,height-300), "Made by Camokool", font=mediumFont, fill=textColour)

        datem = datetime.now().strftime("%h")
        datey = datetime.now().strftime("%y")
        dateString = datem.capitalize() + " " + datey
        draw.text((width-900, height-300), dateString, font=mediumFont, fill=textColour)

        draw.text((550, 550), "~,~", font=fntSymbols, fill=textColour)
        draw.text((550, height-850), "-,+", font=fntSymbols, fill=textColour)

        draw.text((width-1000, 550), "+,-", font=fntSymbols, fill=textColour)
        draw.text((width-1000, height-850), "+,+", font=fntSymbols, fill=textColour)

    del draw
    img.save(typeOfimage + ".png", "PNG")

def mergeImage(backgroundImage, overlayImage, outputPath):

    img = Image.open(overlayImage)
    background = Image.open(backgroundImage)
    img_w, img_h = img.size
    bg_w, bg_h = background.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset, img)
    background.save(outputPath, "PNG")

def main():

    start = datetime.now()

    # Current resolution and dpi are important to the text generation, meaning...
    # The values at this current time can't be changed. See createImage().

    dpiRes = 500
    width = 5000
    height = 5000

    oceanColour = "#A6BBEB"

    backgroundBorder = 500
    backgroundColour = "#363636"

    print("Creating polygons, and painting my nails... 💅")
    matPlotGenerate("polygons", dpiRes)

    print("Generating text map, this may take awhile... 😴")
    matPlotGenerate("textMap", dpiRes)

    print("Resizing a few files... 🗃")
    resizeImage("baseMap.png", "resizedBaseMap.png", width, height)
    resizeImage("polygons.png", "resizedPolygons.png", width, height)
    resizeImage("textMap.png", "resizedText.png", width, height)

    print("Removing 💦 from the 🌏... ")
    removeWater("resizedBaseMap.png", "transparentBaseMap.png")

    print("Overlaying polygons to map... 🤓 ☝️ 🗺")
    multiplyMaps("transparentBaseMap.png", "resizedPolygons.png")

    print("Creating a serene sea... 🌅")
    createImage(width, height, oceanColour, "ocean")

    print("Merging earth and sea... ⛰💥🌊")
    mergeImage("ocean.png", "overlayMap.png", "mapNoBackground.png")

    # We'll leave these out for now

    # print("Merging text and map layers")
    # mergeImage("mapNoBackground.png", "resizedText.png", "mapWithText.png")

    # print("Creating a nice background... 🧑‍💻")
    # createImage((width+backgroundBorder), (height+backgroundBorder), backgroundColour, "background")

    # print("Merging final layers... 🍆💦🍑")
    # #mergeImage("background.png", "mapWithText.png", "mapWithBackground.png")
    # mergeImage("background.png", "mapNoBackground.png", "mapWithBackground.png")

    print("Done! ❤️  Generation 🕓 taken: " + str(datetime.now()-start) +" ❤️")

if __name__ == "__main__":
    main()

