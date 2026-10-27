---
title: Playing with LEDs
difficulty: 2
language: MicroPython
requires: Laptop with Python, Thonny and a Robot kit
version: "1.1"
link: https://orionrobots.co.uk/dojo/led
pdf_link: https://drive.google.com/file/d/1OB-jCAx7PjnKGWfU4E43ljIoachvfbAD/view  # the published PDF in the shared drive
hero: [led-digital-io-status.png]
---
The robot has lots of little lights, known as LEDs (light emitting diodes). How can we light one up? Or light them all up?

We will look at the user controllable LEDs on the robot and how to control them. We’ll control them manually at first, and then get the code to do it for us!
<!-- /intro -->

Here’s what we’ll do:

1. **Turn on an LED**: We’ll use Python to turn on one of the robot LEDs
2. **Turn off an LED**: How to turn off an LED in Python
3. **Try some other LEDs**: How pin numbers related to LEDs
4. **Make an LED Blink**: How to use a loop make the lights flash! ✨
5. **Animating LEDs**: Use a list and loops to run lights in sequence

Are you ready to play with the LEDs?

## Step 1 - Turn on an LED!

Plug the robot into your computer. Turn it on. Open Thonny. Ensure that you’ve selected the Python on the robot:

![Thonny interpreter list](thonny-select-interpreter.png){style="width:78mm"} ➡️ ![Thonny shell](thonny-shell-connected.png){style="width:78mm"}

Connect Thonny to your robot, and click in the Shell area. You may need to press 🛑 first.

```pycon
>>>
```

Now type the following:

```python
from machine import Pin
```

And press enter. Then type:

```python
Pin(2, Pin.OUT).value(1)
```

Press enter, and a robot LED should turn on!

{.nobreak}
## Troubleshooting

If your robot isn’t turned on and plugged in, you’ll not be able to connect to it. If the laptop was used for another robot, you will need to reselect RP2040 in the Python choice list (see Step 2).

```text {tone="error"}
  from machine import Pin
ModuleNotFoundError: No module named 'machine'
```

This error will show if you try to run code when Thonny is not connected to the robot. The “machine” import will only work on the robot’s Python.

## Step 2 - Turn off an LED!

We can also turn an LED off by typing a similar command:

```python
Pin(2, Pin.OUT).value(0)
```

Press enter and the same LED will turn off. Experiment with the value 0 and 1, and you should now be able to turn it on and off.

You can shortcut with a variable for our LED:

```pycon
>>> banana_led = Pin(2, Pin.OUT)
>>> banana_led.value(0)
>>> banana_led.value(1)
>>> banana_led.value(0)
```

We can now say an LED has a purpose, maybe for saying we need a banana?

## Step 3 - Try some different LEDs

Our robot has many controllable LEDs. Let’s try a different LED number:

:::: side-right
::: text
```python
Pin(4, Pin.OUT).value(1)
```

This should turn on another LED. See how the number after Pin has changed? Each of the controllable LEDs on the robot is connected to a numbered Pin.

On the board, you will see little numbers with “GP” (short for General Purpose) in front of them, these are Pin numbers.

The image on the right shows the LED pin numbers. There are gaps because those pin numbers are used for something else on the robot.
:::
::: fig
![LED pin numbers](led-pin-strip.png){style="width:38mm"}
:::
::::

Perhaps we want a different LED for showing we want a banana? Or an LED to show we want a strawberry? Maybe we want both?

```pycon
>>> banana_led = Pin(17, Pin.OUT)
>>> strawberry_led = Pin(16, Pin.OUT)
>>> banana_led.value(1)
>>> strawberry_led.value(0)
>>>
```

We can use variable names with Pin numbers to say what we mean an LED to do.

Try turning different lights on, or off, and giving them names.

## Step 4 - Make an LED blink

While we can type `value(0)` and `value(1)` for a pin to make it blink, these are robots, they should be able to blink an LED by themselves!

Try this in Thonny editor:

```python {note="5|True|This means to loop forever;7|sleep|Sleeps say how long we want an LED on or off for.;9|    |This gap (4 spaces or press the TAB key)<br>tells python that these four lines are to<br>run inside the loop."}
from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)
while True:
    led.value(1)
    sleep(0.2)
    led.value(0)
    sleep(0.2)
```

## What else could you add?

- Could you blink different LEDs?
- Maybe you could blink more than one at the same time?
- Can you blink between some LED’s alternately?

## Step 5 - Animating LEDs

Blinking is simple animation, but we can do more with LEDs than blink a single LED.

First we need the LEDs in a list. Create a **new file** and start it with:

```python
from machine import Pin
from time import sleep
```

:::: side-right
::: text
Then add a list with every LED pin in it:

```python
leds = [
    Pin(0, Pin.OUT),
    Pin(1, Pin.OUT),
    Pin(2, Pin.OUT),
    Pin(3, Pin.OUT),
    Pin(4, Pin.OUT),
    Pin(5, Pin.OUT),
    Pin(6, Pin.OUT),
    Pin(7, Pin.OUT),
    Pin(16, Pin.OUT),
    Pin(17, Pin.OUT),
    Pin(26, Pin.OUT),
    Pin(27, Pin.OUT),
    Pin(28, Pin.OUT),
]
```

Mind the gaps here!
:::
::: fig
![LED pin numbers](led-pin-strip.png){style="width:38mm"}
:::
::::

We can now loop over the LEDs and turn them on:

```python
while True:
    for led in leds:
        led.value(1)
        sleep(0.2)
    for led in leds:
        led.value(0)
        sleep(0.2)
```

You should now see all the LEDs light up in sequence, then turn off.

{.nobreak}
## Can you make other animations here?

- Can you adjust the timing? Make it faster or slower?
- You can use this method to turn each LED on then off - making lights sweep back and forth along the list, or do multiple sweeps.
