# Bad Weather Mount Tester Manual

!!! important
    At the moment southern hemisphere mode is not supported yet.

## Configure BWMT and your gear

Make sure you can startup BWMT as described here, before setting up the gear (can save a lot of walking).

### Setting up the Simulator

- Use a spirit level to position the simulator screen level horizontally and vertically. The screens middle pixel should
  be pointing to the mount.
- Make sure the Simulator is on the same network / WiFi as the Astro Computer and that this network is connected to the
  internet.
- Install python 3.10 or later on it and check that it works:
- Open a terminal on the Simulator and run `python --version`, the number displayed should at least be 3.10.
- Then run `pip install BadWeatherMountTester` in the terminal. This installs the Bad Weather Mount Tester on it (both
  client and server). For other options, how to in stall consult the section "Installation Options"
- Then run `python -m BadWeatherMountTester`. The program will open and show it's logo, display "Waiting for a
  connection" and the network address to connect to.

<figure markdown="span">
  ![BWMT waiting for connection](BWMT_waiting.png)
  <figcaption>Figure 1: BWMT waiting for connection</figcaption>
</figure>

### Setting up your Astro Computer

- Make sure the Astro Computer is on the same network / WiFi as the Simulator
- Open up a web browser on your astro computer and enter the network address displayed on the Simulator's screen.
- The simulator will then change the display to its locator screen, that will help you find the exact location on the
  screen with your guide scope. Note the small red cross on left hand side (or right hand side)

<figure markdown="span">
  ![BWMT waiting for connection](BWMT_configure.png)
  <figcaption>Figure 2: BWMT locator screen (Configure tab)</figcaption>
</figure>

### Setting up your astro gear

- Fix your guiding gear on the (new) mount. Make sure you can control the mount using your Astro Computer, the camera
  and that you can run PHD2 and that it is able to control the correct camera.
- Place the simulator and its monitor in a distance approximately 5 m dead south of your mount (on northern hemisphere,
  dead north on southern hemisphere). With "dead south" we mean, that when standing north of the mount (where the
  polarscope is pointing to), looking south along the RA axis, that line will hit the middle of the screen of the
  simulator. We will fine tune that in one of the next steps.
- Now start BWMT on the simulator and connect to the Simulator using a web browser on your Astro Computer using the
  connection string that is displayed on the simulator screen. BWMT will display a screen full of arrows on the
  simulator screen (see Figure 2) and the web page will display the configuration screen.
- Fill in all information in the configuration screen (see figure below):

<figure markdown="span">
  ![Configuration screen with information that need to be entered into BWMT](BWMT_web_configure.png)
  <figcaption>Figure 3: The configuration screen of BWMT's web interface. TODO - fix wording</figcaption>
</figure>

Enter the appropriate values for your setup into the configuration screen.

First enter the **Mount Configuration**:

- **Latitude (degrees)**: What is the latitude your mount is configured for? Enter a decimal values such as 51.5 (you
  can use both "." and "," as decimal points) Convert from sexagesimal degree (dd° mm') as follows: dd + mm / 60.
- **Guide Scope Focal Length (mm)**: Use the effective length of your guide scope, i. e. if you're using a guide scope
  of 420mm and a reducer of x0.5, enter 210. Use mm as unit.
- **Distance to Screen (m)**: Rotate the RA-axis, so that the Dec-axis is level. Provide the distance from the Dec
  rotational axis to the screen.
- **Mount main period**: Provide the mounts main period, i.e. for a worm drive mount that is tracking at sidereal
  rate, the time it takes the worm gear to rotate once. (At the moment this value is optional and for informational
  purposes only)

Now enter the **Guide Camera** Information:

- **Pixel Size (micrometer)**: What is the size of a pixel in µm? We assume square pixels.
- **Width (pixels)**: How many pixels are there in horizontal direction?
- **Height (pixels)**: How many pixels are there in vertical direction?

At last enter **Screen** information:

- **Simulator Screen Width**: Use a ruler and measure the width of the display area of the screen, i.e. the distance
  from the left-most to the right most pixel.

In the **Calculated Values** section, BWMT displays the following infos:

- **Effective FL for PHD2**: This is the effective focal length you need to configure in PHD2's guiding profile. Since
  your guide scope is focused on the simulator screen at close range (typically 5 m) rather than at infinity, the
  effective focal length differs from the actual focal length. BWMT calculates this using the lens equation:
  `effective_fl = (focal_length × distance) / (distance - focal_length)`. This ensures that PHD2 displays correct
  arcsecond measurements during guiding.

- **Recommended Binning**: This value indicates the optimal camera binning to use in PHD2. BWMT calculates this so that
  one binned camera pixel has approximately the same angular resolution (arcsec/px) as one simulator screen pixel. If
  the recommended binning is higher than 1, configure your camera accordingly in PHD2. If that binning is not availabe,
  choose the most closely matching one, that is available.

- **Measurement Duration**: This shows the estimated time (in minutes) it will take for the mount to traverse the entire
  simulator screen at sidereal tracking rate (15 arcsec/second). The calculation accounts for the angular width of the
  screen as seen from the mount's position and adjusts for your latitude, since stars move slower across the sky the
  further you are from the equator (by a factor of cos(90° - latitude)). This is a coarse estimate, as the value depends
  on the exact geometry of how your guidescope is in relation to the RA-axis.

- **Area on Simulator**: This displays the physical dimensions (width × height in mm) of the area on the simulator
  screen that your guide camera can see through the guide scope. BWMT calculates this from your camera's sensor size and
  the effective focal length using the lens equation for near-focus imaging. This helps you verify that your field of
  view is appropriately sized for the measurements.

- **Dec target**: This is the declination value to enter into PHD2's Calibration Assistant when slewing the mount to the
  simulator screen. It is calculated as negative 90° minus your latitude. For example, at latitude 51.5° the Dec target
  is 38.5°. This points the mount roughly at the simulator screen's elevation above the horizon.

Now we are good to go and need to setup PHD2. So follow the instructions that are displayed on the simulator
screen, which provide a reminder, if you're not looking at this manual

### Setting up PHD2

Open PHD2 on your astro computer and **create a new profile** using the <u>New Profile Wizard</u>. How to do this
depends on the brand of your mount and guidescope. Please consult [PHD2
documentation](https://openphdguiding.org/man/Basic_use.htm#New_profile_wizard) in how to do this.

In advanced settings in PHD2 (the "brain"), disable multi-star guiding, as we will use a single simulated star. You can
also disable "Star Mass Detection" and decrease "Mininum Star HFD (pixels)" and increase "Maximum Star HDF (pixels)" as
shown in this screenshot, but this should work ok for most setups (This would make PHD2 more tolerant for "peculiar"
stars):

<figure markdown="span">
  ![PHD2 Advanced Setting Dialog > Guiding: Multistar Guiding is disables](PHD2_disable_multistarguiding.png)
  <figcaption>Figure 4: In PHD2's "Advanced Settings" > "Guiding" disable "Use multiple stars".</figcaption>
</figure>

Then connect to your guidescope and mount and start looping. If your mount is not yet in home position, move it to home
position, i.e. the guidescope should point along the RA axis to where the polar scope would be pointing, if you were
outside. It is important to always start from the home position, so that PHD2 and the mount driver have a reference
position, providing orientation.

<figure markdown="span">
  ![Home Position of a Mount](BWMT_home_position.jpg)
  <figcaption>Figure 5: In "Home" position, the scope points along the RA axis to the celestial pole.</figcaption>
</figure>

Now open "Tools" > "Calibration Assistant", and have PHD2 command the mount to slew to the simulator screen:

- Enter 5 into the "Calibration Location" > "Meridian offset (degrees)" box (which is the default) and
- the "Dec target" value from BWMT's Calculated Values section for "Declination" (this is 90° - Latitude). On northern
  hemisphere, you need to enter a negative value, on southern hemisphere use the positive value.

Click "Slew".

<figure markdown="span">
  ![Use the PHD Calibration Assistant to slew the mount to the screen](PHD2_CalibrationAssistant.png)
  <figcaption>Figure 6: Enter (90°-Latitute) into the "Declination" filed. Adjust "Meridian Offset" to roughly point on
  the left-hand-side of the screen. Check the "Pointing" field to determine the side of pier.</figcaption>
</figure>

The mount should now point roughly at the simulator screen. If it doesn't adjust the values in the "Calibration
Assistant" dialog and press "Slew" again.

<figure markdown="span">
  ![Guide scope pointing at the simulator screen](BWMT_scope_pointing_at_screen.jpg)
  <figcaption>Figure 7: The scope points roughly at the simulator screen's left-hand-side.</figcaption>
</figure>

Check your mount driver, because PHD2 enabled sidereal tracking. **Disable tracking**, if it is
enabled. Then click "Cancel" in the Calibration Assistant. Start looping in PHD2 and focus your guidescope on the screen.
As it is not pointing at infinity, you may need to add extensions to reach focus position.

<figure markdown="span">
  ![Extensions will almost certainly be necessary to focus](BWMT_extensions.jpg)
  <figcaption>Figure 8: You will almost certainly need to add extensions to get into focus (The scope is a 70/420 with
  ‚a x0.5 Reducer).</figcaption>
</figure>

<figure markdown="span">
  ![Focus achieved](BWMT_focus_achieved.png)
  <figcaption>Figure 9: Focus achieved on the simulator screen, from with-in PHD2.</figcaption>
</figure>

In PHD2 enable the Bullseye overlay from "View" > "Bullseye". Using **only movements in RA** with the mount control
buttons in your mount driver, follow the arrows to point the mount at left side of the screen. Once you're there you've
mastered the first step.

<figure markdown="span">
  ![LHS of screen, at ideal heigth](BWMT_ideal_height.png)‚
  <figcaption>Figure 10: Left-hand-side of screen, in ideal height.</figcaption>
</figure>

Press `next`to go to the alignment screen.

## Aligning Mount and Screen

For the next step you need to be in the "Align" screen:

<figure markdown="span">
  ![BWMTs display for alignment shows horizontal lines. In the middle of a screen is a red 'zero' line. Then parallel
  to that horizontal lines in a distance of 50 pixel are displayed.](BWMT_align.png)
  <figcaption>Figure 11: Simulator screen displayed for Alignment</figcaptoin>
</figure>

### Adjusting height of Screen and Mount

Now that you're pointing at the left side of the screen, adjust the height of mount and screen such, that while the
guidescope is nearly horizontal from the slew (executed with "Drift Align" above), it is pointing at the middle of the
screen, indicated by the red line and a display of 'zero' on right- and left-hand-side.

For this coarsely adjust the height of your mount first, then use the screens height adjustment, if present.
Last, for fine adjustment, use the mount control buttons in your mount driver software.

<figure markdown="span">
  ![Height was adjusted](BWMT_left-hand-side.png)
  <figcaption>Figure 12: Height was adjusted and guidescope is pointing at the middle of the aligment screen (left-hand-side).
  </figcaption>
</figure>

## Placing BWMT dead south of the mount

!!! note
    The following text was written for northern hemisphere. For Southern hemisphere the same procedure applies but the mount
    will be moving right-to-left instead of left-to-right and North and South will be exchanged.

Now we will move the mount back and forth in RA repeatedly to position the screen dead south of the mount.

If during the following procedure the sharpness of the image on left and right hand side is extremely different, orient
the screen so, that it is perpendicular to your guide scope. The best place to adjust focus is at 25% or 75% of the
screen from left-to-right, on the "Configure" screen there are vertical lines to find that position.

If your mount performs a meridian flip in between, check the meridian flip settings in your mount and adjust these so,
that a meridian flip is avoided and does not interfere with setting up BWMT. Then restart the procedure after these
adjustments.

### Alignment Procedure

First, using the mount controls in your mount's driver, locate the left side of the monitor on the guide scope's picture
(If you followed the manual so far, you should already be there). The simulator screen will display horizontol lines and
a pixel scale on each side of the screen.

Using the bullseye displayed by PHD2, center the zero-line in the bullseye (at first this does not have to be
pixel-perfect) using your driver's mount control.

Second, using **ONLY** the RA axis, locate the right side of the screen on the guide scope's picture. If you're leaving
the screen on top or bottom, stop there and adjust the axis of your mount to point to the screen. Once you reach the
right-hand-side, you will notice, that it's very problably showing a different line. Using the azimuth screws of you
mount, rotate it such, that the mount will hit the same horizontal line on both sides of the screen. A few pixel
difference from left to right is ok.

<figure markdown="span">
  a)
  ![BWMT mount aligned left-hand-side](BWMT_left-hand-side.png){width="40%"}
  b)
  ![BWMT right-hand-side](BWMT_right-hand-side.png){width="40%"}
  <figcaption>Figure 13: Orientation of screen and guide scope achieved: The bullseye crosses the center line of the
  screen on both a) left-hand-side and b) right-hand-side.</figcaption>
</figure>

Repeat this procedure until you're satisfied, that a symmetric arc will be traced on the monitor when fully moving from
left-to-right.

Move the mount to the left hand side of the simulator screen and press `next`.

## Calibrating the simulator

You should now be in the "Calibrate" tab.

<figure markdown="span">
  ![BWMT Calibration Screen](BWMT_web_calibration.png)
  <figcaption>Figure 14: The Calibration Screen</figcaption>
</figure>

Now we will trace the mount's location accross the screen, to setup the average path that the mount takes across the
screen. This entails:

1. Looking at the guide scopes picture in PHD2, and telling BWMT where the scope is looking
2. Moving the scope in RA for a few pixels
3. Repeating 1 and 2 until all the screen is crossed.

**Step 1**: BWMT displays on the webpage a scaled down picture of the screen ("Calibration Preview"). When hovering with
the mouse, a cross is displayed on the simulator screen at the location of the mouse. Looking at PHD2's guide scope
picture, move the mouse so that the cross is displayed in the middle of the bullseye, that PHD2 is overlaying on the
picture. Right click to place the first alignment point. Using curser keys, adjust to the cross to be at the center of
the bullseye. The keys only work, if the cursor is hovering on the picture.

<figure markdown="span">
  a) Hovering on the web page, shows a crosshair on both the Calibration Preview (right) and the simulator screen
  (PHD2 image, left)
  ![Step 1a: Hover and point crosshar](BWMT_calibration_step1a.png)

  b) left-click with the mouse creates a calibration point (15 in this case).
  ![Step 1b: Click to place a calibration point](BWMT_calibration_step1b.png)

  c) fine adjust position to center crosshair in bullseye using cursor keys or s,d,f and e.
  ![Step 1c: Using cursor keys, place calibration point at center of bullseye](BWMT_calibration_step1c.png)
  <figcaption>Figure 15: Steps to create a calibration point.
</figure>

**Step 2**: Using **ONLY** the RA axis, move the mount to the right, so that you can still see the previous alignment
point. Then repeat step 1.

<figure markdown="span">
  ![Step 2: move mount to add next calibration point](BWMT_calibration_step2.png)
  <figcaption>Figure 16: Move mount to create the next calibration point.</figcaption>
</figure>

**Step 3 .. N**: Repeat Steps 1 and 2 until you have alignment points spanning the whole distance on the screen from
left to right.

BWMT will display an ellipse fit below the screen in the webbrowser. This will in the next step be used to simulate a
star crossing the screen.

<figure markdown="span">
  ![All calibration points set](BWMT_calibration_complete.png)
  <figcaption>Figure 17: Repeat calibration steps, to cover the whole simulator screen. This completes the calibration.</figcaption>
</figure>

At last, move the mount to the left of the screen, then press `next`, to start measuring the velocity of your mount.

## Measuring on Screen Velocity

!!! info
    You probably know about sidereal, lunar and solar tracking velocities. These velocities apply in the
    case where the telescope is directly mounted to the intersection point of conic sections.

The next simulator display shows three areas, at which we are going to measure the velocity of the mount. Each area
consists of a vertical stripe, one at the left, one in the middle and one to the right. The width of the stripes are
chosen such, that the mount will take approximately 3 min to cross it.

<figure markdown="span">
  ![For measuring velocity three stripes are displayed](BWMT_velocity.png)
  <figcaption>Figure 18: 3 stripes to measure the velocity, one on left, middle and right.</figcaption>
</figure>

The web page shows three "recorded times", one for each stripe and a stop watch on top. Clicking on "left", "middle" or
"right" in the stop watch selects the recorded time for that stripe.

<figure markdown="span">
  ![For measuring velocity the web page allows to stop the time to cross the stripes](BWMT_web_velocity.png)
  <figcaption>Figure 19: The web page to measure on screen velocities. Choose the respective stripe by clicking on "Left",
  "Middle" or "Right", then use the Start/Stop, Reset buttons to measure how long it takes the mount to cross the stripe.
  </figcaption>
</figure>

Chose a very short exposure time for your camera. The smallest value, that PHD2 supports is 0.1s. Try to avoid
saturation, but in principle it doesn't matter.

Now move the mount to the left of the outer strip, start tracking with the bullseye overlay active on the screen and
press "Start" once the bullseye center enters the left stripe. Take care to avoid any reflection of the stripe on the
screen casing. Press stop, when it leaves the stripe. The time it took to cross the stripe is displayed on the web page.
Now using **ONLY** movements in RA, move to the middle stripe and measure there. Then repeat this procedure with the
right-hand stripe.

<figure markdown="span">
  ![During a velocity measurement](BWMT_velocity_running.png)
  <figcaption>Figure 20: While the measurement for the left hand stripe is running. Note that the mount is tracking
  (Tracking "on").</figcaption>
</figure>

If you want to re-measure a stripe, click the clear button next to the corresponding entry field. Starting and stopping
the stop watch will then put that measurement into this field.

After measuring the mounts velocity at each location, press `next`, you're now in the "Measure tab" of the web interface.
and the Simulation Controls are displayed.

## Qualification of Measurement Setup

For the following you need to be in the "Measure" tab of the web interface, where simulation control is displayed:

<figure markdown="span">
  ![BWMT Simulation Control](BWMT_web_measure.png)
  <figcaption>Figure 21: The simulation control.</figcaption>
</figure>

### Prerequisits for good measurements

#### Matching Exposure time

The PHD2 mailing list recommends an exposure time of 1 - 3s, if you've got a worm gear mount and 0.5 - 1s for strain
wave gear mounts. Choose an exposure time that is fitting to that. You probably will have to add a neutral density
filter to your camera or in fron of your guidescope to avoid saturation.

#### Get a Good Star Profile (Averaging Pixels)

As we are imaging the pixels from the simulator screen, we need to make sure that the camera doesn't pick up that pixel
structure, but at least averages that pixel structure out.

Take for example this focused view of the "LEFT" printed along the stripe from the velocity measurement step:

<figure markdown="span">
  ![Focused star profile, showing pixel structure of simulator screen](BWMT_pixelstructure.png)
  <figcaption>Figure 22: PHD2's Star Profile tool showing pixels.</figcaption>
</figure>

As you can see the star profile is ragged, and does not consist of a single "hump" with symmetric appearance. This will
then also be the case for the simulated star, but not as pronounced:

<figure markdown="span">
  a)
  ![Focused star profile, showing pixel structure of simulator screen](BWMT_pixelstructure_star.png)
  b)
  ![Unfocused star profile, showing a symmetric structure](BWMT_pixelstructure_unfocused.png)
  <figcaption>Figure 23: PHD2's Star Profile tool showing pixels in a), and a more symmetric profile when unfocused b).
  </figcaption>
</figure>

In order to improve the star profile for measurements, you can do the following:

- Increase distance between mount and simulator screen. Decreases arcsec / px for the simulator screen.
- Reduce the focal length of your guidescope. Decreases arcsec / px for the guidescope image.
- Use a different guide camera with larger pixels
- Use a different screen, with a better resolution (higher dpi)
- unfocus the guidescope. Artifically smears out the pixel structure

#### Rock solid floor

In my case, I am conducting measurements in an old building that has wooden floors, so that people that are walking next
to the mount or next to the simulator screen can create excursions of more than 20", i.e. the picture of the simulated
star is changing its position by approximately 6 pixels or a distance of 21µm. This is about a 1/3rd of a human hair.

It may even be the case, that people slamming doors or otherwise introducing energy or vibrations into the house (like
bouncing a ball) will be noticed by your measurement setup.

If you've got the choice, make sure that the floor your mount in standing on and any furniture the simulator screen is
standing on are exremely sturdy. At least (if possible) make sure that these kind of things do not happen during your
measurements (people walking around or bouncing balls)

#### Exposure Time and Screen Refresh

BWMT is configured to refresh the screen every 1/60th of a second or equivalently every 0.017 seconds. The exposure time
of the guidecam should therefore be different from that rate.

### Statistical Measurement Error

When entering the "measurement" tab, BWMT will on left hand side (northern hemisphere, right hand side on southern
hemisphere), where you placed the first alignment point, display a simulated star. This star will have a gaussian
profile that is sampled at the positions of the pixels. The diameter of this star will be roughly 3 pixels.

Let's see, which statistical fluctuations the measurement setup is reporting. These can be: air currents, cables
tugging, imbalances in RA and Dec, vibrations present in the building from people or cars driving on the street, the
higher temperature of the mount and its lubricants (comparing inside to outside temperatures), fluctuations due to
backlash (in Dec), etc.

In order to measure this we create a situation, where nothing should be changing: We disable all motors and all
movements of the simulated star. So disable tracking in the mount driver and make sure that the simulation is stopped in
BWMT's "Measure" web interface.

Start looping in PHD2, if it is not already running. Then move the mount **only in RA** to display the simulated star,
click on the simulated star to select it for guiding and then &lt;SHIFT&gt;-click or click on the "Start Guiding" icon
in PHD2.

Using shift-click you can force a calibration. As we have created a new profile above, a new calibration should be
created now. You should force a new calibration, if you have an old one active (PHD2 usually re-uses a good
calibration), but you changed the optical train, e.g. by adding a neutral density filter to get into the right exposure
range.

Let it run for a while. Now use PHD2 Log Viewer to have a look at the Log.

<figure markdown="span">
  ![BWMT ](BWMT_statistical_error.png)
  <figcaption>Figure 24: Guiding while "nothing is moving". Distance between gray lines is 1". </figcaption>
</figure>

The things that you can take from this are

- Even if "nothing is moving", PHD2 recognizes different locations of the simulated guide star
- The movement looks like a random walk
- The scatter plot of the selected section is largely symmetric
- There was a large excursion, due to people walking in the room (deselected)
- RA RMS is reported to be 0.09px, that means averaging yields measurements that are "good" up to 1/10th of a guidecam
  pixel.
- Dec RMS, is slightly larger at 0.12px
- Drift is on the order of half of that (where there should be no drift)
- Polar alignment error is reported to be 1.4'

Given the same guidecam and guidescope and similar load on the mount, it will be hard to achieve better values than this.

Repeat this measurement at position 25%, 50%, 75% and 100%. For this you can click on the progress bar in the web
application and use the "fast backward" and "fast forward" buttons. If you lost the position of the guide camera, press
`back` to display the alignment points to point your guide scope and locate the simulated star.

All these measurements should be congruent and give you similar figures for RMS RA.

If the figures are inconsistent and diverging from each other much:

- Check orientations of Guide Scope and Simulator screen
- Check a different focus setting of the guide scope
- Check for cable tugging, and
- Imbalances in RA and Dec

## Measuring a guiding run

First we need to have PHD2 optimize it's  guiding parameters using the Guiding Assistant, then we can perform measurements.

### Guiding Assistant run

Now let's run PHD2's guiding assistant. This switches off guiding and just follows the movement of the stars and directly
records the position of the guide star on the camera.

For this to happen, do this:

- Move to the left of the simulated star and enable tracking in the mount.
- When the guidecam picture has the star approximately in the center, start simulation in BWMT's web interface.
- Open up PHD2 "Tools" > "Guiding Assistant", select the simulated star, if it is not already selected, then start guiding.
- Let "Measure Declination Backlash" enabled, then press "Start".
- Let it run for at least one full revolution of the worm gear (see "elapsed time" in the top-right table).
- Check that time against he remaining simulation time, that is displayed on the simulator screen.
- Wait
- Press "Stop" in the guiding assistant.
- Accept all changes that the guiding assistant recommends.

!!! bug
    The velocity, with which the simulator crosses the screen is systematically too high.
    The reason for that is at the moment unknown. Any help is appreciated.
    If all else fails, a future version will contain a slider to tune velocity up or down.

### Measurement: Guiding

!!! warning During measurement avoid crossing the line of sight and walking around the mount and screen! Else PHD2 might
    loose the simulated guide star and stop guiding.

    Also do not walk next to the mount or the simulator screen, as depending on the floor you're measuring this on, your
    weight will create vibrations or changes of the floor that might travel to the mount or screen and
    create excursions.

Return the simulation back to 0% by clicking the "back to start" button, and rotate the guide scope back to point at
the simulated star.

Now it's time to start the simulation:

1. Using driver's controls start tracking in the mount
2. Start the simulation, by clicking on the play button in the webpage.
3. Start guiding in PHD2
4. Once the simulation is going to end, first stop guiding in PHD2.
5. Stop tracking of the mount

BWMT will now display the time left, for the mount to cross the screen. One minute and then again 30 seconds before the
end is reached BWMT will beep, the screen that is attached to the simulator has a speaker. 10 seconds before the end of
the simulation a countdown will start and BWMT will beep 10 times. Use this to stop the mount.

Using **PHD2 Log Viewer** you can now analyse the performance of your mount.
