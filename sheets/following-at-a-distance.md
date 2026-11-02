---
title: Following at a distance
difficulty: 5
language: MicroPython
requires: Laptop with Python, Thonny and a Robot kit
version: "0.2"
link: https://orionrobots.co.uk/dojo/follow  # planned short link, no site rule yet
hero: [hero-robot-following-feet.jpg, hero-robot-sensors-front.jpg]
---
Use distance sensors to follow an object like a puppy!

We’ll build code to intelligently follow a moving object in front of a robot, exploring the PID algorithm when doing so.

We recommend you have done the Obstacle avoiding sheet first.
<!-- /intro -->

Here’s what we’ll do:

1. **Stop before we hit**: we revisit the robot that stops when it’s a distance away from an object.
2. **Close the gap**: we’ll get the robot to quickly drive to close a gap.
3. **Keeping pace**: Follow a moving object without bunny hopping
4. **Calm it down**: Tame it so it does jump when let go
5. **Adding brakes**: Making your robot smoother

Let's make a robot puppy dog!

## Step 1 - Stop before we hit!

This is the code from Step 2 of the Avoiding obstacles sheet: the robot has a pair of distance sensors, and stops when they are too close to an object. Let’s revisit it, as we’re going to build on it.

```python {note="8|THRESHOLD|Set the motor speed and<br>stopping threshold;22|if|If we are too close"}
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

Try running this. When the robot is closer than 30cm from the target, it should stop. If you move the object, you’ll need to run the code again to see the robot move. The reset button will work if you save it to the robot as main.py.

Try changing this for different thresholds.

## Step 2 - Close the gap!

We can make the robot try to keep a gap between itself and an object in front. Add this code below `SPEED` and above `try`:

```python {note="1|SET_POINT|Aim for this distance - a set point;4|p_factor|^0.6The p_factor setting controls<br>how strongly it responds.;6|calculate|The controller responds proportionally<br>to a gap. A greater gap means a<br>greater response"}
SET_POINT = 30

class Controller:
    p_factor = 0.03

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor
        return p
```

This makes a `Controller` class and a `SET_POINT` instead of a threshold. This is **proportional** control: the bigger the gap, the bigger the response. Let’s make the rest of the code use it. Swap out the whole try section:

```python {note="11|left_gap|Get the gap<br>between where<br>we are and<br>the set point;15|left_speed|Use the gap to<br>get a speed for<br>each motor;19|set_speed|Set the motor<br>speeds"}
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

```python {note="2|TIME_STEP|We add a TIME_STEP setting so all<br>code uses the same timing;6|i_factor|We add an i factor - controlling how<br>much influence the integral has<br>on the result.;8|integral|_1.3The integral adds up gaps over time;15|TIME_STEP|^Calculate the gap multiplied<br>by passed time;16|i_factor|Then multiply by<br>the i_factor"}
SET_POINT = 30
TIME_STEP = 0.1

class Controller:
    p_factor = 0.03
    i_factor = 0.001

    integral = 0

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor

        # I term
        self.integral += gap * TIME_STEP
        i = self.integral * self.i_factor

        return p + i
```

Locate the time.sleep, and ensure this also uses the time step:

```python {tok="1|TIME_STEP"}
        time.sleep(TIME_STEP)
```

If you send the updated code to the robot, you should find that you can walk with the robot following behind you. Your shoes and trousers may be hard for the sensors to read, so holding a barrier or something rigid and moving that may work better.

If it’s still hopping, adjust the `i_factor` up a bit, but don’t let it get too high.

If it’s failing to stop when you stop or slow when you slow, reduce the `i_limit`, the integral can get very high and be stuck there for a while

## Checkpoint - all the code so far ✅

Here is the whole program with the proportional and integral controller, to check against what is on your robot. `THRESHOLD` and `SPEED` aren’t used any more, so they are left out.

```python
import time
from hcsr04 import HCSR04
import motors

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

SET_POINT = 30
TIME_STEP = 0.1

class Controller:
    p_factor = 0.03
    i_factor = 0.001

    integral = 0

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor

        # I term
        self.integral += gap * TIME_STEP
        i = self.integral * self.i_factor

        return p + i

```

```python
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
        time.sleep(TIME_STEP)
finally:
    motors.stop_all()
```

## Step 4 - Calm it down!

Try this, start your robot a little further than the distance, and hold it, watch the wheels get fast. Now let it go and it will drive really quickly, and probably crash (careful!)

We need to make sure that integral can’t get too excited!

```python {note="5|i_limit|A limit stops it growing out of control;15|i_limit|Apply limits so it isn’t out of control"}
class Controller:
    p_factor = 0.02
    i_factor = 0.001

    i_limit = 50

    integral = 0

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor

        # I term
        self.integral += gap * TIME_STEP
        if self.integral > self.i_limit:
            self.integral = self.i_limit
        elif self.integral < -self.i_limit:
            self.integral = -self.i_limit
        i = self.integral * self.i_factor

        return p + i
```
    
Now, if you let the robot build up an integral error, it will not grow out of control thanks to the `i_limit`. Try this code with the same test.

## Step 5 - Adding brakes!

By now, your robot should be able to follow an object by speeding up when it is too far away and slowing down when it gets closer. But even a good follower can be clumsy: if the object stops suddenly, or jumps away, the robot lurches after it. Let’s give it some brakes. We will make it notice **how quickly the gap is changing** and react to sudden changes, dampening its response to spikes and drops in the gap. **Replace only** the Controller section with this (the other code stays the same):

```python {note="4|d_factor|How strong the<br>brakes are;9|last_gap|Remember the<br>gap from last time<br>round the loop;27|gap_rate|How fast the gap<br>is changing;30|d_factor|Scale it by the<br>d_factor"}
class Controller:
    p_factor = 0.02
    i_factor = 0.001
    d_factor = 0.01

    i_limit = 50

    integral = 0
    last_gap = None

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor

        # I term
        self.integral += gap * TIME_STEP
        if self.integral > self.i_limit:
            self.integral = self.i_limit
        elif self.integral < -self.i_limit:
            self.integral = -self.i_limit
        i = self.integral * self.i_factor

        # D term
        if self.last_gap is None:
            gap_rate = 0
        else:
            gap_rate = (gap - self.last_gap) / TIME_STEP

        self.last_gap = gap
        d = gap_rate * self.d_factor

        return (p +
            i +
            d)
```

The new part looks at how much the gap changed since the last time round the loop. A big, sudden change makes the brakes bite hard; a slow change barely touches them. Start with a very small `d_factor`: reduce it if the robot gets twitchy, and increase it a little if it still overshoots.

**Aside:** the maths name for “how fast something is changing” is the derivative, hence the D. P, I and D together make a PID controller.

## Checkpoint - the finished code ✅

Here is the whole program with the smoother controller, to check against what is on your robot. `THRESHOLD` and `SPEED` aren’t used any more, so they are left out.

```python
import time
from hcsr04 import HCSR04
import motors

right_sensor = HCSR04(trigger_pin=0, echo_pin=1)
left_sensor = HCSR04(trigger_pin=7, echo_pin=28)

SET_POINT = 30
TIME_STEP = 0.1

class Controller:
    p_factor = 0.02
    i_factor = 0.001
    d_factor = 0.01

    i_limit = 50

    integral = 0
    last_gap = None

    def calculate(self, gap):
        # P term
        p = gap * self.p_factor

        # I term
        self.integral += gap * TIME_STEP
        if self.integral > self.i_limit:
            self.integral = self.i_limit
        elif self.integral < -self.i_limit:
            self.integral = -self.i_limit
        i = self.integral * self.i_factor

        # D term
        if self.last_gap is None:
            gap_rate = 0
        else:
            gap_rate = (gap - self.last_gap) / TIME_STEP

        self.last_gap = gap
        d = gap_rate * self.d_factor

        return (p +
            i +
            d)
```

```python
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
        time.sleep(TIME_STEP)
finally:
    motors.stop_all()
```

## What else could you add?

Printing these values in a "P: &lt;value&gt;, I: &lt;value&gt;" format can help you tune the controller, triggering the graph updates in the plotter for better visualization.

How well tuned can you get it before it starts to overshoot or become unstable?
