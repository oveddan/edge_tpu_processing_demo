import javax.imageio.*;
import java.awt.image.*; 
import java.net.*;
import java.io.*;

class BroadcastThread extends Thread {
  // This is the port we are sending to
  int clientPort = getRemoteBroadcastPort(); 
  String clientHost = getRemoteBroadcastHost();
  // This is our object that sends UDP out
  DatagramSocket ds; 
  PImage lastImage;
  boolean newFrame = false;
  boolean running;
  
  BroadcastThread() {
    //println("Host and port:", host, port);
    // Setting up the DatagramSocket, requires try/catch
    try {
      ds = new DatagramSocket();
    } catch (SocketException e) {
      e.printStackTrace();
    }
  }
  
  void start(){
    running = true;
    super.start();
  }
  
  // we must implement run, this gets triggered by start()
  void run() {
    while (running) {
      if (newFrame) {
        broadcast(lastImage);
      }
    }
  }
  
  void update(PImage img) {
    lastImage = img;
    newFrame = true;
  }
  
  // Function to broadcast a PImage over UDP
  // Special thanks to: http://ubaa.net/shared/processing/udp/
  // (This example doesn't use the library, but you can!)
  void broadcast(PImage img) {
    // We need a buffered image to do the JPG encoding
    BufferedImage bimg = new BufferedImage(img.width,img.height, BufferedImage.TYPE_INT_RGB );
  
    // Transfer pixels from localFrame to the BufferedImage
    img.loadPixels();
    bimg.setRGB( 0, 0, img.width, img.height, img.pixels, 0, img.width);
  
    // Need these output streams to get image as bytes for UDP communication
    ByteArrayOutputStream baStream  = new ByteArrayOutputStream();
    BufferedOutputStream bos    = new BufferedOutputStream(baStream);
  
    // Turn the BufferedImage into a JPG and put it in the BufferedOutputStream
    // Requires try/catch
    try {
      ImageIO.write(bimg, "jpg", bos);
    } 
    catch (IOException e) {
      e.printStackTrace();
    }
  
    // Get the byte array, which we will send out via UDP!
    byte[] packet = baStream.toByteArray();
  
    // Send JPEG data as a datagram
    println("Sending datagram with " + packet.length + " bytes");
    try {
      ds.send(new DatagramPacket(packet,packet.length, InetAddress.getByName(clientHost),clientPort));
      ds.send(new DatagramPacket(packet,packet.length, InetAddress.getByName(getRemoteBroadcastHost()),getRemoteBroadcastPort()));
    } 
    catch (Exception e) {
      e.printStackTrace();
    }
  }
}

int getRemoteBroadcastPort() {
  String portString = System.getenv("BROADCAST_PORT");
  
  if (portString != null) {
    return int(portString);
  } else
    return 9002;
}

String getRemoteBroadcastHost() {
  String portString = System.getenv("BROADCAST_HOST");
  //println("Broadcast host:", portString);
  
  if (portString != null) {
    return portString;
  } else
    return "192.168.86.170";
}
