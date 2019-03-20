import java.nio.charset.*;
import processing.net.*;

static final int MAX_DETECTED_OBJECTS = 20;

class ReceiverThread extends Thread {
  // This is the port we are sending to
  int port = 9101;   
  
  byte[] buffer = new byte[65536];
  
  DatagramSocket ds;
  //Client client;
  
  boolean running;
  boolean available;
  
  float[][] boxes = new float[MAX_DETECTED_OBJECTS][4];
  String[] labels = new String[MAX_DETECTED_OBJECTS];
  int numDetections = 0;
  
  ReceiverThread(PApplet parent) {
    running = false;
    available = true;
    
    //client = new Client(parent, "127.0.0.1", port);
    try {
      ds = new DatagramSocket(port);
    } catch (SocketException e) {
      e.printStackTrace();
    }
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
  
  
  byte[] receiveBuffer = new byte[65536];
  
  boolean checkForResult() {
    DatagramPacket p = new DatagramPacket(receiveBuffer, receiveBuffer.length);
    
    try {
      ds.receive(p);
    } catch (IOException e) {
      e.printStackTrace();
      return false;
    }
    
    byte[] data = p.getData();
    
    String responseString = (new String(data)).trim();
    
    String mostRecentResults = getValidMostRecentResult(responseString);
      
    if (mostRecentResults == null)
      return false;
    
    return parseResults(mostRecentResults);
  }
  
  String getValidMostRecentResult(String responseString) {
    if (responseString.endsWith("|")) {
      return getValidMostRecentResult(responseString.substring(0, responseString.length() - 2));
    }
    
    String[] allResultStrings = responseString.split("|");
    
    return allResultStrings[allResultStrings.length-1];
  }
  
  boolean parseResults(String resultsString) {
    if (resultsString == "") {
      numDetections = 0;
      return true;
    }
    JSONObject obj;
    
    try {
      obj = parseJSONObject(resultsString);
    } catch (RuntimeException e) {
      print("Invalid json to parse:");
      println(resultsString);
      e.printStackTrace();
      return false;
    }
    
    JSONArray resultsList = obj.getJSONArray("results");
    
    float scaleW = 640.0 / 300.0;
    float scaleH = 480.0 / 300.0;
    
    for(int i = 0; i < resultsList.size(); i++) {
      JSONObject result = resultsList.getJSONObject(i);
      
      labels[i] = result.getString("label");
      
      JSONArray box = result.getJSONArray("box");
      
      boxes[i][0] = box.getFloat(0) * scaleW;
      boxes[i][1] = box.getFloat(1) * scaleH;
      boxes[i][2] = box.getFloat(2) * scaleW;
      boxes[i][3] = box.getFloat(3) * scaleH;
    }
    
    return true;
  }
  
  //boolean checkForResult(){
  //  if (client.available() > 0) {
      
  //    String base64String = client.readString();
      
      
  //    try {
  //      JSONObject obj = parseJSONObject(base64String);
        
  //      println("good json");
  //    } catch (RuntimeException e) {
  //      println("bad json: ", base64String);
  //      e.printStackTrace();
  //      return false;
  //    }
      
  //    return true;
  //  } else {
  //    return false;
  //  }
  //}
}
