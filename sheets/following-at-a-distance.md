---
title: Following at a distance
draft: true  # work in progress: built locally, never copied to the shared drive by publish-sheets
difficulty: 5
language: MicroPython
requires: Laptop with Python, Thonny and a Robot kit
version: "0.2"
link: https://orionrobots.co.uk/dojo/follow  # planned short link, no site rule yet
hero: [hero-placeholder-1.png, hero-placeholder-2.png]  # the source doc's cover images (fireworks, from its template): replace
---
Use distance sensors to follow an object like a puppy!

We’ll build code to intelligently follow a moving object in front of a robot, exploring the PID algorithm when doing so.

We recommend you have done the Obstacle avoiding sheet first.
<!-- /intro -->

Here’s what we’ll do:

1. **Stop when ready**: we can start with a robot that stops when it’s a distance away from an object.
2. **Close the gap**: we’ll get the robot to quickly drive to close a gap.
3. **Keeping pace**: Follow a moving object without bunny hopping
4. **Calm it down**: Tame it so it does jump when let go
5. **Adding brakes**: Making your robot smoother

Let's make a robot puppy dog!

## Step 1 - Stop when ready!

The robot has a pair of distance sensors. Let’s make the robot stop when they are too close to an object.

```python {note="1|import|Import the sensor and motor<br>moving libraries;6|left_sensor|Set up the sensors;8|THRESHOLD|Set the motor speed and<br>stopping threshold;11|try|Use try/finally to ensure it<br>stops, even with errors;18|left_distance|Get the sensor data;22|if|If we are too close;25|break|Then break out of the loop;28|stop_all|Stop motors when we leave<br>the loop for any reason"}
import time
from hcsr04 import HCSR04
import motors

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

THRESHOLD = 30
SPEED = 0.7

try:
    motors.set_speed(motors.left, SPEED)
    motors.set_speed(motors.right, SPEED)

    while True:

        # Sense
        left_distance = left_sensor.distance_cm()
        right_distance = right_sensor.distance_cm()

        # Think
        if left_distance < THRESHOLD or \
            right_distance < THRESHOLD:
            # act
            break
        time.sleep(0.1)
finally:
    motors.stop_all()
```

Try running this. When the robot is closer than 30cm from the target, it should stop. Try changing this for different thresholds.

If you move the object, you’ll need to run the code again to see the robot move.

## Step 2 - Close the gap!

We can make the robot try to keep a gap between itself and an object in front. Add this code:

```python {note="1|SET_POINT|Aim for this distance - a set point;4|p_factor|The p_factor setting controls<br>how strongly it responds.;6|calculate|The controller responds proportionally<br>to a gap. A greater gap means a<br>greater response"}
SET_POINT = 10

class Controller:
    p_factor = 0.03

    def calculate(self, gap):
        return gap * self.p_factor
```

This makes a `Controller` class and a `SET_POINT` instead of a threshold. This is a bit closer at 10cm.

Let’s make the rest of the code use it - update the numbered lines:

```python {note="1|try|Use try/finally to ensure it<br>stops, even with errors;7|left_distance|Get the sensor data;11|left_gap|Get the gap between where we are<br>and the set point;15|left_speed|Use the gap to get a speed<br>for each motor;19|set_speed|Set the motor speeds;23|stop_all|Stop the motors here when we leave<br>the loop for any reason"}
try:
    left_controller = Controller()
    right_controller = Controller()

    while True:
        # Sense
        left_distance = left_sensor.distance_cm()
        right_distance = right_sensor.distance_cm()

        # Think
        left_gap = left_distance - SET_POINT
        right_gap = right_distance - SET_POINT
        print(left_gap, right_gap)

        left_speed = left_controller.calculate(left_gap)
        right_speed = right_controller.calculate(right_gap)

        # act
        motors.set_speed(motors.left, left_speed)
        motors.set_speed(motors.right, right_speed)
        time.sleep(0.1)
finally:
    motors.stop_all()
```

When you run this, the robot should try to get about 30 cm from something held in front - for both motors. You can try changing the proportional number. A smaller value means the response will be slower, but more smooth. A higher value will mean a faster and stronger response, but it could get jittery.

Our motor control goes between 1 and -1, we usually want smaller speeds than all the way, and at less than 10cm we should slow down. So 1/10 or 0.1 is a reasonable maximum. But much lower makes it a smoother response.

## Step 3 - Keeping pace!

If you walk, it will jump to follow, but it isn’t keeping pace. We can add an **integral** so it can correct for small constant changes like someone walking away from it.\
**Replace only** the Controller section with this (the other code stays the same):

```python {note="2|TIME_STEP|We add a TIME_STEP setting so all<br>code uses the same timing;6|i_factor|We add an i factor - controlling how<br>much influence the integral has<br>on the result.;8|integral|The integral adds up gaps over time;11|TIME_STEP|Calculate the gap multiplied<br>by passed time;13|i_factor|Then multiply by the i_factor and<br>add to the control response."}
SET_POINT = 10
TIME_STEP = 0.1

class Controller:
    p_factor = 0.03
    i_factor = 0.001

    integral = 0

    def calculate(self, gap):
        self.integral += gap * TIME_STEP
        return (gap * self.p_factor +
            self.integral * self.i_factor)
```

If you send the updated code to the robot, you should find that you can walk with the robot following behind you. Your shoes and trousers may be hard for the sensors to read, so holding a barrier or something rigid and moving that may work better.

If it’s still hopping, adjust the `i_factor` up a bit, but don’t let it get too high.

If it’s failing to stop when you stop or slow when you slow, reduce the `i_limit`, the integral can get very high and be stuck there for a while

## Step 4 - Calm it down!

Try this, start your robot a little further than the distance, and hold it, watch the wheels get fast. Now let it go and it will drive really quickly, and probably crash (careful!)

We need to make sure that integral can’t get too excited!

```python {note="4|i_limit|A limit stops it growing out of control;11|i_limit|Apply limits so it isn’t out of control"}
class Controller:
    p_factor = 0.02
    i_factor = 0.001
    i_limit = 50

    integral = 0

    def calculate(self, gap):
        self.integral += gap * TIME_STEP
        if self.integral > self.i_limit:
            self.integral = self.i_limit
        elif self.integral < -self.i_limit:
            self.integral = -self.i_limit
        return (gap * self.p_factor +
            self.integral * self.i_factor)
```

## Step 5 - Adding brakes!

By now, your robot should be able to follow an object by speeding up when it is too far away and slowing down when it gets closer.

But even a good follower can still be a bit clumsy. **Replace only** the Controller section with this (the other code stays the same):

```python {note="3|i_factor|We now have an integral and i factor.<br>The integral grows as an error remains.<br>A limit stops it growing out of control.;7|last_time|The integral adds up error over time;17|time_change|We add the gap multiplied by passed time;20|if|Apply limits so it isn’t out of control;23|i_factor|Then multiply by the i_factor and add<br>to the control response."}
class Controller:
    p_factor = 0.02
    i_factor = 0.001
    i_limit = 50

    integral = 0
    last_time = time.ticks_ms()

    def get_time_change(self):
        current_time = time.ticks_ms()
        time_change = time.ticks_diff(self.last_time, current_time) / 1000
        self.last_time = current_time
        return time_change

    def calculate(self, gap):
        time_change = self.get_time_change()
        self.integral += gap * time_change
        if self.integral > self.i_limit:
            self.integral = self.i_limit
        if self.integral < -self.i_limit:
            self.integral = - self.i_limit
        return gap * self.p_factor + \
                self.integral * self.i_factor
```

- start with a very small `d_factor`
- if the robot gets twitchy, reduce `d_factor`
- if it still feels clumsy or overshoots, try increasing it a little

## What else could you add?

&lt;Ideas to extend the project, in increasing complexity&gt;\
&lt;Maybe where to get reference material to help&gt;
