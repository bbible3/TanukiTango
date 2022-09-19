from PIL import Image
import pytesseract
import argparse
import cv2
import os
from manga_ocr import MangaOcr

class TanukiOcr:


    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


    def loadImage(path, pathSave=None, ocrMode="none"):
        if ocrMode == "manga-ocr":
            #Load as manga ocr
            mocr = MangaOcr()
            text = mocr(path)
            filename = path.split(os.path.sep)[-1].split(".")[0]
            if not pathSave:
                pathSave = filename + ".txt"
            fileStrOnly = filename.split('/')[-1]
            if not pathSave:
                pathSave = pathSave + "/" + fileStrOnly + ".txt"
            print("Saving to:", fileStrOnly)
            with open(pathSave, "w", encoding='utf-8') as f:
                try:
                    f.write(text)
                except Exception as e:
                    print("Could not write to file", pathSave, e)
                    pass

            print("Successfully wrote to file", pathSave)
            # How many lines of text were found in the image?
            print("# of lines:", len(text.split("\n")))
            return True
        else:
            print("Loading image:", path)
            image = cv2.imread(path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, gray)
            text = pytesseract.image_to_string(Image.open(filename), lang="jpn_vert")
            os.remove(filename)
            # Get the filename of the imagefile without the extension
            filename = path.split(os.path.sep)[-1].split(".")[0]
            if not pathSave:
                pathSave = filename + ".txt"

            fileStrOnly = filename.split('/')[-1]
            pathSave = pathSave + "/" + fileStrOnly + ".txt"
            print("Saving to:", fileStrOnly)
            with open(pathSave, "w", encoding='utf-8') as f:
                try:
                    f.write(text)
                except Exception as e:
                    print("Could not write to file", pathSave, e)
                    pass

            print("Successfully wrote to file", pathSave)
            # How many lines of text were found in the image?
            print("# of lines:", len(text.split("\n")))
            return True

    def processAll(path, outPath, ocrMode="manga-ocr"):
        #Read all the pngs in the directory
        pngs = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.png')]
        #Make a txt folder in this path if it does not exist
        if not os.path.exists(path + "/txt"):
            os.makedirs(path + "/txt")
        #For each png, process it and save the text to a txt file
        for png in pngs:
            print("Processing", png)
            TanukiOcr.loadImage(png, outPath, ocrMode)
    def removeSpaces(path):
        #Load all txt in path
        txts = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.txt')]
        #For each txt, remove all spaces
        for txt in txts:
            print("Removing spaces from:", txt)
            with open(txt, "r", encoding='utf-8') as f:
                text = f.read()
            text = text.replace(" ", "")
            with open(txt, "w", encoding='utf-8') as f:
                try:
                    f.write(text)
                except Exception as e:
                    print("Could not write to file", txt, e)
                    pass
            print("Successfully wrote to file", txt)
    #loadImage("jptest.png", "txt/jptest.txt")
    #loadImage("kinmoza2.png", pathSave="kinmoza2.txt", ocrMode="manga-ocr")
#TanukiOcr.processAll("video/demo-mp4/frames/", "video/demo-mp4/frames/txt/")
