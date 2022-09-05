from vproc import TanukiVproc
from ocr import TanukiOcr

#Extract all frames from a video
#TanukiVproc.extractAllFrames("video/demo.mp4", "video/demo-mp4/frames/")

#Process all of the frames to get their differences, remove them if they are deemed identical
#TanukiVproc.processFrames("video/demo-mp4/frames/")

#OCR all of the frames
#TanukiOcr.processAll("video/demo-mp4/frames/", "video/demo-mp4/frames/txt/", ocrMode="none")

#Process just one image
#TanukiOcr.loadImage("fullpage.png", "txt/")

#Remove spaces from the text files
TanukiOcr.removeSpaces("video/demo-mp4/frames/txt/")