---
title: Following lines
difficulty: 4
language: Python
requires: Laptop with Python, Thonny or Mu, Robot kit
version: "1.1"
link: https://orionrobots.co.uk/dojo/line-follow
pdf_link: https://drive.google.com/file/d/1ZISvVXBvOEpCu8rUh5q7j10Me3O__4gG/view  # the published PDF in the shared drive
hero: [hero-maker-line-sensor.png, hero-robot-on-line.png]
---
Robots can use their sensors to respond to their environment. The sensor under the robot can “see” a line using infra-red light 👀. Using the line sensor, the robot can follow a thick line drawn on the floor.

Using the robot kit and micropython, see how to get the robot to detect and follow a line 🛤️, and how to make it smoother and faster.

You will need to use or borrow the line following paper for this.
<!-- /intro -->

Here’s what we’ll do:

1. **Preparing the sensor:** See how the line sensor detects the line
2. **Getting sensor data**: How to see the sensor data in code
3. **Line following**: How to follow the line using if statements
4. **Run code automatically**: The robot 🤖 can run your code without the laptop
5. **Smooth Line Following:** Using multiplication for smoothing - proportional control

Get excited, this robot’s going to drive itself following lines automatically! 🤖

## Step 1 - Preparing the sensor

The line following sensor has 5 elements, each of which has an invisible infrared light 🔆 and a sensor 👁️. The bottom of the sensor looks like this:

![The top of the Maker Line sensor, labelled](sensor-top-labelled.png){style="width:150mm"}

On the robot, these sensors are facing down, as close to the floor as they can be.

![The underside of the Maker Line sensor, labelled](sensor-bottom-labelled.png){style="width:150mm"}

The sensor needs to be configured for the line we’ll put it on. It can either detect a light line on a dark background, or a dark line on a light background. Ensure “line color” switch matches the colour of the line.

The sensor needs you to “teach” it how the light and dark light levels look on the test area. This is also called “calibration”

Put the robot on its stand and turn the robot on, it may have driving code on it. Replace the `main.py` on the robot with the LED flashing demo from <https://orionrobots.co.uk/dojo/thonny>.

Now, the robot shouldn’t try to drive when you turn it on. Put it on a line following sheet instead of its stand, and the sensor should be lit up, and may already be responding to the line. It may also be not-quite detecting the line.

With the robot on the sheet, near to a line or test bar, hold the “Calibration” button, the LEDs should fill up and then start blinking. You can now let go of this button.

You can now wave the line sensor over the line until all the Line Sensors have seen the line, then press the button again to finish.

You should now see the sensor LEDs show where the line is under them. This sensor is ready to use.

## Step 2 - Getting sensor data

Let’s get that line sensor data, and print that on the screen.

```python
from machine import ADC, Pin
import time

line_in = ADC(Pin(27, Pin.IN))

while True:
    line = line_in.read_u16()
    print(line)
    time.sleep(0.1)
```

When you run this, wave the robot over a line, and you should see changing numbers depending on where the line is.\
A high number means the sensor is left, a lower means it’s right.

The sensor is connected on Pin 27, which we set up as an Input. It’s then turned into an ADC - Analog data converter. That allows one pin to measure a varying input level.

The while loop reads this data, as a `u16` - a number between 0 and 65535 (2 to the power of 16 minus 1), prints it and sleeps a little time.

::::: side-right
::: text
Thonny has a trick up its sleeve for this. Click view->plotter:\
And Thonny will plot the data:

![Thonny plotting the sensor values](thonny-plotter.png){style="width:100mm"}

Awesome, we can now see our data. But how can we get the robot making decisions with it?
:::
::: fig
![Thonny View menu with Plotter highlighted](thonny-view-menu.png){style="width:42mm"}
:::
:::::

## Step 3 - Line following

We can use this data to control our robot motors. You will need to upload `motors.py` to your robot from <https://orionrobots.co.uk/dojo/driving>.

Let’s make code to drive on a line:

Try this on the stand with a test sheet under the stand - pressing play, the robot should change motor speeds to turn towards the line.

```python
from machine import ADC, Pin
import time
import motors


line_in = ADC(Pin(27, Pin.IN))
middle = 2 ** 15
fast = 0.7
slow = 0.3

try:
    while True:
        line = line_in.read_u16()
        print(line)
        if line > middle + 1000:
            motors.set_speed(motors.left, fast)
            motors.set_speed(motors.right, slow)
        elif line < middle - 1000:
            motors.set_speed(motors.left, slow)
            motors.set_speed(motors.right, fast)
        else:
            motors.set_speed(motors.left, fast)
            motors.set_speed(motors.right, fast)
        time.sleep(0.01)
finally:
    motors.stop_all()
```

## Step 4 - Run code automatically

Running code in Thonny is fine when the robot is connected, but after testing your code that way, you probably want to run it when you’ve turned on the robot.

<span style="color:#ff0000">File -> Save As -> Select Micropython device -> Name it “main.py”.</span>

Thonny has panels for managing files, both on your computer and on the robot:

:::: split
::: fig
![Thonny file panels: files on your computer and files on the robot](thonny-files-left.png){style="width:100mm"}
:::
::: fig
![The right-click menu with Upload to / and Rename](thonny-files-right.png){style="width:66mm"}
:::
::::

First, in the files on your computer, you need to rename the file to “main.py”. Right click on the file to rename or make a copy.\
Right click the new named file, and use “Upload to /” to put it on the robot.

You can now **turn off the robot** and unplug it.

{{> warn-test-run}}

Put the robot on a test sheet on the floor, and turn it on. It should follow this. If it’s working, try it on a line-following track.

This code tracks the middle of the line as 2**15 - or 2 to the power of 15 - this is half of the `u16` range.

The loop is in a `try/finally` block to ensure the motors stop if there are any problems.

When the line is read, we compare it with the middle with if statements. If the value is 1000 above the middle, we make the right motor slower, so the robot will turn a little to the left. If it’s 1000 below the middle, we make the left motor slower.

You can try changing the speed or limit values, and see how this robot behaves. Which make it follow the line better?

If it’s inside this area, the robot drives forward. The result is pretty good and will follow lines.\
Can we make it smoother?

## Step 5 - Smooth Line Following

We can vary how much we turn by how far our robot is from the middle point, a different approach. Try this code:

```python
from machine import ADC, Pin
import time
import motors


line_in = ADC(Pin(27, Pin.IN))
middle = 2 ** 15
scale = 1/middle
speed = 0.5
proportion = 0.4

try:
    while True:
        line = line_in.read_u16()
        print(line)
        error = line - middle
        correction = error * scale * proportion

        motors.set_speed(motors.left, speed + correction)
        motors.set_speed(motors.right, speed - correction)
        time.sleep(0.01)
finally:
    motors.stop_all()
```

Test this on the stand first for errors, then try it on a track.

This code uses **Proportional Control**, a technique in robots where they respond more strongly when the error or difference from the intended point is higher.

After measuring the line, this takes the difference, to compare the line with the middle, this is the **error**, how far we are from the line.

The code scales the error from the middle down to a value between -1 and 1, a similar range to our motors. This scaled error is then multiplied by a **proportion** variable, how strongly the robot will react, to make a correction.

The motor speeds are set from a base speed, and the correction is added to one motor speed, and subtracted from the other, so the robot will turn more when there’s a higher correction.

Does this approach look smoother? Try adjusting the speed and proportion values, perhaps you can get a faster robot.

This proportional control response has a tendency to overshoot and adjust back.

## What else could you try?

- Can changing the timing in the sleep make these behaviours smoother?
- The robot starts as soon as you turn it on. Could you add a loop that waits for a button before it goes?
