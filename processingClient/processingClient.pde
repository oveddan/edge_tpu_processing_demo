import gohai.glvideo.*;
GLCapture video;


PGraphics pg;
  

BroadcastThread broadcastThread;
ReceiverThread receiverThread;

void setup() {
  size(640, 480, P2D); 
  pg = createGraphics(300, 300, P2D);
  broadcastThread = new BroadcastThread();
  broadcastThread.start();
  receiverThread = new ReceiverThread(this);
  receiverThread.start();

  // this will use the first recognized camera by default
  video = new GLCapture(this);

  video.start();
}

//PImage img;

PImage downloadScaledImage() {
  pg.beginDraw();
  pg.image(video, 0, 0, 300, 300);
  pg.endDraw();
  return pg.copy();
}

void draw() {
  //background(0);
  // If the camera is sending new data, capture that data
  if (video.available()) {
    video.read();
    broadcastThread.update(downloadScaledImage());
  }
  // Copy pixels into a PImage object and show on the screen
  image(video, 0, 0, 640, 480);  
  //println(frameRate);
}
