import gohai.glvideo.*;
GLCapture video;


PGraphics inputImage;
PGraphics resultsImage;

int captureW = 640;
int captureH = 480;

float aspect = captureW * 1.0 / captureH;

// the width and height of the input image for
// object detection
int inputW = 300;
int inputH = 300;

int resizeW = inputW;
// resize but maintain aspect ratio
int resizeH = floor(inputW / aspect);
int paddingW = 0;
// pad image to fit input size
int paddingH = (inputH - resizeH) / 2;

BroadcastThread broadcastThread;
ResultsReceivingThread receiverThread;

boolean debugInputImage = false;
boolean drawResults = true;

void setup() {
  size(640, 480, P2D); 
  inputImage = createGraphics(inputW, inputH, P2D);
  resultsImage = createGraphics(width, height, P2D);
  
  // start threads
  broadcastThread = new BroadcastThread();
  broadcastThread.start();
  receiverThread = new ResultsReceivingThread(this);
  receiverThread.start();

  // setup graphics
  String[] devices = GLCapture.list();
  println("Available cameras:");
  printArray(devices);
  
  // use the first camera
  video = new GLCapture(this, devices[0], captureW, captureH, 25);

  video.start();
}

PImage captureAndScaleInputImage() {
  inputImage.beginDraw();
  inputImage.background(0);
  // draw video into input image, scaling while maintaining the
  // aspect ratio
  inputImage.image(video, paddingW, paddingH, resizeW, resizeH);
  inputImage.endDraw();
  return inputImage.copy();
}

void updateResultsImage() {
  int numDetections = receiverThread.getNumDetections();
  float[][] boxes = receiverThread.getBoxes();
  String[] labels = receiverThread.getLabels();
  
  resultsImage.beginDraw();
  resultsImage.clear();
  resultsImage.noFill();
  resultsImage.stroke(#ff0000);
  
  for(int i = 0; i < numDetections; i++) {
    float[] box = boxes[i];
    
    String label = labels[i];
    
    resultsImage.rect(box[0], box[1], box[2] - box[0], box[3] - box[1]);
    
    if (label != null)
      resultsImage.text(label, box[0], box[1]);
  }
  
  resultsImage.endDraw();
}

void draw() {
  background(0);
  // If the camera is sending new data, capture that data
  if (video.available()) {
    video.read();
    broadcastThread.update(captureAndScaleInputImage());
  }
  // Copy pixels into a PImage object and show on the screen
  image(video, 0, 0, width, height);  
  
  if (debugInputImage)
    image(inputImage, 0, 0, inputW, inputH);
  
  if (drawResults) {
    if (receiverThread.newResultsAvailable()) {
      updateResultsImage();
    }
    image(resultsImage, 0, 0, width, height);
  }
}
