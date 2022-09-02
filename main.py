from PIL import Image
import pytesseract
import argparse
import cv2
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh", help="type of preprocessing to be done")
#Set the language to Japanese
ap.add_argument("-l", "--lang", required=True, type=str, default="jpn", help="language to be used for OCR")
args = vars(ap.parse_args())
print("Trying to run with the following args:", args)

#load the image and convert it to grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#check to see if we should apply thresholding to preprocess the image
if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)

filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

#load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
text = pytesseract.image_to_string(Image.open(filename), lang=args["lang"])
os.remove(filename)
print(text)
#Get the filename of the image without the extension
filename = args["image"].split(os.path.sep)[-1].split(".")[0]
#Try to log the text to a file
with open(filename+".txt", "w", encoding='utf-8') as f:
    try:
        f.write(text)
    except Exception as e:
        print("Could not write to text.txt:", e)
        pass

#show the output images
#cv2.imshow("Image", image)
#cv2.imshow("Output", gray)
cv2.waitKey(0)
#Print the filename
print("Filename:", filename+".txt")
