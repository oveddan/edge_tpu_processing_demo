import java.nio.charset.*;
import processing.net.*;

class ReceiverThread extends Thread {
  // This is the port we are sending to
  int port = 9101;   
  
  byte[] buffer = new byte[65536];
  
  DatagramSocket ds;
  Client client;
  
  boolean running;
  boolean available;
  
  float[][] boxes = new float[10][4];
  String[] labels = new String[10];
  int numResults = 0;
  
  ReceiverThread(PApplet parent) {
    running = false;
    available = true;
    
    client = new Client(parent, "127.0.0.1", port);
  }
  
  void start(){
    running = true;
    super.start();
  }
  
  void run() {
    while (running) {
      available = checkForResult();
      available = true;
    }
  }
  
  boolean checkForResult(){
    if (client.available() > 0) {
      
      String base64String = client.readString();
      
      
      try {
        JSONObject obj = parseJSONObject(base64String);
        
        println("good json");
      } catch (RuntimeException e) {
        println("bad json: ", base64String);
        e.printStackTrace();
        return false;
      }
      
      return true;
    } else {
      return false;
    }
  }
}
