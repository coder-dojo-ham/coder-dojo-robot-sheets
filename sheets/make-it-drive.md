---
title: Drive a robot
difficulty: 3
language: MicroPython
requires: Laptop with Thonny and a Robot
version: "1.0"
link: https://orionrobots.co.uk/dojo/driving
pdf_link: https://drive.google.com/file/d/1_aQZ4OTaQi4755W07Y7ElXY6j0I0Vjzl/view  # the published PDF in the shared drive
hero: [robot-wheel-closeup.png, square-path.png]
---
Let’s get the robot to drive 🚗! These robots are driven with code, so can program them to follow a pattern, or respond to sensors.

We’ll get them to go forwards ⬆️, backwards ⬇️, turn left ↪️ and right ↩️. Then put them together in sequences.

Let’s make robots move 🤖!
<!-- /intro -->

Here’s what we’ll do:

1. **Get the motors moving**: Write code on the robot to move the motors.
2. **Full speed ahead**: Drive forward and backward.
3. **Controlling the speed**: What if we want to drive slower than full speed?
4. **About turn:** Turn the robot left or right
5. **Putting it all together:** Drive the robot in a square, hexagon or other path.

Ok, let’s get the robot moving! 🚀

## Step 1 - Get a motor moving! ⬆️⬇️

Let’s make our robot motors move! Load **Thonny,** plug the robot into the computer. Turn the robot on, then enter MicroPython mode in Thonny and press the stop button.

The motors are connected to IO (Input output) pins. For example pin 11 drives the left wheel forward:

```robot
left: [up, down]
right: [up, down]
front: true
wheel-names: true
pins: {left-up: Pin 11, left-down: Pin 10, right-up: Pin 8, right-down: Pin 9}
```

We start with imports:

```python
from machine import Pin
import time
```

We import `Pin` to control the output pins, and `time` so we can turn the motors on long enough to do something.

::: tip
💡 Output pins allow us to control hardware on the robot like the motors and lights.
:::

Let’s connect some variables to control the Pins on one motor:

```python
motor_forward = Pin(10, Pin.OUT)
motor_back = Pin(11, Pin.OUT)
```

Each output pin makes the motor turn a different direction. Turning both on makes the motor stop.

{{> warn-try-finally}}

Let’s turn the motor on:

```python
try:
    motor_forward.on()
    time.sleep(0.5)
```

This turns the forward pin on for half a second. If we didn’t have the sleep, it would stop immediately, faster than you might even be able to notice.

We can then do the same with the backward pin:

```python
    motor_forward.off()
    motor_back.on()
    time.sleep(0.5)
```

Now we need a `finally` section. This runs when the code ends, always stopping the motors:

```python
finally:
    motor_forward.off()
    motor_back.off()
```

{{> warn-stand}}

Put the robot on its stand, and run this code with Thonny, you should see one wheel drive forward, then backward, then stop.

{.nobreak}
## Experiments to try:

- Try changing the sleep times (they are fractions of a second).
- Try using pins 8 and 9 for the other motor. If it goes back when you meant forward, you may need to swap the order of the pins.

## Step 2 - Full speed ahead! ⏫⏬

We’ve made one motor move, but to drive the robot forward, we need both motors. In a **new file**:

:::: side
::: fig
```python
from machine import Pin
import time

motor_r_forward = Pin(8, Pin.OUT)
motor_r_back = Pin(9, Pin.OUT)
motor_l_forward = Pin(11, Pin.OUT)
motor_l_back = Pin(10, Pin.OUT)
```
:::
::: text
```robot
left: up
right: up
arrow: forward-short
```
:::
::::

This now has variables for pins on both motors. The key to this working, is that both motors forward pins are on at the same time:

```python
try:
    motor_l_forward.on()
    motor_r_forward.on()
    time.sleep(0.5)
```

In the `finally` section we must remember to **turn all the motor pins off**:

```python
finally:
    motor_l_forward.off()
    motor_l_back.off()
    motor_r_forward.off()
    motor_l_back.off()
```

Save the file as `main.py` and upload it to the robot.

**Test this on the stand**, then try it on the floor. It should drive forwards.
You can go backwards by swapping forward pins for back pins in the same file:

:::: side
::: fig
```python
try:
    motor_r_back.on()
    motor_r_back.on()
    time.sleep(0.5)
finally:
    motor_l_forward.off()
    motor_l_back.off()
    motor_r_forward.off()
    motor_l_back.off()
```
:::
::: text
```robot
left: down
right: down
arrow: backward
```
:::
::::

This goes at full speed, but what if we wanted to control the speed?

## Step 3 - Controlling the speed 🐢🐇

:::: side
::: fig
```robot
left: up
right: up
arrow: forward
stripes: true
```
:::
::: text
We control motor speeds with **PWM** - pulse width modulation. PWM sends pulses of power to motors.

We can control how much time it mixes being on vs being off. When more on-time is mixed, more power is sent to the motor, making the motor faster.

How much on-time is in the mix is known as the **duty-cycle**.
:::
::::

In a **new file**:

```python
import time
from machine import Pin, PWM
```

On this robot, duty cycle control is a 16 bit value. This lets it go between 0 meaning off and 2 to the power of 16 minus 1 meaning full power:

```python
MAX_SPEED = 2 ** 16 - 1
```

We then set up each motor pin to be a PWM pin. They need a fixed frequency:

```python
motor_l_forward = PWM(Pin(8), freq=2000)
motor_l_back = PWM(Pin(9), freq=2000)
motor_r_forward = PWM(Pin(11), freq=2000)
motor_r_back = PWM(Pin(10), freq=2000)

left = motor_l_forward, motor_l_back
right = motor_r_forward, motor_r_back
```

We also created variables, `left` and `right`, storing forward and back PWM pins for each motor. This lets us build a stop function to make it easier to stop the motors:

```python
def stop(motor):
    motor[0].duty_u16(0)
    motor[1].duty_u16(0)
```

We can pass our `left` or `right` variables to this `stop` function. PWM pins have a `duty_u16` function to set their duty cycle.

Let’s test the speeds in a loop from 0 to 10, using that to scale from 0 to the maximum speed:

```python
try:
    for n in range(0, 10):
        speed = int(MAX_SPEED * n /10)
        left[0].duty_u16(speed)
        right[0].duty_u16(speed)
        time.sleep(0.5)
```

By dividing the loop counter by 10, we get a fraction value between 0 and 1. By multiplying it by `MAX_SPEED` we get a power level.
We can then send this to the motors with the PWM `duty_u16` function. We want to sleep between each loop, so we have time to observe the effect.

We’ve put the speed test in a try section, so we can then use `finally` to ensure the motors always stop:

```python
finally:
    stop(left)
    stop(right)
```

**Put the robot on the stand**. When you run this, you should hear the motors start with a beep, then increase in speed.

The motors barely move at the lower values where there’s too little power for it to move, but past about 3/10ths the motors will move.

### Building a motor control layer 🔧

We will use motors in other robot experiments. Details like the `MAX_SPEED` variable and motor pins can be kept in this layer, so code for other experiments don’t need to worry about them. Build a **new file** called **`motors.py`** to deal with this. Start it with:

```python
from machine import Pin, PWM

MAX_SPEED = 2 ** 16 - 1

motor_l_forward = PWM(Pin(8), freq=2000)
motor_l_back = PWM(Pin(9), freq=2000)
motor_r_forward = PWM(Pin(11), freq=2000)
motor_r_back = PWM(Pin(10), freq=2000)

left = motor_l_forward, motor_l_back
right = motor_r_forward, motor_r_back
```

We add helper functions for the other code. First the `stop` function:

```python
def stop(motor):
    motor[0].duty_u16(0)
    motor[1].duty_u16(0)
```

A `stop_all` function stops both motors, something we’ll do at the end of most programs:

```python
def stop_all():
    stop(left)
    stop(right)
```

The next function, `set_speed`, sets the speed of a motor:

```python
def set_speed(motor, speed):
    if speed < 0:
        motor = motor[1], motor[0]
        speed = -speed
    motor[0].duty_u16(int(speed * MAX_SPEED))
    motor[1].duty_u16(0)
```

We can send the `left` or `right` variables as the `motor` parameter. The `speed` parameter is a power mix between -1 and 1. The value 0.7 goes forward a little slower than full speed, and -1.0 goes backward at full speed.

Upload `motors.py` to the robot, by right clicking it in the file area. This code doesn’t run anything, but instead makes these functions available as tools.

Let’s start a **new file** to drive at different speeds using our new tools:

```python
import motors
import time
```

Add a `try` section, and use the `set_speed` function to control the speed of each motor:

```python
try:
    motors.set_speed(motors.left, 0.7)
    motors.set_speed(motors.right, 0.7)
    time.sleep(0.4)
```

In the finally part, we can use `stop_all` to stop the motors:

```python
finally:
    motors.stop_all()
```

**Put the robot on the stand**, then send this as a new **`main.py`**.
You can now change the number 0.7 to anything from -1.0 to 1.0. Or build a for loop again and divide down to make the speed ramp up.

## Checkpoint - motors library and demonstration ✅

The file `motors.py` should have the following in it:

```python
from machine import Pin, PWM

MAX_SPEED = 2 ** 16 - 1

motor_l_forward = PWM(Pin(8), freq=2000)
motor_l_back = PWM(Pin(9), freq=2000)
motor_r_forward = PWM(Pin(11), freq=2000)
motor_r_back = PWM(Pin(10), freq=2000)

left = motor_l_forward, motor_l_back
right = motor_r_forward, motor_r_back


def stop(motor):
    motor[0].duty_u16(0)
    motor[1].duty_u16(0)


def stop_all():
    stop(left)
    stop(right)


def set_speed(motor, speed):
    if speed < 0:
        motor = motor[1], motor[0]
        speed = -speed
    motor[0].duty_u16(int(speed * MAX_SPEED))
    motor[1].duty_u16(0)
```

The file `main.py` should have the following in it:

```python
import motors
import time

try:
    motors.set_speed(motors.left, 0.7)
    motors.set_speed(motors.right, 0.7)
    time.sleep(0.4)
finally:
    motors.stop_all()
```

## Step 4 - About turn! ↩️

:::: side
::: fig
```robot
left: up
right: down
arrow: spin
```
:::
::: text
You might have accidentally made the robot spin or turn a corner. Let’s see how that works.

Robot wheels are like oars on a rowing boat, if they both go in the **same direction at the same speed**, you go in a **straight line**, but if they have **different speeds or directions**, the robot will **turn**.
:::
::::

Let’s modify the **previous** `main.py` to make the robot **spin**:

```python {note="6|-0.7|Set to **-0.7**"}
import motors
import time

try:
    motors.set_speed(motors.left, 0.7)
    motors.set_speed(motors.right, -0.7)
    time.sleep(0.4)
finally:
    motors.stop_all()
```

Try this out **on the stand**, then on the floor. You can control the speed of the spin with the numbers, and the direction of the spin by which one is negative.

You can control how far the robot spins with the speed of the spin, or the time it spins for.

:::: side
::: fig
```robot
left: up
right: up
arrow: curve-left
```
:::
::: text
Gentler curves can be made by having different values. If one motor drives a little slower than the other, the robot will turn towards that direction.
:::
::::

Let’s modify the code to do this:

```python {note="5|1|Change to **1**;6|0.5|Change to **-0.5**"}
import motors
import time

try:
    motors.set_speed(motors.left, 1)
    motors.set_speed(motors.right, 0.5)
    time.sleep(0.4)
finally:
    motors.stop_all()
```

This code should draw out a curve on the floor.

By adjusting the relative values and time, you can roughly get any angle, and wider gentler curves or tighter spins. Play with these numbers and see how the robot moves!

## Step 5 - Putting it all together! ⬆️⤴️⬆️⤴️

:::: side
::: fig
![Square path](square-path.png){style="width:60mm"}
:::
::: text
You can now use motors to make shapes and paths, or with some fun timing, make the robot dance! 💃🤖

This works a little bit like drawing with Turtle. You can make a robot move forward, then turn.

We can use a for loop to make a square, or long curves to make a circle.
:::
::::

Let’s try a square. Start a **new** `main.py`. The imports are the same:

```python
import time
import motors
```

For this exercise, we make a helper function for a straight line:

```python
def straight(speed, duration):
    motors.set_speed(motors.left, speed)
    motors.set_speed(motors.right, speed)
    time.sleep(duration)
```

We also make a helper for a left turn, like our square diagram:

```python
def left(speed, duration):
    motors.set_speed(motors.left, 0)
    motors.set_speed(motors.right, speed)
    time.sleep(duration)
```

We can use these in `for` loop over each side, wrapped in the `try`/`finally` section:

```python
try:
    for n in range(4):
        straight(0.6, 1.0)
        left(0.6, 1.0)
finally:
    motors.stop_all()
```

It goes straight for a second, then turns for a second. You can adjust the speed and timing values.

We guarantee that this won’t make an exact 90 degree turn, however, you can try and find the right time on turning left to do so.

## Your turn!

You have everything you need to make shapes, paths or dances with the robot.

- Try adding a `right` turn function and making a square the other way.
- Try making other shapes, either a regular shape (like a hexagon), or drawing a simple shape sequence on paper (straight, turn, straight).
- Try using a spin to do a victory spin at the end!
- Try using gentle curves to make circles.
- Try timing with pauses, and spin moves to make the robot dance!
