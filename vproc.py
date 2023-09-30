import ffmpeg
import os
import diffimg
import cv2

class TanukiVproc:
    def extractAllFrames(videoPath, outputPath):
        #Create the output folder if it does not exist
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        ffmpeg.input(videoPath).output(outputPath + '%d.png', start_number=0).run()

    def processFrames(directory, fac=1.0, quiet=True):
        print("Processing frames...")
        #Get the path of pngs in dir
        pngs = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]
        #Sort them properly in numeric order
        pngs.sort(key=lambda f: int(os.path.splitext(os.path.basename(f))[0]))

        difvals = []
        for index, png in enumerate(pngs):
            if index < len(pngs)-1:
                if not quiet: 
                    print("This:", png, "Next:" , pngs[index+1])
                difresult = diffimg.diff(png, pngs[index+1])
                difvals.append(difresult)
                if not quiet:
                    print("Differs by:", difresult)
            else:
                if not quiet:
                    print("This:", png, "Next: None")

        #What is the maximum difval?
        maxdif = max(difvals)
        print("Max dif:", maxdif)
        #What is the minimum difval?
        mindif = min(difvals)
        print("Min dif:", mindif)
        #What is the standard deviation of the difvals?
        stddif = sum(difvals)/len(difvals)
        print("Std dif:", stddif)

        allowedDev = stddif*fac
        nremoved = 0
        for index, png in enumerate(pngs):
            if index < len(pngs)-1:
                if difvals[index] < allowedDev:
                    print("Removing:", png)
                    os.remove(png)
                    nremoved += 1
        print("Removed:", nremoved)
    def cropImage(imgLoc, ratio):
        #Load the image
        img = cv2.imread(imgLoc)
        #Get the height and width of the image
        height, width = img.shape[:2]
        #Get the new height and width
        newHeight = int(height*ratio)
        newWidth = int(width*ratio)
        #Crop the image
        #img = img[0:newHeight, 0:newWidth]
        #Crop the image to the center
        img = img[int(height/2-newHeight/2):int(height/2+newHeight/2), int(width/2-newWidth/2):int(width/2+newWidth/2)]
        #Save the image
        cv2.imwrite(imgLoc, img)
        return img
    def curDir():
        return os.path.dirname(os.path.realpath(__file__))
    def countFrames(directory):
        return len(os.listdir(directory))
#Extract all frames from a video
#extractAllFrames("video/demo.mp4", "video/demo-mp4/frames/")
#Process all of the frames to get their differences, remove them if they are deemed identical
#processFrames("video/demo-mp4/frames/")
#TanukiVproc.cropImage("video/demo-mp4/frames/104.png", 0.9)
#TanukiVproc.extractAllFrames("video/mls.mp4", "video/mls-mp4/frames/")
#TanukiVproc.processFrames("video/mls-mp4/frames/", 1.0, False)