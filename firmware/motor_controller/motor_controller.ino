const int LEFT_PWM = 5;
const int LEFT_DIR = 4;
const int RIGHT_PWM = 6;
const int RIGHT_DIR = 7;
const unsigned long WATCHDOG_MS = 500;

String line = "";
unsigned long lastCommand = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LEFT_PWM, OUTPUT);
  pinMode(LEFT_DIR, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT);
  pinMode(RIGHT_DIR, OUTPUT);
  stopMotors();
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(line);
      line = "";
    } else if (c != '\r') {
      line += c;
    }
  }

  if (millis() - lastCommand > WATCHDOG_MS) {
    stopMotors();
  }
}

void handleLine(const String &text) {
  if (text.startsWith("S")) {
    stopMotors();
    lastCommand = millis();
    return;
  }

  if (text.startsWith("M ")) {
    int space = text.indexOf(' ', 2);
    if (space < 0) {
      return;
    }
    float left = text.substring(2, space).toFloat();
    float right = text.substring(space + 1).toFloat();
    setMotor(LEFT_PWM, LEFT_DIR, left);
    setMotor(RIGHT_PWM, RIGHT_DIR, right);
    lastCommand = millis();
  }
}

void setMotor(int pwmPin, int dirPin, float speed) {
  speed = constrain(speed, -1.0, 1.0);
  digitalWrite(dirPin, speed >= 0 ? HIGH : LOW);
  analogWrite(pwmPin, (int)(fabs(speed) * 255));
}

void stopMotors() {
  analogWrite(LEFT_PWM, 0);
  analogWrite(RIGHT_PWM, 0);
}
