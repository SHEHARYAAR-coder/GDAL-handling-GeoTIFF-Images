```markdown
# Automatic Georeferencing System

Automatic Georeferencing System is a desktop application designed to automatically georeference aerial images by aligning them with a georeferenced TIF reference file. The application uses feature detection, matching, and homography estimation to compute the geographic coordinates (latitude and longitude) of selected points in an aerial image.

## Features

- **Automatic Feature Detection:** Uses the AKAZE algorithm to detect keypoints and compute descriptors in both the reference and aerial images.
- **Robust Matching:** Employs brute-force matching with a ratio test to filter out poor matches.
- **Homography Estimation:** Uses RANSAC to estimate a homography matrix that maps points between images.
- **Interactive GUI:** Built with PyQt5, the interface allows users to load images and obtain geospatial coordinates via simple double-click actions.
- **Real-Time Projection:** Projects clicked points from the aerial image to the georeferenced coordinate system and displays the corresponding latitude and longitude.

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.6+**
- **GDAL:** For geospatial data handling. ([GDAL Installation](https://gdal.org/download.html))
- **PyQt5:** For building the GUI.
- **OpenCV (opencv-python):** For image processing and feature detection.
- **NumPy:** For numerical operations.
- **Matplotlib:** For optional image plotting.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your_username/automatic-georeferencing-system.git
   cd automatic-georeferencing-system
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Required Dependencies:**

   Create a `requirements.txt` file with the following content:

   ```
   gdal
   PyQt5
   opencv-python
   numpy
   matplotlib
   ```

   Then install using pip:

   ```bash
   pip install -r requirements.txt
   ```

   **Note:** GDAL installation may require additional system dependencies. Please refer to the [GDAL documentation](https://gdal.org/download.html) for detailed instructions.

## Usage

1. **Prepare the Reference File:**
   
   Ensure that you have the reference TIF file (e.g., `reference1Km.tif`) in the project directory.

2. **Run the Application:**

   ```bash
   python main.py
   ```

   This command will launch the Automatic Georeferencing System window.

3. **Load an Aerial Image:**

   - Click the **"Load Image"** button.
   - Select an aerial image (PNG, JPG, etc.) from your file system.

4. **Obtain Geospatial Coordinates:**

   - Double-click on any point in the loaded aerial image.
   - The application will compute and display the projected coordinates (latitude and longitude) based on the reference TIF file.

## How It Works

- **Data Loading:**  
  The application uses GDAL to load a georeferenced TIF file and the user-selected aerial image.
  
- **Feature Detection & Matching:**  
  AKAZE is applied to both images to detect keypoints and compute descriptors. A brute-force matcher (with a ratio test) finds reliable feature matches.
  
- **Homography Estimation:**  
  With sufficient good matches, a homography matrix is computed using RANSAC, allowing the transformation of points between the aerial image and the georeferenced reference.
  
- **Coordinate Projection:**  
  When the user double-clicks on the aerial image, the clicked pixel is transformed using the homography matrix, and the corresponding geographic coordinates are computed using the geotransform information from the TIF file.

## Example Code

```python
from osgeo import gdal
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np

class Automatic_Georeferencing_System(QMainWindow):
    def __init__(self, filepathTIF):
        super().__init__()
        self.TIFFile = gdal.Open(filepathTIF)
        self.aerialFile = None
        self.init_ui()

    def init_ui(self):
        self.image_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def loadImage(self, file_path):
        self.aerialFile = gdal.Open(file_path)
        self.aerialimg_data = self.aerialFile.GetRasterBand(1).ReadAsArray()
        q_image = QImage(self.aerialimg_data, self.aerialimg_data.shape[1], self.aerialimg_data.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication([])
    viewer = Automatic_Georeferencing_System("reference1Km.tif")
    viewer.show()
    app.exec_()
```

## Contributing

Contributions are welcome! If you have suggestions, improvements, or bug fixes, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```
