# Bad Weather Mount Tester

When you buy a new telescope mount, the first things to do is to measure the periodic error, because if the periodic error is really high, you would like to
complain and send it back as fast as possible. Unfortunately, most of the time there will be bad weather after buying astro gear for an indefinite amount of time.

**Bad Weather Mount Tester to the rescue!**

Using this program you can test the periodic error of your mount any time, any place, provided you have a spare computer and monitor and a little bit of space. 

## How does Bad Weather Mount Tester work?

You use a small computer to simulate a star moving across a monitor, you record this movement using a guiding application. As the monitor is very regular, one is able to measure the 
periodic error of your mount any time any place, given the place is large enough and there's a roof on top. 

## Setting up

This manual uses PHD2 as guiding program, but other guiding programs should provide similar functionality. You can use other guiding programs of your choice, 
but you need to check how the given functionality of PHD2 is implemented in your software. 

What you need: 

1. Your (new) mount, with your guiding gear and a computer attached to it (the Astro Computer)
2. A spare computer with monitor (the Simulator)
3. At least 5 m of space between them. 

### Setting up the Simulator

- Make sure the Simulator is on the same network / WiFi as the Astro Computer and that this network is connected to the internet. 
- Install python 3.10 or later on it and check that it works: 
- Open a terminal on the Simulator and run `python --version`, the number displayed should at least be 3.10.
- Then run `pip install BadWeatherMountTester` in the terminal. This installs the Bad Weather Mount Tester on it (both client and server)
- Then run `python -m BadWeatherMountTester`. The program will open and show it's logo, display "Waiting for a connection" and its network address.
- Use a spirit level to position the monitor level horizontally and vertically. The screens middle pixel should be pointing to the mount. 

### Setting up your Astro Computer

- Make sure the Astro Computer is on the same network / WiFi as the Simulator
- Open up a web browser on your astro computer and enter the network address displayed on the Simulator's screen. 
- The simulator will then change the display to its locator screen, that will help you find the exact location on the screen with your guide scope. 

Make sure you can startup BWMT as described here, before setting up the gear (can save a lot of walking).

### Setting up your astro gear

- Fix your guiding gear on the (new) mount. Make sure you can control the mount, the camera and that you can run PHD2 and that it is able to control the correct camera. 
- Place the simulator and its monitor in a distance approximately 5 m dead south of your mount (on northern hemisphere, dead north on southern hemisphere). 
  With "dead south" we mean, that when standing north of the mount (where the guidescope is pointing to), looking south along the RA axis, that line will hit the middle of the 
  screen of the simulator. The extension of the axis of the guidescope (how you would be looking through, but reversed) will hit the ground somwhere between your mount 
  and the simulator's screen. We will fine tune that in one of the next steps. 
- Now start BWMT on the simulator and connect to the simulator using a web browser on your astro computer.
- Point the guidescope to have a good look at the simulator's screen and focus it, using what is displayed by BWMT on the screen.

That's it, you're mostly set to go. Now follow the instructions displayed in the web browser. 
You will be asked to provide some background information to BWMT through the web browser then configure PHD2 correctly:

- Enter the latitude that your mount is configured for into BWMT
- Enter the focal length of your guide scope and the distance between mount and simulator screen . 
- Enter the mount's main period into the web application. (For worm gear mounts: How long does it take to have the worm rotate once?). 
  This is information that the manufacturer of your mount provides.

In PHD2: 
- Create a new guiding profile with the focal length displayed by the Simulator. 
  (The guide scope is not focused to infinity now, and we need to compensate for that to have PHD2 display correct data)
- Disable multi-star guiding, as we will be using one simulated star. 
- Start looping in PHD2. From the `Tools` menu enable the cross in the camera display in PHD2.

Next will be orienting mount and screen.

### Placing BWMT dead south of the mount (Northern Hemisphere)

!!! note: Southern hemisphere 
  The same procedure applies but the mount will be moving right-to-left instead of left-to-right. And North and South will be exchanged.

If during the following procedure the sharpness of the image on left and right hand side is extremely different, orient the screen so, that it is perpendicular to your guide scope, 
stop the movement in the middle of the screen and adjust focus. Then restart the procedure.

If your mount performs a meridian flip in between, check the meridian flip settings in your mount and adjust these so, 
that a meridian flip is avoided and does not interfere with setting up BWMT. Then restart the procedure after these adjustments.

First, using the mount controls, locate the left side of the monitor on the guide scope's picture. The picture displayed on the monitor shows arrows, that point you into the right
corner of the screen. Just follow the arrows. When you have reached the destination indicated by a cross in the picture press `next` in the webbrowser. The webbroser will show you 
a detail of the picture, that it is displaying on the screen. When you start hovering with the mouse, a cross will appear on the screen and become visible in PHD2's display on your
astro computer. Left-Click with the mouse, when the cross displayed by PHD2 and the one displayed by BWMT align. Note: At the moment this does not have to be pixel precise. 

Second, using **ONLY** the RA axis, locate the right side of the screen on the guide scope's picture. If you're leaving the screen on top or bottom, stop there. Press next and again
BWMT will display a detail of the picture. Again use the mouse to find and locate the center position of your guide camera's picture. 

Third, the web application will tell you how to adjust the mount and the screen to get a symmetric trace on the monitor. 
This usually involves using the screws in Azimuth to orient the mount. You may need to recheck focus.  

This procedure ensures, that the longes possible path is traced by the mount, so that we can get the most data.

Repeat this procedure until you're satisfied, that a symmetric arc is traced on the monitor when fully moving from left-to-right. Then press next.

### Setting up the trace line

First we will trace the mount's location accross the screen, to setup the average path that the mount takes across the screen. This entails:  

1. Looking at the guide scopes picture in PHD2, and telling BWMT where the scope is looking
2. Moving the scope in RA for a few pixels
3. Repeating 1 and 2 until all the screen is crossed. 

Then move the mount back to the starting location on the left hand side of the monitor. 

Follow the instructions in the web application.

### Measuring a guiding run

Now activate the simulation of BWMT by pressing next. The mount should now see a single "star" simulated in the guide picture, center this in PHD2 and then start a guiding run in PHD2.
Let it run, until the mount has traced the star across the screen. The web application will display a count-down. 

Using **PHD2 Log Viewer** you can now analyse the performance of your mount. 

# Credit

This software is based on the idea by [Klaus Weyer from Solingen, Germany](https://web.archive.org/web/20241013053734/https://watchgear.de/SWMT/SWMT.html). Rest in Peace, Klaus!

# Author, Copyright & License

Copyright (c) 2026 Jens Scheidtmann and contributors (see CONTRIBUTORS.md)

This file is part of BWMT, the Bad Weather Mount Tester. 

BWMT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

BWMT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with BWMT.  If not, see <http://www.gnu.org/licenses/>.