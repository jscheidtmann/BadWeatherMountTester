# Manual

## How does Bad Weather Mount Tester work?

You use a small computer to simulate a star moving across a monitor, you record this movement using a guiding application. As the monitor is very regular, one is able to measure the
periodic error of your mount any time any place, given the place is large enough and there's a roof on top.

## Setting up

This manual uses PHD2 as guiding program, but other guiding programs should provide similar functionality. You can use other guiding programs of your choice,
but you need to check how the given functionality of PHD2 is implemented in your software.

What you need:

1. Your (new) mount, with your guiding gear and a computer attached to it (the Astro Computer)
2. A spare computer with monitor (the Simulator)
3. At least 5 m of space between them. (Ok, you can do with 3.5 m, but then accuracy will suffer)

### Setting up the Simulator

- Make sure the Simulator is on the same network / WiFi as the Astro Computer and that this network is connected to the internet.
- Install python 3.10 or later on it and check that it works:
- Open a terminal on the Simulator and run `python --version`, the number displayed should at least be 3.10.
- Then run `pip install BadWeatherMountTester` in the terminal. This installs the Bad Weather Mount Tester on it (both client and server)
- Then run `python -m BadWeatherMountTester`. The program will open and show it's logo, display "Waiting for a connection" and its network address.
- Use a spirit level to position the screen level horizontally and vertically. The screens middle pixel should be pointing to the mount.

### Setting up your Astro Computer

- Make sure the Astro Computer is on the same network / WiFi as the Simulator
- Open up a web browser on your astro computer and enter the network address displayed on the Simulator's screen.
- The simulator will then change the display to its locator screen, that will help you find the exact location on the screen with your guide scope.

Make sure you can startup BWMT as described here, before setting up the gear (can save a lot of walking).

### Setting up your astro gear

- Fix your guiding gear on the (new) mount. Make sure you can control the mount using your Astro Computer, the camera and that you can run PHD2 and that it is able to
  control the correct camera.
- Place the simulator and its monitor in a distance approximately 5 m dead south of your mount (on northern hemisphere, dead north on southern hemisphere).
  With "dead south" we mean, that when standing north of the mount (where the guidescope is pointing to), looking south along the RA axis, that line will hit the middle of the
  screen of the simulator. The extension of the axis of the guidescope (how you would be looking through, but reversed) will hit the ground somwhere between your mount
  and the simulator's screen. We will fine tune that in one of the next steps.
- Now start BWMT on the simulator and connect to the Simulator using a web browser on your Astro Computer. BWMT will display a screen full of arrows.
- Point the guidescope to have a good look at the simulator's screen and focus it, using what is displayed by BWMT on the screen.

That's it, you're mostly set to go. Now follow the instructions displayed in the web browser.
You will be asked to provide some background information to BWMT through the web browser then configure PHD2 correctly:

- Enter the latitude that your mount is configured for into BWMT
- Enter the focal length of your guide scope and the distance between mount and simulator screen
- Enter the guide camera's sensor information, i.e. the number of pixels in width and heigth and the pixel pitch
- Enter the mount's main period into the web application. (For worm gear mounts: How long does it take to have the worm rotate once?).
  This is information that the manufacturer of your mount provides

In PHD2:
- Create a new guiding profile with the focal length displayed and the binning recommended by BWMT.
  (The guide scope is not focused to infinity now, and we need to compensate for that to have PHD2 display correct data)
- Disable multi-star guiding, as we will be using one simulated star.
- Start looping in PHD2. From the `View` menu enable the bullseye overlay in the camera display in PHD2.

Next will be orienting mount and screen.

### Placing BWMT dead south of the mount (Northern Hemisphere)

> [!NOTE]
> For Southern hemisphere the same procedure applies but the mount will be moving right-to-left instead of left-to-right. And North and South will be exchanged.

Starting from home position, and using PHD2's calibration assistant, slew the mount to point at the screen. For this you have to enter the negative value of `(90° - Latitude)` into Dec
and then let it slew the mount. Adjust the RA value that it chooses up or down, so that the guide scope takes a nice view at the screen. Focus the guide scope on the screen.

If you're not hitting the middle line (where all arrows are pointing to the left), adjust the height of your mount or the height of your simulator screen. A few 10th of pixels difference are ok.

Now we will move the mount back and forth in RA repeatedly to position the screen dead south of the mount:

If during the following procedure the sharpness of the image on left and right hand side is extremely different, orient the screen so, that it is perpendicular to your guide scope.
The best place to adjust focus is at 25% or 75% of the screen from left-to-right, there are vertical lines on the screen to find that position.

If your mount performs a meridian flip in between, check the meridian flip settings in your mount and adjust these so,
that a meridian flip is avoided and does not interfere with setting up BWMT. Then restart the procedure after these adjustments.

First, using the mount controls in your mount's driver, locate the left side of the monitor on the guide scope's picture. The picture displayed on the screen shows arrows,
that point you into the right corner of the screen. Just follow the arrows. When you have reached the destination indicated by a cross in the picture press `next` in the webbrowser.
The webbrowser will display horizontol lines and a pixel scale on each side of the screen.

Using the bullseye displayed by PHD2, center the zero-line in the bullseye (at first this does not have to be pixel-perfect) using your driver's mount control.

Second, using **ONLY** the RA axis, locate the right side of the screen on the guide scope's picture. If you're leaving the screen on top or bottom, stop there and adjust the axis of your mount
to point to the screen. Once you reach the right-hand-side, you will notice, that it's very problably showing a different line. Using the azimuth screws of you mount, rotate it such, that the mount will hit the same horizontal line
on both sides of the screen. A few pixel difference from left to right is ok.

Repeat this procedure until you're satisfied, that a symmetric arc will be traced on the monitor when fully moving from left-to-right. Then press `next`.

> [!WARNING]
> In this version the velocity that the star traces is calculated and valid for this geometry.
> If you use different orientations of the mount the velocity might not match and PHD2 might loose the star.

Move the mount to the left hand side of the screen and press `next`.

### Setting up the trace line

Now we will trace the mount's location accross the screen, to setup the average path that the mount takes across the screen. This entails:

1. Looking at the guide scopes picture in PHD2, and telling BWMT where the scope is looking
2. Moving the scope in RA for a few pixels
3. Repeating 1 and 2 until all the screen is crossed.

Step 1:
BWMT displays on the webpage a scaled down picture of the screen. When hovering with the mouse, a cross is displayed on the simulator screen at the location of the mouse.
Looking at PHD2's guide scope picture, move the mouse so that the cross is displayed in the middle of the bullseye, that PHD2 is overlaying on the picture. Right click to place the first alignment point.
Using curser keys, adjust to the cross to be at the center of the bullseye. The keys only work, if the cursor is hovering on the picture.

Step 2:
Using **ONLY** the RA axis, move the mount to the right, so that you can still see the previous alignment point. Then repeat step 1.

Step 3 .. N:
Repeat Steps 1 and 2 until you have alignment points spanning the whole distance on the screen from left to right.

BWMT will display an ellipse fit below the screen in the webbroswer. This will in the next step be used to simulate a star corssing the screen.

At last, move the mount to the left of the screen, then press `next`, to start measuring the velocity of your mount.

### Measuring velocity on screen

The next simulator display shows three areas, at which we are going to measure the velocity of the mount. Each area consists of a vertical stripe, one at the left, one in the middle and one to the right. The width of the stripes are chosen such,
that the mount will take approximately 3 min to cross it. The web page shows three entry fields, one for each stripe and a stop watch

Now move the mount to the left of the outer strip, start tracking with the bullseye overlay active on the screen and press "Start" once the bullseye center enters the left stripe. Press stop, when it leaves the stripe.
The time it took to cross the stripe is displayed on the web page. Now using **ONLY** movements in RA, move to the middle stripe and measure there. Then repeat this procedure with the right-hand stripe.

If you want to re-measure a stripe, click the clear button next to the corresponding entry field. Starting and stopping the stop watch will then put that measurement into this field.

After measuring the mounts velocity at each location, press `next`.

### Measuring a guiding run

#### Preparing measurement

BWMT will on left hand side (northern hemisphere, right hand side on southern hemisphere), where you placed the first alignment point, display a simulated star.
This star will have a gaussian profile that is sampled at the positions of the pixels. The diameter of this star will be roughly 3 pixels.
As the pixel resolution of the screen is fixed, you will have to adjust your guide camera and the focus of your guide scope such that the star profile displayes a smooth gaussian profile.

Center this "star" in PHD2 and click on it. If you have not displayed the "Star Profile" yet, activate it from the menu ("View" > "Display Star Profile").
Then adjust camera gain and exposure time so that the star profile is not clipped at the top (mesa shape). If you get a ragged profile (stemming from the different pixels simulated star), unfocus slightly.
Make sure that the star profile does not become too broad. The square displayed by PHD2 around the simulated star should always be green and it should not vanish in between. Check the message that is displayed
in the Star Profile view, if that happens. You may have to adjust PHD2 configuration settings to tell PHD2 to be more tolerant:

1. Disable "Star Mass Detection"
2. Disable "Use multiple stars"
3. Up the "Maximum star HFD (pixels)" setting to the max (10)

If you have difficulties to get a smooth star profile, consider:

- Adjusting the distance between scope and simulator screen: The wider the distance the smaller the pixels from the point of view of the guide scope
- Adjusting the focal length of the guide scope. By choosing a smaller focal length, the size of the displayed pixels will shrink, but your arcsec resolution will suffer
- Using a different guide camera with larger pixels
- Using a different screen, with a better resolution (higher dpi)

#### Measurement: Simulation Quality

Start looping in PHD2, then by moving the mount **ONLY** in RA, center the simulated star in PHD2's display. Click on the star and press "Begin Guiding" in PHD2.
PHD2 will complain that that this is a bad location for a calibration but start calibration anyway. The calibration should run through successfully and PHD2 will start guiding.
Check your mount driver, if PHD2 started tracking. If it did, stop tracking.

Now let PHD2 and the simulation run for a few minutes. Check the "Guide Stats" in PHD2: The RA RMS and Peak should give you an indication of how good the measurement will be. This value will not be zero,
as the screen's refresh cycle might overlap or otherwise influence the values of the guide camera. On the other hand, noise and other influences (e.g. vibrations of the building) will also move the camera and
screen relative to each other. Remember the pixel scale is on the order of µm, which is 1/60th of a hair and we are trying to measure movements on the order of a few arcsec (1 arcsec is the diameter of 1 Euro coin at 4.8 km distance).
Anyway, the values displayed are usually 1/10th of the pixel scale of the guide scope.
Depending on which periodic error you want to measure, make sure this figure is small enough to measure what you want.

Then move the simulated star to the 25% mark. For this you can click on the progress bar in the web application and use the "fast backward" and "fast forward" buttons. If you lost the position of the guide camera,
press back to display the alignment points to point your guide scope and locate the simulated star.

Repeat this procedure at 50%, 75% and 100% of the simulation. All these measurements should be congruent and give you similar figures for RMS RA.

If the figures are inconsistent and diverging from each other much:

- Check orientations of guide scope and Simulator screen
- Check a different focus setting of the guide scope
- Increase the distance between mount and Simulator screen

> [!NOTE]
> **Dec values may be different!**
>
> The Dec values in this chosen geometry are roughly parallel to the vertical lines of the screen. Due to screen updates usually going top down, noise in that direction might be much higher than noise in RA direction.
> This does not matter for measuring the periodic error of the mount.

#### Measurement: Guiding

> [!IMPORTANT]
> At the moment southern hemisphere mode is not supported yet.

> [!WARNING]
> During measurement avoid crossing the line of sight and walking around the mount and screen!
> Else PHD2 might loose the simulated guide star and stop guiding.
>
> Also do not walk next to the mount or the simulator screen, as depending on the floor you're measuring this on, your weight will create vibrations or changes of the floor that might travel to the mount or screen and
> create excursions.

Now return the simulation back to 0% by clicking the "back to start" button, and rotate the guide scope back to point at the simulated star.

Now it's time to start the simulation:

1. Start the simulation, by clicking on the play button in the webpage.
2. Using driver's controls start tracking in the mount
3. Start guiding in PHD2

BWMT will now display the time left, for the mount to cross the screen. One minute and again 30 seconds before the end is reached BWMT will beep. 10 seconds before the end of the simulation a countdown will start and BWMT will
beep 10 times. Use this to stop the mount.

Using **PHD2 Log Viewer** you can now analyse the performance of your mount.
