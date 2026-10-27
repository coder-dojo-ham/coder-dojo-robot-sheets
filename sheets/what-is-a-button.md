---
title: Playing with buttons
difficulty: 3
language: MicroPython
requires: Laptop with Thonny and a Robot
version: "1.1"
link: https://orionrobots.co.uk/dojo/button
pdf_link: https://drive.google.com/file/d/15gzrvQxV9wEEc4268Vl9PKX2HNs3sEYj/view  # the published PDF in the shared drive
hero: [buttons-board.png]
---
Your robot has two user buttons. We can use them to let the user control the robot.

Let’s see how to read the buttons, and use them to choose what the robot will do.
<!-- /intro -->

Here’s what we’ll do:

1. **Read a button state**: How to read from a button
2. **Read a button in a loop**: How to let the code keep reading buttons
3. **Choose based on a button press**: How to use the button to choose
4. **Connect buttons to lights**: Turn on lights with the buttons

Let’s play with buttons!

## Step 1 - Read the button state

Get your robot connected. Use the shell, and we can check if a button is pressed. Type the following lines in the shell:

```python
from machine import Pin
Pin(20, Pin.IN).value()
```

You should see something like the following:

```pycon {note="3|1|The button isn’t pressed;5|0|The button is pressed"}
>>> from machine import Pin
>>> Pin(20, Pin.IN).value()
1
>>> Pin(20, Pin.IN).value()
0
```

You’ll need to hold the button with one hand, then press up, and enter with the other hand!

{.nobreak}
## Step 2 - Read the button in a loop

Needing to hold the button in one hand, and rerun the code with the other is pretty inconvenient. What we need is code to keep checking it…

Go to the code editor area of Thonny, create a new 📄 file and add the following:

```python {note="1|sleep|Prepare tools our code will use;3|button|A variable for our button;5|True|Loop until stop pressed;6|print|Print the button’s value;7|sleep|Too fast, and the prints won’t keep up.<br>We must let the Pico sleep a bit between checks"}
from time import sleep
from machine import Pin
button = Pin(20, Pin.IN)

while True:
    print(button.value())
    sleep(0.1)
```

Run this with the play ▶️ button. You should now be able to see the button being pressed or not.

```text {note="1|1|Button not pressed;2|0|Button pressed"}
1
0
1
0
1
1
1
```

You can try the other button by changing the 20 to 21 for the other pin.

## Step 3 - Choose with button presses

Using an `if` we can check which button is pressed and do different things.

```python {note="4|strawberry_button|Creating variables for our pins,<br>name them something useful;8|0|Check if the value is 0, to see if it’s pressed;9|print|Print a funny message"}
from time import sleep
from machine import Pin

strawberry_button = Pin(20, Pin.IN)
banana_button = Pin(21, Pin.IN)

while True:
    if strawberry_button.value() == 0:
        print("Strawberries!")
    if banana_button.value() == 0:
        print("Bananas!")
    sleep(0.1)
```

Run this, and you should be able to get the code to print bananas or strawberries. Perhaps you can press both at the same time and make a smoothie?

```text
Strawberries!
Strawberries!
Bananas!
Bananas!
Bananas!
Strawberries!
Bananas!
```

Could you make it print something else?

Could you change the names we’ve given the buttons to match?

## Step 4 - Using the buttons with LEDs

We can have pins for buttons, and pins for LEDs. Let’s try that now:

```python {note="4|Pin&IN|INput pins for buttons;7|Pin&OUT|OUTput pins for LEDs;11|0|^Test if a button<br>was pressed;12|value|Set the LED value<br>to the result"}
from time import sleep
from machine import Pin

strawberry_button = Pin(20, Pin.IN)
banana_button = Pin(21, Pin.IN)

banana_led = Pin(2, Pin.OUT)
strawberry_led = Pin(3, Pin.OUT)

while True:
    strawberry_pressed = strawberry_button.value() == 0
    strawberry_led.value(strawberry_pressed)

    banana_pressed = banana_button.value() == 0
    banana_led.value(banana_pressed)

    sleep(0.1)
```

This code is doing a test of a button being pressed, and passing that result straight into the LED value. Run it, and you should be able to light each of the two LEDs with the button.

We could add a smoothie LED for when both are pressed:

```python {hl="9,18,19" note="9|Pin&OUT|Adding another LED;18|and|^1“and” lets us<br>check that both<br>are pressed;19|value|_1We can use that<br>result to set<br>an LED"}
from time import sleep
from machine import Pin

strawberry_button = Pin(20, Pin.IN)
banana_button = Pin(21, Pin.IN)

banana_led = Pin(2, Pin.OUT)
strawberry_led = Pin(3, Pin.OUT)
smoothie_led = Pin(4, Pin.OUT)

while True:
    strawberry_pressed = strawberry_button.value() == 0
    strawberry_led.value(strawberry_pressed)

    banana_pressed = banana_button.value() == 0
    banana_led.value(banana_pressed)

    is_a_smoothie = strawberry_pressed and banana_pressed
    smoothie_led.value(is_a_smoothie)
    sleep(0.1)
```
