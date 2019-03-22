import gohai.glvideo.*;
GLCapture video;

// CONFIGURATION
int captureW = 320;
int captureH = 240;

// the width and height of the input image for
// object detection
int inputW = 300;
int inputH = 300;

int outputW = 320;
int outputH = 240;

// drawing config
boolean debugInputImage = false;
boolean drawResults = true;

PGraphics inputImage;
PGraphics resultsImage;

float aspect = captureW * 1.0 / captureH;

int resizeW = inputW;
// resize but maintain aspect ratio
int resizeH = floor(inputW / aspect);
int paddingW = (inputW - resizeW) / 2;
// pad image to fit input size
int paddingH = (inputH - resizeH) / 2;

int fps = 25;

BroadcastThread broadcastThread;
ResultsReceivingThread receiverThread;

void settings(){
  size(outputW, outputH, P2D);
  println(resizeW, resizeH, paddingW, paddingH);
}

void setup() {
  inputImage = createGraphics(inputW, inputH, P2D);
  resultsImage = createGraphics(outputW, outputH, P2D);
  frameRate(fps);
  
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
  video = new GLCapture(this, devices[0], captureW, captureH, fps);

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

float padAndScale(float value, float padding, float scale) {
  return (value - padding) * scale;
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
      
    float scaleWH = captureW * 1.0 / inputW;
    
    float x1 = padAndScale(box[0], paddingW, scaleWH);
    float y1 = padAndScale(box[1], paddingH, scaleWH);
    float x2 = padAndScale(box[2], paddingW, scaleWH);
    float y2 = padAndScale(box[3], paddingH, scaleWH);
    
    String label = labels[i];
    
    resultsImage.rect(x1, y1, x2 - x1, y2 - y1);
    
    if (label != null)
      resultsImage.text(label, x1, y1);
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
  image(video, 0, 0, outputW, outputH);  
  
  if (debugInputImage)
    image(inputImage, 0, 0, inputW, inputH);
  
  if (drawResults) {
    if (receiverThread.newResultsAvailable()) {
      updateResultsImage();
    }
    image(resultsImage, 0, 0, outputW, outputH);
  }
}
