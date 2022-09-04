from PIL import Image
import pytesseract
import argparse
import cv2
import os


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def loadImage(path, pathSave):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename), lang="jpn")
    os.remove(filename)
    #Get the filename of the imagefile without the extension
    filename = path.split(os.path.sep)[-1].split(".")[0]
    if not pathSave:
        pathSave = filename + ".txt"
    with open(pathSave, "w", encoding='utf-8') as f:
        try:
            f.write(text)
        except Exception as e:
            print("Could not write to file", pathSave, e)
            pass

    print("Successfully wrote to file", pathSave)
    #How many lines of text were found in the image?
    print("# of lines:", len(text.split("\n")))
    return True

#loadImage("jptest.png", "txt/jptest.txt")


