---
title: Avoiding obstacles
difficulty: 4
language: MicroPython
requires: Laptop with Thonny and a Robot
version: "1.1"
link: https://orionrobots.co.uk/dojo/obstacles
pdf_link: https://drive.google.com/file/d/1Qa1zQxD-eVhmJGW7Cc5yrJgFLwUlNRDs/view  # the published PDF in the shared drive
hero: [hero-ultrasonic-sensors.png, hero-test-arena.png]
---
The robots can’t see the way we see 👀, they see with a couple of distance sensors. We can use them to drive around the world without bumping into things 🦺⛑️.

See how the robot can drive itself around a test area 🚧, avoid walls 🧱 and other robots 🤖.
<!-- /intro -->

Here’s what we’ll do:

1. **Read distance sensors**: Connect to the distance sensors on the robot
2. **Stop when too close**: Write code to stop when too close to an obstacle
3. **Bounce away**: Turn away when too close and keep driving

Let’s start building

## Step 1 - Read the distance!

These sensors use echo-location like a bat. They “ping” an object, and receive a response. By timing how long it took, they can see how far things are from the robot.

The robots all have an `hcsr04` library on board for communicating with these sensors. Let’s test this:

```python {note="2|hcsr04|A library to talk to the sensor;4|HCSR04|^1Objects to talk with sensors;4|trigger_pin|Trigger - pin to start a “ping”;5|echo_pin|Echo - pin to receive a “pong”;8|distance_cm|Get a distance from the sensors;10|print|Print the distances;11|sleep|Wait a bit before doing it again"}
import time
from hcsr04 import HCSR04

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

while True:
    left_distance = right_sensor.distance_cm()
    right_distance = left_sensor.distance_cm()
    print(left_distance, right_distance)
    time.sleep(0.1)
```

:::: side
::: fig
![Ping and pong: the sensor chirps, and listens for the echo](ping-pong.png){style="width:62mm"}
:::
::: text
These sensors use ultrasonic echo-location - like bats 🦇!\
They chirp a high frequency sound (that you probably cannot hear), and listen for the echo back to determine how far things are away.

When you run this, you will see the distances for the two sensors printed in the shell panel. Try moving your hands in front of the sensors.

```text
16.70103 25.36082
16.71821 24.48454
16.71821 24.48454
16.71821 24.48454
16.71821 24.50172
16.70103 25.36082
16.71821 25.36082
16.71821 25.36082
```
:::
::::

We can make it more visual with the plotter:

![Thonny with the View menu open and Plotter ticked, plotting the two sensors](thonny-plotter.png){style="width:170mm"}

Now we have some sensor input, how can we use it?

## Step 2 - Stop before we hit!

We can use this to make our robot a little smarter. We can make sure it stops before it hits an object.

Let’s add motors into our imports (from <https://tinyurl.com/robot-make-it-drive>):

```python {note="2|motors|Import the motors<br>library so we can<br>move;8|THRESHOLD|^Use these to<br>control the speed<br>and stopping<br>threshold;11|try|Use try/finally to<br>ensure it stops,<br>even with errors;17|distance_cm|Get the sensor data;21|if|If we are too close;24|break|Then break out<br>of the loop;27|finally|Stop the motors<br>here when we leave<br>the loop for any<br>reason"}
import time
import motors
from hcsr04 import HCSR04

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

THRESHOLD = 30
SPEED = 0.7

try:
    motors.set_speed(motors.left, SPEED)
    motors.set_speed(motors.right, SPEED)

    while True:
        # Sense
        left_distance = right_sensor.distance_cm()
        right_distance = left_sensor.distance_cm()
        print(left_distance, right_distance)
        # Think
        if left_distance < THRESHOLD or \
           right_distance < THRESHOLD:
            # Act
            break
        time.sleep(0.1)

finally:
    motors.stop_all()
```

Test this on the stand first, you should see the robot start driving, and stop as soon as you wave a hand in front of it. You can then paste that code into `main.py`, and put the robot in the test area. It should drive and stop before it hits a barrier or other robot.\
We’ve got some commented sections, **sense**, **think** and **act**.

Is 30 the right distance? You can increase the speed, but you may need to increase the distance with it. How close can you get the robot to stop without hitting something? You can change the `SPEED` or `THRESHOLD` settings to make it faster, and stop closer or further from the target.

## Step 3 - Bounce!

Stopping means it won’t hit something, but we would like the robot to keep on driving. We need to turn the robot by slowing down one of the motors. Let’s change our settings to add that:

```python {note="9|TURN_SPEED|Tuning variables<br>now have a turn<br>speed - for turning<br>away from the<br>obstacle;19|SPEED|^We start by<br>assuming both<br>motors go forward;21|if|But if either<br>sensor is too<br>close, it goes<br>back by the<br>turn speed;26|set_speed|We then apply<br>those speeds to<br>the motors"}
import time
import motors
from hcsr04 import HCSR04

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

SPEED = 0.5
TURN_SPEED = 0.3
THRESHOLD = 30

try:
    while True:
        # Sense
        left_distance = left_sensor.distance_cm()
        right_distance = right_sensor.distance_cm()
        print(left_distance, right_distance)
        # Think
        left_speed = SPEED
        right_speed = SPEED
        if left_distance < THRESHOLD:
            right_speed = -TURN_SPEED
        elif right_distance < THRESHOLD:
            left_speed = -TURN_SPEED
        # act
        motors.set_speed(motors.left, left_speed)
        motors.set_speed(motors.right, right_speed)
        time.sleep(0.01)
finally:
    motors.stop_all()
```

Test this on the stand again, and depending on which sensor you put your hand close to, a different wheel will spin.

You can now experiment with the basic code in a test area. You can tune the speeds and thresholds for a more daring robot!

## What else could you add?

The robot turns suddenly at a wall. Could you link the speed that it turns to how close it is to a wall for more subtle behaviour?
