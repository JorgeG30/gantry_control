//This code will check the state of the motor encoder

//These pins will be used for the A, B, and N pins
int A = 2;
int B = 3;
int N = 4;

//These variables will store the state of pin A
byte currStateA;
byte prevStateA;
byte stateN;

//These variables will store the total revolutions and the 1/4 steps of the motor
int steps = 0;
int revs = 0;

void setup(){

  //Begin serial monitor
  Serial.begin(9600);
  
  //Set up pins as inputs
  int c;
  for(c = 2; c < 5; c++){
    pinMode(c, INPUT);
  }

  //Read initial state of A and B
  prevStateA = digitalRead(A);
  
}

void loop(){

  //Read current state of A
  currStateA = digitalRead(A);

  //Check states
  if(prevStateA != currStateA){
    if(digitalRead(B) != currStateA){
      steps++;
    }else{
      steps--;
    }
  }

  //Read the pin state of N
  stateN = digitalRead(N);

  //Check the state of N
  if(stateN == HIGH)
    revs++;

  Serial.print("Number of 1/4 steps: ");
  Serial.println(steps);
  Serial.print("Number of Revolutions: ");
  Serial.println(revs);
  
  //Change prev state to current state
  prevStateA = currStateA;

  
}

