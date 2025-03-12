from osgeo import gdal
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget,QPushButton,QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import matplotlib.pyplot as plt

class Automatic_Georeferencing_System(QMainWindow):
    def __init__(self, filepathTIF):
        super().__init__()
        self.TIFFile = gdal.Open(filepathTIF)
        self.aerialFile = None
        self.init_ui()

    def init_ui(self):
        # Create central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()

        # Create label to display image
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # Create labels to display coordinates
        self.x_label = QLabel(self)
        layout.addWidget(self.x_label)

        self.y_label = QLabel(self)
        layout.addWidget(self.y_label)

        self.lat_label = QLabel(self)
        layout.addWidget(self.lat_label)

        self.lon_label = QLabel(self)
        layout.addWidget(self.lon_label)

        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.loadImage)
        layout.addWidget(self.load_button)

        # Set layout to central widget
        central_widget.setLayout(layout)

        # Set up mouse tracking for the image label
        self.image_label.setMouseTracking(True)
        self.image_label.mouseDoubleClickEvent = self.on_mouse_move

    def loadImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg);;All Files (*)", options=options)
        if file_path:
            self.aerialFile = gdal.Open(file_path)
            # Display satellite image using QPixmap
            self.aerialimg_data = self.aerialFile.GetRasterBand(1).ReadAsArray()

            height, width = self.aerialimg_data.shape

            q_image = QImage(self.aerialimg_data, width, height, width, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

    def on_mouse_move(self, event):
        self.clickedXPoint, self.clickedYPoint = event.x(), event.y()

        # Get pixel values
        pixel_values = self.aerialFile.ReadAsArray(self.clickedXPoint, self.clickedYPoint, 1, 1)

        self.compute()

    def compute(self):  
        akaze = cv2.AKAZE_create()

        # Detect keypoints and compute descriptors for both images
        self.aerialkeypoints, self.aerialdescriptors = akaze.detectAndCompute(self.aerialimg_data, None)
        self.tifkeypoint,self.tifdescriptor= akaze.detectAndCompute(self.TIFFile.GetRasterBand(1).ReadAsArray(), None)
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(self.tifdescriptor, self.aerialdescriptors, k=2)

        # Apply ratio test to select good matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
       
        # Minimum number of matches required for homography
        MIN_MATCH_COUNT = 10
        if len(good_matches) >= MIN_MATCH_COUNT:
            src_pts = np.float32([self.tifkeypoint[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([self.aerialkeypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
           
            # Estimate homography matrix using RANSAC (Inverse Warping!)
            homography, _ = cv2.findHomography(dst_pts,src_pts, cv2.RANSAC, 5.0)

            # Create a numpy array with the clicked pixel coordinates
            clicked_pixel = np.array([[[self.clickedXPoint, self.clickedYPoint ]]], dtype=np.float32)

            # Use the Homography matrix to project the pixel
            projected_pixel = cv2.perspectiveTransform(clicked_pixel, homography)

            # Extract the x and y coordinates of the projected pixel
            ReferenceXPoint, ReferenceYPoint = projected_pixel[0][0]
           
            geo_transform = self.TIFFile.GetGeoTransform()
            ReferenceLongitute = geo_transform[0] + self.clickedXPoint * geo_transform[1]
            ReferenceLatitute = geo_transform[3] + self.clickedYPoint * geo_transform[5]
      
            coordinate_label = QLabel(self)
            coordinate_label.setText(f"Clicked Coordinates: ({self.clickedXPoint:.2f}, {self.clickedYPoint:.2f})\nLatitude: {ReferenceLatitute:.6f}\nLongitude: {ReferenceLongitute:.6f}")

            coordinate_label.setGeometry(self.clickedXPoint, self.clickedYPoint, 300, 150)  
        
            coordinate_label.setStyleSheet("color: rgb(0, 0, 139); background-color : white;")

            coordinate_label.show()


if __name__ == '__main__':
    app = QApplication([])

    filepathTIF = "reference1Km.tif"
   
    viewer = Automatic_Georeferencing_System(filepathTIF)
    viewer.show()
    app.exec_()