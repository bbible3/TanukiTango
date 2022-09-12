import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QGridLayout, QTabWidget, QPushButton, QLineEdit, QProgressBar
from vproc import TanukiVproc
from ocr import TanukiOcr

def loadDirectory(textbox):
    #Get the directory
    directory = QFileDialog.getOpenFileName(window, 'Select Directory', textbox.text(), filter="Mp4 Files (*.mp4)")
    print(directory)
    if len(directory[0])>0:
        QLineEdit.setText(textbox, directory[0])
def runExtraction(textbox, statusLabel=None):

    setTextTo = "Status: Extracting frames..."

    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    

    #Get the file
    directory = textbox.text()

    #Get just the name of the file without directories
    filename = directory.split(os.path.sep)[-1]
    #Replace the period with a dash
    filename_subdir = filename.replace(".", "-")
    #Get just the directory without the file
    working_directory = directory.replace(filename, "")

    our_subdir = working_directory + filename_subdir
    if not os.path.exists(our_subdir):
        os.makedirs(our_subdir)
        os.makedirs(our_subdir + "/frames")
    else:
        print("Directory already exists")
        
    #Force a refresh
    QApplication.processEvents()

    TanukiVproc.extractAllFrames(directory, our_subdir + "/frames/")
def runSeparation(textbox, statusLabel=None):
 

    

    #Get the file
    directory = textbox.text()

    #Get just the name of the file without directories
    filename = directory.split(os.path.sep)[-1]
    #Replace the period with a dash
    filename_subdir = filename.replace(".", "-")
    #Get just the directory without the file
    working_directory = directory.replace(filename, "")

    our_subdir = working_directory + filename_subdir
    if not os.path.exists(our_subdir):
        os.makedirs(our_subdir)
        os.makedirs(our_subdir + "/frames")
    else:
        print("Directory already exists")
        
    our_subdir = our_subdir + "/frames/"
    print("Running separation in:", our_subdir)
    setTextTo = "Status: Separating " + str(TanukiVproc.countFrames(our_subdir)) + " frames..."
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    TanukiVproc.processFrames(our_subdir)

def getOCRFolder(textbox, statusLabel=None):
    print("Getting OCR folder")
    directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    textbox.setText(directory)
    
def startOCR(textbox, statusLabel=None):
    print("Starting OCR")
    directory = textbox.text()
    setTextTo = "Status: OCRing " + str(TanukiVproc.countFrames(directory)) + " frames..."
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    TanukiOcr.processAll(directory, directory + "/txt/", ocrMode="none")

app = QApplication([])

window = QWidget()
window.setWindowTitle('TanukiTango')
#window.setGeometry(100, 100, 300, 300)
#Set the window's minimum size
window.setMinimumSize(600, 300)

#Create a QHBoxLayout
layout = QGridLayout()
window.setLayout(layout)

#Generate content for the tabs

#Tab 1
tab1 = QWidget()
tab1_layout = QGridLayout()
tab1.setLayout(tab1_layout)
tab1_label1 = QLabel('<h1>Frame Extraction</h1>')
tab1_label2 = QLabel('<h2>Select an MP4 video file to extract unique frames.</h2>')

tab1_tabtext = "Frame Extraction"

#A textbox and button to select the video file
tab1_textbox = QLineEdit('')
tab1_textbox_default = TanukiVproc.curDir()
tab1_textbox.setText(tab1_textbox_default)

tab1_textbox.setReadOnly(True)
tab1_button = QPushButton('Select Video File')
tab1_button.clicked.connect(lambda: loadDirectory(tab1_textbox))

tab1_start_button = QPushButton('Begin frame extraction')
tab1_start_button.clicked.connect(lambda: runExtraction(tab1_textbox, statusLabel=tab1_status_label))

tab1_status_label = QLabel('Status: Waiting...')

tab1_start_proc = QPushButton('Begin frame separation')
tab1_start_proc.clicked.connect(lambda: runSeparation(tab1_textbox, statusLabel=tab1_status_label))

#Add labels
#Add tab1_label1 to the layout
tab1_layout.addWidget(tab1_label1, 0, 0)
#Add tab1_label2 to the layout
tab1_layout.addWidget(tab1_label2, 1, 0)
#Add tab1_textbox to the layout
tab1_layout.addWidget(tab1_textbox, 2, 0)
#Add tab1_button to the layout
tab1_layout.addWidget(tab1_button, 2, 1)
#Add tab1_start_button to the layout
tab1_layout.addWidget(tab1_start_button, 3, 0)
#Add tab1_status_label to the layout
tab1_layout.addWidget(tab1_status_label, 4, 0)
#Add tab1_start_proc to the layout
tab1_layout.addWidget(tab1_start_proc, 5, 0)

#Tab 2
tab2 = QWidget()
tab2_layout = QGridLayout()
tab2.setLayout(tab2_layout)

tab2_label = QLabel('<h1>Auto OCR</h1>')
tab2_tabtext = "Auto OCR"
tab2_label2 = QLabel('<h2>Select a folder of frames to attempt OCR on.</h2>')

#Text box and button to select the video file
tab2_textbox = QLineEdit('')
tab2_textbox_default = TanukiVproc.curDir()
#Make it read only
tab2_textbox.setReadOnly(True)
tab2_textbox.setText(tab2_textbox_default)

tab2_button = QPushButton('Select Folder')
tab2_button.clicked.connect(lambda: getOCRFolder(tab2_textbox, statusLabel=tab2_status_label))
tab2_status_label = QLabel('Status: Waiting...')
tab2_start_ocr_button = QPushButton('Begin OCR')
tab2_start_ocr_button.clicked.connect(lambda: startOCR(tab2_textbox, statusLabel=tab2_status_label))
tab3_label = QLabel('<h1>Tab 3</h1>')



#Add label to the layout
tab2_layout.addWidget(tab2_label, 0, 0)
#Add label2 to the layout
tab2_layout.addWidget(tab2_label2, 1, 0)
#Add textbox to the layout
tab2_layout.addWidget(tab2_textbox, 2, 0)
#Add button to the layout
tab2_layout.addWidget(tab2_button, 2, 1)
#Add status label to the layout
tab2_layout.addWidget(tab2_status_label, 3, 0)
#Add start button to the layout
tab2_layout.addWidget(tab2_start_ocr_button, 4, 0)



#Add the tabs
tabwidget = QTabWidget()
tabwidget.addTab(tab1, tab1_tabtext)
tabwidget.addTab(tab2, tab2_tabtext)
tabwidget.addTab(tab3_label, 'Tab 3')
layout.addWidget(tabwidget, 0,0)

#A file select dialog
#fileName = QFileDialog.getOpenFileName(window, 'Open file', '/home')
#print(fileName[0])

window.show()
sys.exit(app.exec())

