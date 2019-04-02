

int getEnvValueOrDefault(String name, int defaultValue) {
  String value = System.getenv(name);
  
  if (value != null) {
    return int(value);
  } else
    return defaultValue;
}

String getEnvValueOrDefault(String name, String defaultValue) {
  String value = System.getenv(name);
  //println("Broadcast host:", portString);
  
  if (value != null) {
    return value;
  } else
    return defaultValue;
}
