# Custom Region Object Counter - YOLOv8

This web application uses Python, Flask, and the YOLOv8 model to accurately detect and count objects in video data. The YOLOv8 model, pre-trained on the COCO dataset, identifies objects in the input video. A custom region of interest (ROI) function allows users to define areas for precise counting.

For tracking, the ByteTrack algorithm ensures accurate identification of individual objects as they move through the specified region. The user-friendly web interface enables video uploads, ROI selection, and real-time tracking and counting of objects.

![Demo](demo/demo.gif)

**Example Use Case:**  
Detecting and counting cattle within a designated area in farm surveillance videos.

### Step 1: Clone the Repository
Start by cloning the repository to your local machine.

```bash
git clone https://github.com/Kongesque/custom-region-object-counter-YOLOV8.git
cd custom-region-object-counter-YOLOV8
```

### Step 2: Install Dependencies
Ensure you have Python 3.x installed. Then, install the required packages by running:

```bash
pip install -r requirements.txt
```

## Step 3: Run the Application

Start the application:

```bash
python3 app.py
```

Visit `http://127.0.0.1:5000` in your web browser.

