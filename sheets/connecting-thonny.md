---
title: Getting started with MicroPython robots
difficulty: 2
language: MicroPython
requires: Laptop with Thonny and a Robot
version: "1.1"
link: https://orionrobots.co.uk/dojo/thonny
pdf_link: https://drive.google.com/file/d/17jP2cvMQIRG5ZUo4uXjmtOCUoOoJHCdj/view  # the published PDF in the shared drive
hero: [hero-thonny.png, hero-robot.jpg]
---
In this sheet, you’ll see how to get started with your robot by connecting to it, writing some code, and getting the robot to run it.

We’re using Thonny, a Python editor with simple controls. It can connect to MicroPython devices like the Pico on our robot and send code to them.
<!-- /intro -->

Here’s what we’ll do:

1. **Setup Thonny**: Get Thonny ⬇️ and configure it ⚙️
2. **Connect Thonny to the robot**: Connect to the robot 🔌 and try code on it 🚀

Let’s get our robot connected!

## Step 1 - Setup Thonny

Your computer may already have Thonny. If not, go to <https://thonny.org/>. Download the latest installer for your computer, and follow the install guides.

Launch Thonny. You should see the following:

![Thonny’s window: menu, play and stop buttons, file list, code editor, shell panel and Python choice menu](thonny-window-labelled.png){style="width:120mm"}

### Help! The menu is missing!

You may see Thonny looks like this:

![Thonny’s simple mode toolbar, with “Switch to regular mode” on the right](thonny-regular-mode.png){style="width:150mm"}

If you see this, click the “Switch to regular mode” text on the right, click OK, then close Thonny and open it again. Thonny should now look like the screen above.

{.newpage}
### Enable files and shell

:::: side-right
::: text
In the View menu at the top of the Thonny screen, ensure that Files and Shell are ticked.
:::
::: fig
![Thonny’s View menu with Files and Shell ticked](thonny-view-menu.png){style="width:44mm"}
:::
::::

## Step 2 - Connect Thonny to the robot

In this step, we’ll connect your computer to the robot and run some simple MicroPython code.

::: warning
⚠️ **Beware!** When you turn on a robot, it may run old code and drive off! Always prop the wheels up from the desk if you don’t know what’s on the robot!
:::

:::: split
::: fig
![The robot stand](robot-stand.png){style="width:66mm"}
:::
::: fig
![The robot on its stand, wheels off the desk](robot-on-stand.png){style="width:66mm"}
:::
::::

First, plug the robot into the computer with MicroUSB. Turn on the robot with the on/off switch!

![The robot’s power switch and USB connector](usb-power.png){style="width:90mm"}

In Thonny, select “MicroPython (RP2040)” from the menu in the bottom right:

![Thonny with the Python choice menu arrowed](thonny-click-here.png){style="width:128mm"}

![The menu with MicroPython (RP2040) outlined](thonny-pick-interpreter.png){style="width:128mm"}

{.lead}
We will be writing our own code, so ignore code that is already on the robot. The Shell panel shown below should show if you have successfully connected to the robot:

:::: side
::: fig
![Thonny connected to the robot, with the Stop button and Shell panel marked](thonny-connected.png){style="width:84mm"}
:::
::: text
**If you see this, you are connected**

```pycon
MicroPython v1.24.1 on 2024-11-29;
Raspberry Pi Pico with RP2040
Type "help()" for more information.
>>>
```

**If you see this, select the RP2040 again**

```text {tone="error"}
Unable to connect to COM13:
port not found

Process ended with exit code 1.
```

**If you see this, press Stop**

```text {tone="error"}
Connection lost -- EOF

Use Stop/Restart to reconnect.

Process ended with exit code 1.
```
:::
::::

You can run simple code by clicking in the Shell. It will be waiting for you to type:

```pycon
>>>
```

You can now type a command, maybe get it to say hello?

```python
print("Hello, robot!")
```

Press enter, and it will run this and respond:

```pycon
Hello, robot!
>>>
```
