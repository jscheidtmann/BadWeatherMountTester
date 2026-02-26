# Bad Weather Mount Tester Handbuch

Dieses Handbuch dokumentiert Version 0.9.0 von Bad Weather Mount Tester.

## BWMT und deine Ausrüstung konfigurieren

Stelle sicher, dass du BWMT starten kannst, wie hier beschrieben, bevor du die Ausrüstung aufbaust (das kann viel Laufen sparen).

### Den Simulator einrichten

- Verwende eine Wasserwaage, um den Simulator-Bildschirm horizontal und vertikal auszurichten. Das mittlere Pixel des Bildschirms sollte auf die Montierung zeigen.
- Stelle sicher, dass der Simulator im selben Netzwerk / WLAN wie der Astro-Computer ist und dass dieses Netzwerk mit dem Internet verbunden ist.
- Installiere Python 3.10 oder neuer darauf und prüfe, dass es funktioniert:
- Öffne ein Terminal am Simulator und führe `python --version` aus; die angezeigte Zahl sollte mindestens 3.10 sein.
- Führe dann `pip install BadWeatherMountTester` im Terminal aus. Dies installiert den Bad Weather Mount Tester darauf (sowohl Client als auch Server). Für andere Installationsoptionen lies den Abschnitt "Installationsoptionen".
- Führe dann `python -m BadWeatherMountTester` aus. Das Programm öffnet sich und zeigt sein Logo an, zeigt „Warte auf Verbindung" und die Netzwerkadresse zum Verbinden an.

<figure markdown="span">
  ![BWMT wartet auf Verbindung](BWMT_waiting.png)
  <figcaption>Abbildung 1: BWMT wartet auf Verbindung</figcaption>
</figure>

### Den Astro-Computer einrichten

- Stelle sicher, dass der Astro-Computer im selben Netzwerk / WLAN wie der Simulator ist.
- Öffne einen Webbrowser auf deinem Astro-Computer und gib die auf dem Bildschirm des Simulators angezeigte Netzwerkadresse ein.
- Der Simulator wechselt dann die Anzeige zu seinem Suchbildschirm, der dir hilft, den genauen Ort auf dem Bildschirm mit deinem Leitfernrohr zu finden. Beachte das kleine rote Kreuz auf der linken Seite (oder rechten Seite).

<figure markdown="span">
  ![BWMT wartet auf Verbindung](BWMT_configure.png)
  <figcaption>Abbildung 2: BWMT Lokalisierungsbildschirm (Configure-Tab)</figcaption>
</figure>

### Deine Astro-Ausrüstung einrichten

- Befestige deine Nachführausrüstung an der (neuen) Montierung. Stelle sicher, dass du die Montierung über deinen Astro-Computer steuern kannst, die Kamera funktioniert und du PHD2 ausführen kannst, das in der Lage ist, die richtige Kamera zu steuern.
- Stelle den Simulator und seinen Monitor in einer Entfernung von ca. 5 m genau südlich deiner Montierung (auf der Nordhalbkugel, genau nördlich auf der Südhalbkugel). Mit „genau südlich" meinen wir, dass wenn man nördlich der Montierung steht (wo der Polarsucher zeigt), nach Süden entlang der RA-Achse schaut, diese Linie die Mitte des Bildschirms des Simulators trifft. Das werden wir in einem der nächsten Schritte feinjustieren.
- Starte jetzt BWMT auf dem Simulator und verbinde dich über einen Webbrowser auf deinem Astro-Computer mit dem Simulator, indem du den auf dem Simulatorbildschirm angezeigten Verbindungsstring verwendest. BWMT zeigt auf dem Simulatorbildschirm einen Bildschirm voller Pfeile an (siehe Abbildung 2) und die Webseite zeigt den Konfigurationsbildschirm an.
- Fülle alle Informationen im Konfigurationsbildschirm aus (siehe folgende Abbildung):

<figure markdown="span">
  ![Konfigurationsbildschirm mit Informationen, die in BWMT eingegeben werden müssen](BWMT_web_configure.png)
  <figcaption>Abbildung 3: Der Konfigurationsbildschirm der BWMT-Weboberfläche. TODO - Beschriftung korrigieren</figcaption>
</figure>

Gib die passenden Werte für dein Setup in den Konfigurationsbildschirm ein.

Gib zunächst die **Montierungskonfiguration** ein:

- **Breite (Grad)**: Auf welche Breite ist deine Montierung ausgerichtet? Gib einen Dezimalwert wie z. B. 51,5 ein (du kannst sowohl "." als auch "," als Dezimaltrennzeichen verwenden). Umrechnung von Sexagesimalgrad (dd° mm'): dd + mm / 60.
- **Brennweite des Leitfernrohrs (mm)**: Verwende die effektive Länge deines Leitfernrohrs; wenn du z. B. ein Leitfernrohr mit 420 mm und einen Reducer von x0,5 verwendest, gib 210 ein. Verwende mm als Einheit.
- **Entfernung zum Bildschirm (m)**: Drehe die RA-Achse, so dass die Dec-Achse waagerecht ist. Gib die Entfernung von der Dec-Rotationsachse zum Bildschirm an.
- **Hauptperiode der Montierung**: Gib die Hauptperiode der Montierung an, d. h. bei einer Schneckengetriebe-Montierung, die mit siderischer Geschwindigkeit nachführt, die Zeit, die das Schneckenrad für eine vollständige Umdrehung benötigt. (Dieser Wert ist im Moment optional und dient nur zu Informationszwecken.)

Gib jetzt die **Leitkamera**-Informationen ein:

- **Pixelgröße (Mikrometer)**: Wie groß ist ein Pixel in µm? Wir nehmen quadratische Pixel an.
- **Breite (Pixel)**: Wie viele Pixel gibt es in horizontaler Richtung?
- **Höhe (Pixel)**: Wie viele Pixel gibt es in vertikaler Richtung?

Gib schließlich **Bildschirm**-Informationen ein:

- **Simulator-Bildschirmbreite**: Verwende ein Lineal und messe die Breite des Anzeigebereichs des Bildschirms, d. h. den Abstand vom äußerst linken bis zum äußerst rechten Pixel.

Im Abschnitt **Berechnete Werte** zeigt BWMT folgende Informationen an:

- **Effektive Brennweite für PHD2**: Dies ist die effektive Brennweite, die du in PHD2's Nachführprofil konfigurieren musst. Da dein Leitfernrohr auf den Simulatorbildschirm in geringer Entfernung (typischerweise 5 m) statt auf Unendlich fokussiert ist, weicht die effektive Brennweite von der tatsächlichen Brennweite ab. BWMT berechnet dies mit der Linsengleichung: `effective_fl = (focal_length × distance) / (distance - focal_length)`. Dies stellt sicher, dass PHD2 korrekte Bogensekunden-Messungen während der Nachführung anzeigt.

- **Empfohlenes Binning**: Dieser Wert gibt das optimale Kamera-Binning für PHD2 an. BWMT berechnet diesen Wert so, dass ein gebinntes Kamerapixel ungefähr die gleiche Winkelauflösung (Bogensekunden/px) hat wie ein Simulatorbildschirm-Pixel. Wenn das empfohlene Binning höher als 1 ist, konfiguriere deine Kamera entsprechend in PHD2. Falls dieses Binning nicht verfügbar ist, wähle das am nächsten passende verfügbare.

- **Messdauer**: Zeigt die geschätzte Zeit (in Minuten) an, die die Montierung benötigt, um den gesamten Simulatorbildschirm bei siderischer Nachführgeschwindigkeit (15 Bogensekunden/Sekunde) zu überqueren. Die Berechnung berücksichtigt die Winkelbreite des Bildschirms von der Position der Montierung aus und passt sich an deine Breite an, da Sterne umso langsamer über den Himmel ziehen, je weiter du vom Äquator entfernt bist (um einen Faktor cos(90° - Breite)). Dies ist eine grobe Schätzung, da der Wert von der genauen Geometrie abhängt, wie dein Leitfernrohr in Bezug auf die RA-Achse ausgerichtet ist.

- **Bereich auf dem Simulator**: Zeigt die physikalischen Abmessungen (Breite × Höhe in mm) des Bereichs auf dem Simulatorbildschirm an, den deine Leitkamera durch das Leitfernrohr sehen kann. BWMT berechnet dies aus der Sensorgröße deiner Kamera und der effektiven Brennweite unter Verwendung der Linsengleichung für Nahfokus-Bildgebung. Dies hilft dir zu überprüfen, ob dein Gesichtsfeld für die Messungen angemessen groß ist.

- **Dec-Ziel**: Dies ist der Deklinationswert, der in PHD2's Kalibrierungsassistenten eingegeben werden muss, wenn die Montierung auf den Simulatorbildschirm geschwenkt wird. Er wird als -(90° - Breite) für die Nordhalbkugel berechnet. Zum Beispiel beträgt das Dec-Ziel bei einer Breite von 51,5° -38,5°. Dies richtet die Montierung ungefähr auf die Höhe des Simulatorbildschirms über dem Horizont aus.

!!! tip "Südhalbkugel"
    Das Dec-Ziel ist positiv: +(90° - |Breite|). Zum Beispiel beträgt das Dec-Ziel bei einer Breite von 34°S +56°.

Jetzt können wir loslegen und müssen PHD2 einrichten. Folge also den Anweisungen, die auf dem Simulatorbildschirm angezeigt werden, die eine Erinnerung darstellen, wenn du nicht in dieses Handbuch schaust.

### PHD2 einrichten

Öffne PHD2 auf deinem Astro-Computer und **erstelle ein neues Profil** mit dem <u>New Profile Wizard</u>. Wie das geht, hängt von der Marke deiner Montierung und deines Leitfernrohrs ab. Bitte lies die [PHD2-Dokumentation](https://openphdguiding.org/man/Basic_use.htm#New_profile_wizard) dazu.

Deaktiviere in den erweiterten Einstellungen von PHD2 (dem "Gehirn") die Multi-Stern-Nachführung, da wir einen einzelnen simulierten Stern verwenden. Du kannst auch "Star Mass Detection" deaktivieren sowie "Minimum Star HFD (pixels)" verringern und "Maximum Star HFD (pixels)" erhöhen, wie in diesem Screenshot gezeigt, aber das sollte bei den meisten Setups in Ordnung sein (dies würde PHD2 toleranter für "besondere" Sterne machen):

<figure markdown="span">
  ![PHD2 Erweiterte Einstellungen > Nachführung: Multistar-Nachführung ist deaktiviert](PHD2_disable_multistarguiding.png)
  <figcaption>Abbildung 4: In PHD2's „Erweiterte Einstellungen" > „Nachführung" „Mehrere Sterne verwenden" deaktivieren.</figcaption>
</figure>

Verbinde dann dein Leitfernrohr und deine Montierung und starte das Loopping. Wenn deine Montierung noch nicht in der Ausgangsposition ist, bewege sie in die Ausgangsposition, d. h. das Leitfernrohr sollte entlang der RA-Achse dorthin zeigen, wohin der Polarsucher zeigen würde, wenn du draußen wärst. Es ist wichtig, immer von der Ausgangsposition aus zu starten, damit PHD2 und der Montierungstreiber eine Referenzposition haben und die Orientierung kennen.

<figure markdown="span">
  ![Ausgangsposition einer Montierung](BWMT_home_position.jpg)
  <figcaption>Abbildung 5: In der „Ausgangsposition" zeigt das Fernrohr entlang der RA-Achse zum Himmelspol.</figcaption>
</figure>

Öffne jetzt „Tools" > „Calibration Assistant" und lasse PHD2 die Montierung auf den Simulatorbildschirm schwenken:

- Gib 5 in das Feld „Calibration Location" > „Meridian offset (degrees)" ein (das ist der Standardwert) und
- den „Dec-Ziel"-Wert aus dem Abschnitt „Berechnete Werte" von BWMT für „Declination" (das ist 90° - Breite). Auf der Nordhalbkugel musst du einen negativen Wert eingeben, auf der Südhalbkugel einen positiven.

!!! tip "Südhalbkugel"
    Verwende einen Meridian-Offset von -5° statt +5°, damit PHD2 auf die rechte Seite des Bildschirms schwenkt statt auf die linke.

Klicke auf „Slew".

<figure markdown="span">
  ![Verwende den PHD Kalibrierungsassistenten, um die Montierung auf den Bildschirm zu schwenken](PHD2_CalibrationAssistant.png)
  <figcaption>Abbildung 6: Gib (90°-Breite) in das Feld „Declination" ein. Passe den „Meridian Offset" an, um ungefähr auf die linke Seite des Bildschirms zu zeigen. Prüfe das Feld „Pointing", um die Seite des Meridians zu bestimmen.</figcaption>
</figure>

Die Montierung sollte jetzt ungefähr auf den Simulatorbildschirm zeigen. Falls nicht, passe die Werte im Dialog „Calibration Assistant" an und drücke erneut „Slew".

<figure markdown="span">
  ![Leitfernrohr zeigt auf den Simulatorbildschirm](BWMT_scope_pointing_at_screen.jpg)
  <figcaption>Abbildung 7: Das Fernrohr zeigt ungefähr auf die linke Seite des Simulatorbildschirms.</figcaption>
</figure>

Überprüfe deinen Montierungstreiber, denn PHD2 hat die siderische Nachführung aktiviert. **Deaktiviere die Nachführung**, falls sie aktiviert ist. Klicke dann auf „Cancel" im Kalibrierungsassistenten. Starte das Looping in PHD2 und fokussiere dein Leitfernrohr auf den Bildschirm. Da es nicht auf Unendlich zeigt, musst du möglicherweise Verlängerungsringe hinzufügen, um die Fokusposition zu erreichen.

<figure markdown="span">
  ![Verlängerungen werden fast sicher notwendig sein, um zu fokussieren](BWMT_extensions.jpg)
  <figcaption>Abbildung 8: Du wirst fast sicher Verlängerungen hinzufügen müssen, um in den Fokus zu kommen (Das Fernrohr ist ein 70/420 mit einem x0,5-Reducer).</figcaption>
</figure>

<figure markdown="span">
  ![Fokus erreicht](BWMT_focus_achieved.png)
  <figcaption>Abbildung 9: Fokus auf dem Simulatorbildschirm erreicht, aus PHD2 heraus.</figcaption>
</figure>

Aktiviere in PHD2 die Bullseye-Überlagerung über „View" > „Bullseye". Verwende **nur RA-Bewegungen** mit den Montierungssteuerknöpfen in deinem Montierungstreiber und folge den Pfeilen, um die Montierung auf die linke Seite des Bildschirms zu zeigen. Sobald du dort bist, hast du den ersten Schritt gemeistert.

!!! tip "Südhalbkugel"
    Die Lokalisierungspfeile zeigen auf die **rechte Seite** des Bildschirms. Folge ihnen, um die Montierung dort zu positionieren.

<figure markdown="span">
  ![Linke Seite des Bildschirms, in idealer Höhe](BWMT_ideal_height.png)‚
  <figcaption>Abbildung 10: Linke Seite des Bildschirms, in idealer Höhe.</figcaption>
</figure>

Drücke `next`, um zum Ausrichtungsbildschirm zu wechseln.

## Montierung und Bildschirm ausrichten

Für den nächsten Schritt musst du im „Align"-Bildschirm sein:

<figure markdown="span">
  ![BWMTs Anzeige zur Ausrichtung zeigt horizontale Linien. In der Mitte des Bildschirms ist eine rote 'Null'-Linie. Parallel dazu werden horizontale Linien in einem Abstand von 50 Pixeln angezeigt.](BWMT_align.png)
  <figcaption>Abbildung 11: Simulatorbildschirm-Anzeige zur Ausrichtung</figcaption>
</figure>

### Höhe von Bildschirm und Montierung anpassen

Jetzt, wo du auf die linke Seite des Bildschirms zeigst, passe die Höhe von Montierung und Bildschirm so an, dass das Leitfernrohr — das nach dem Schwenken (ausgeführt mit „Drift Align" oben) fast waagerecht ist — auf die Mitte des Bildschirms zeigt, angezeigt durch die rote Linie und die Anzeige „Null" auf rechter und linker Seite.

Passe dazu zunächst grob die Höhe deiner Montierung an, dann verwende die Höhenverstellung des Bildschirms, falls vorhanden. Für die Feineinstellung zuletzt die Montierungssteuerknöpfe in deiner Montierungstreiber-Software verwenden.

<figure markdown="span">
  ![Höhe wurde angepasst](BWMT_left-hand-side.png)
  <figcaption>Abbildung 12: Höhe wurde angepasst und das Leitfernrohr zeigt auf die Mitte des Ausrichtungsbildschirms (linke Seite).
  </figcaption>
</figure>

## BWMT genau südlich der Montierung positionieren

!!! tip "Südhalbkugel"
    Das gleiche Verfahren gilt, aber die Montierung bewegt sich von **rechts nach links** statt von links nach rechts, und Nord und Süd sind vertauscht (der Simulator wird genau **nördlich** der Montierung aufgestellt). Beginne von der **rechten Seite** des Bildschirms, überall wo die folgenden Anweisungen „linke Seite" sagen, und umgekehrt.

Jetzt werden wir die Montierung mehrfach in RA hin- und herbewegen, um den Bildschirm genau südlich der Montierung zu positionieren.

Wenn während des folgenden Verfahrens die Schärfe des Bildes auf der linken und rechten Seite extrem unterschiedlich ist, richte den Bildschirm so aus, dass er senkrecht zu deinem Leitfernrohr steht. Der beste Ort zum Anpassen des Fokus ist bei 25% oder 75% des Bildschirms von links nach rechts; auf dem „Configure"-Bildschirm gibt es vertikale Linien, um diese Position zu finden.

Wenn deine Montierung zwischendurch einen Meridianwechsel durchführt, überprüfe die Meridianwechsel-Einstellungen deiner Montierung und passe diese so an, dass ein Meridianwechsel vermieden wird und den Aufbau von BWMT nicht stört. Starte dann das Verfahren nach diesen Anpassungen neu.

### Ausrichtungsverfahren

Finde zunächst mit den Montierungssteuerungen in deinem Montierungstreiber die linke Seite des Monitors im Bild des Leitfernrohrs (Wenn du dem Handbuch bisher gefolgt bist, solltest du bereits dort sein). Der Simulatorbildschirm zeigt horizontale Linien und eine Pixelskala auf jeder Seite des Bildschirms an.

!!! tip "Südhalbkugel"
    Beginne von der **rechten Seite** des Bildschirms (du solltest bereits dort aus dem vorherigen Schritt sein).

Zentriere mithilfe des von PHD2 angezeigten Bullseyes die Nulllinie im Bullseye (zunächst muss das nicht pixelgenau sein) mit der Montierungssteuerung deines Treibers.

Finde dann **NUR** mit der RA-Achse die rechte Seite des Bildschirms im Bild des Leitfernrohrs. Wenn du den Bildschirm oben oder unten verlässt, halte dort an und passe die Achse deiner Montierung an, um auf den Bildschirm zu zeigen. Sobald du die rechte Seite erreichst, wirst du feststellen, dass dort sehr wahrscheinlich eine andere Linie angezeigt wird. Verwende die Azimutschrauben deiner Montierung, um sie so zu drehen, dass die Montierung auf beiden Seiten des Bildschirms die gleiche horizontale Linie trifft. Ein paar Pixel Unterschied von links nach rechts ist in Ordnung.

!!! tip "Südhalbkugel"
    Bewege dich nach **links** über den Bildschirm (RA-Richtung ist umgekehrt). Passe die Azimutschrauben so an, dass die Montierung die gleiche horizontale Linie auf beiden Seiten trifft.

<figure markdown="span">
  a)
  ![BWMT Montierung ausgerichtet linke Seite](BWMT_left-hand-side.png){width="40%"}
  b)
  ![BWMT rechte Seite](BWMT_right-hand-side.png){width="40%"}
  <figcaption>Abbildung 13: Ausrichtung von Bildschirm und Leitfernrohr erreicht: Das Bullseye kreuzt die Mittellinie des Bildschirms auf a) der linken Seite und b) der rechten Seite.</figcaption>
</figure>

Wiederhole dieses Verfahren, bis du zufrieden bist, dass beim vollständigen Bewegen von links nach rechts ein symmetrischer Bogen auf dem Monitor gezeichnet wird.

Bewege die Montierung zur linken Seite des Simulatorbildschirms und drücke `next`.

!!! tip "Südhalbkugel"
    Bewege die Montierung zur **rechten Seite** des Bildschirms, bevor du `next` drückst.

## Den Simulator kalibrieren

Du solltest jetzt im „Calibrate"-Tab sein.

<figure markdown="span">
  ![BWMT Kalibrierungsbildschirm](BWMT_web_calibration.png)
  <figcaption>Abbildung 14: Der Kalibrierungsbildschirm</figcaption>
</figure>

Jetzt werden wir die Position der Montierung über den Bildschirm verfolgen, um den durchschnittlichen Weg einzurichten, den die Montierung über den Bildschirm nimmt. Das beinhaltet:

1. Das Bild des Leitfernrohrs in PHD2 ansehen und BWMT mitteilen, wohin das Fernrohr schaut
2. Das Fernrohr in RA um einige Pixel bewegen
3. 1 und 2 wiederholen, bis der gesamte Bildschirm überquert wurde.

**Schritt 1**: BWMT zeigt auf der Webseite ein verkleinertes Bild des Bildschirms an ("Calibration Preview"). Beim Bewegen der Maus wird ein Kreuz auf dem Simulatorbildschirm an der Position der Maus angezeigt. Das PHD2-Leitfernrohrbild betrachtend, bewege die Maus so, dass das Kreuz in der Mitte des Bullseyes angezeigt wird, das PHD2 auf das Bild überlagert. Rechtsklick, um den ersten Ausrichtungspunkt zu setzen. Mit den Pfeiltasten den Fadenkreuz auf das Zentrum des Bullseyes ausrichten. Die Tasten funktionieren nur, wenn der Cursor über dem Bild schwebt.

<figure markdown="span">
  a) Das Schweben über der Webseite zeigt ein Fadenkreuz sowohl in der Kalibrierungs-Vorschau (rechts) als auch auf dem Simulatorbildschirm (PHD2-Bild, links)
  ![Schritt 1a: Schweben und Fadenkreuz zeigen](BWMT_calibration_step1a.png)

  b) Linksklick mit der Maus erstellt einen Kalibrierungspunkt (hier 15).
  ![Schritt 1b: Klicken, um einen Kalibrierungspunkt zu setzen](BWMT_calibration_step1b.png)

  c) Position feinjustieren, um das Fadenkreuz mit Pfeiltasten oder s, d, f und e im Bullseye zu zentrieren.
  ![Schritt 1c: Mit Pfeiltasten den Kalibrierungspunkt im Zentrum des Bullseyes platzieren](BWMT_calibration_step1c.png)
  <figcaption>Abbildung 15: Schritte zum Erstellen eines Kalibrierungspunkts.
</figure>

**Schritt 2**: Bewege die Montierung **NUR** mit der RA-Achse nach rechts, so dass du den vorherigen Ausrichtungspunkt noch sehen kannst. Wiederhole dann Schritt 1.

!!! tip "Südhalbkugel"
    Bewege die Montierung stattdessen nach **links**, und verfolge von rechts nach links über den Bildschirm. In der Kalibrierungs-Vorschau ist Punkt #1 auf der rechten Seite und die Punkte zählen nach links hoch.

<figure markdown="span">
  ![Schritt 2: Montierung bewegen, um den nächsten Kalibrierungspunkt hinzuzufügen](BWMT_calibration_step2.png)
  <figcaption>Abbildung 16: Montierung bewegen, um den nächsten Kalibrierungspunkt zu erstellen.</figcaption>
</figure>

**Schritte 3 .. N**: Wiederhole Schritte 1 und 2, bis du Ausrichtungspunkte hast, die den gesamten Abstand auf dem Bildschirm von links nach rechts abdecken.

BWMT zeigt eine Ellipsenanpassung unterhalb des Bildschirms im Webbrowser an. Diese wird im nächsten Schritt verwendet, um einen Stern zu simulieren, der den Bildschirm überquert.

<figure markdown="span">
  ![Alle Kalibrierungspunkte gesetzt](BWMT_calibration_complete.png)
  <figcaption>Abbildung 17: Kalibrierungsschritte wiederholen, um den gesamten Simulatorbildschirm abzudecken. Damit ist die Kalibrierung abgeschlossen.</figcaption>
</figure>

Bewege zuletzt die Montierung zur linken Seite des Bildschirms, dann drücke `next`, um mit der Messung der Geschwindigkeit deiner Montierung zu beginnen.

!!! tip "Südhalbkugel"
    Bewege die Montierung zur **rechten Seite** des Bildschirms, bevor du `next` drückst.

## Bildschirmgeschwindigkeit messen

!!! info "Warum die gemessene Geschwindigkeit von der siderischen Rate abweichen kann"
    Du kennst wahrscheinlich siderische, lunare und solare Nachführgeschwindigkeiten. Diese Geschwindigkeiten gelten für den Fall, dass das Teleskop direkt am Schnittpunkt von Kegelschnitten montiert ist.

Die nächste Simulatoranzeige zeigt drei Bereiche, an denen wir die Geschwindigkeit der Montierung messen werden. Jeder Bereich besteht aus einem vertikalen Streifen, einen links, einen in der Mitte und einen rechts. Die Breite der Streifen ist so gewählt, dass die Montierung ungefähr 3 Minuten benötigt, um ihn zu überqueren.

<figure markdown="span">
  ![Zur Geschwindigkeitsmessung werden drei Streifen angezeigt](BWMT_velocity.png)
  <figcaption>Abbildung 18: 3 Streifen zur Geschwindigkeitsmessung, einer links, einer in der Mitte und einer rechts.</figcaption>
</figure>

Die Webseite zeigt drei „aufgezeichnete Zeiten", eine für jeden Streifen und eine Stoppuhr oben. Durch Klicken auf „Left", „Middle" oder „Right" in der Stoppuhr wird die aufgezeichnete Zeit für diesen Streifen ausgewählt.

<figure markdown="span">
  ![Zur Geschwindigkeitsmessung erlaubt die Webseite das Stoppen der Zeit zum Überqueren der Streifen](BWMT_web_velocity.png)
  <figcaption>Abbildung 19: Die Webseite zur Messung der Bildschirmgeschwindigkeiten. Wähle den jeweiligen Streifen durch Klicken auf „Left", „Middle" oder „Right", dann verwende die Start/Stop- und Reset-Schaltflächen, um zu messen, wie lange die Montierung benötigt, um den Streifen zu überqueren.
  </figcaption>
</figure>

!!! important "Fokus prüfen! Nochmal!"
    Es ist sehr wichtig, dass du die Geschwindigkeit korrekt misst. Vermeide daher — wenn möglich — die Verwendung von Fernzugriffssoftware wie Remote Desktop Client oder VNC für den Zugriff auf deinen Astro-Computer. Stelle außerdem sicher, dass das Leitfernrohr **genau fokussiert** auf den Simulatorbildschirm ist.

Wähle eine sehr kurze Belichtungszeit für deine Kamera. Der kleinste Wert, den PHD2 unterstützt, ist 0,01 s. Vermeide Sättigung und fokussiere korrekt auf den Simulatorbildschirm.

Bewege jetzt die Montierung nach links des äußeren Streifens, starte die Nachführung mit aktiver Bullseye-Überlagerung auf dem Bildschirm und drücke „Start", sobald das Bullseye-Zentrum in den linken Streifen eintritt. Achte darauf, Reflexionen des Streifens auf dem Bildschirmgehäuse zu vermeiden. Drücke Stop, wenn es den Streifen verlässt. Die Zeit, die zum Überqueren des Streifens benötigt wurde, wird auf der Webseite angezeigt. Bewege dann **NUR** mit RA-Bewegungen zum mittleren Streifen und messe dort. Wiederhole dann dieses Verfahren mit dem rechten Streifen.

!!! tip "Südhalbkugel"
    Beginne rechts vom rechten Streifen und messe in der Reihenfolge **rechts → Mitte → links**, in der Richtung, in die die Montierung natürlich wandert. Die Weboberfläche wechselt die Stoppuhr-Auswahl automatisch in dieser Reihenfolge, wenn der Südhalbkugel-Modus aktiv ist.

<figure markdown="span">
  ![Während einer Geschwindigkeitsmessung](BWMT_velocity_running.png)
  <figcaption>Abbildung 20: Während die Messung für den linken Streifen läuft. Beachte, dass die Montierung nachführt (Tracking „ein").</figcaption>
</figure>

Wenn du einen Streifen neu messen möchtest, klicke auf die Löschen-Schaltfläche neben dem entsprechenden Eingabefeld. Das Starten und Stoppen der Stoppuhr legt die Messung dann in dieses Feld.

Nach dem Messen der Montierungsgeschwindigkeit an jedem Ort, drücke `next`; du befindest dich jetzt im „Measure"-Tab der Weboberfläche und die Simulationssteuerung wird angezeigt.

## Qualifizierung des Messaufbaus

Für das Folgende musst du im „Measure"-Tab der Weboberfläche sein, wo die Simulationssteuerung angezeigt wird:

<figure markdown="span">
  ![BWMT Simulationssteuerung](BWMT_web_measure.png)
  <figcaption>Abbildung 21: Die Simulationssteuerung.</figcaption>
</figure>

### Voraussetzungen für gute Messungen

#### Passende Belichtungszeit

Die PHD2-Mailingliste empfiehlt eine Belichtungszeit von 1 - 3 s bei Schneckengetriebe-Montierungen und 0,5 - 1 s für Strain-Wave-Getriebe-Montierungen. Wähle eine passende Belichtungszeit. Wahrscheinlich musst du einen Graufilter vor deine Kamera oder vor dein Leitfernrohr setzen, um Sättigung zu vermeiden.

#### Gutes Sternprofil erzielen (Pixel mitteln)

Da wir die Pixel vom Simulatorbildschirm abbilden, müssen wir sicherstellen, dass die Kamera diese Pixelstruktur nicht aufnimmt, sondern sie zumindest herausmittelt.

Nimm zum Beispiel diese fokussierte Ansicht der „LEFT"-Beschriftung entlang des Streifens aus dem Geschwindigkeitsmessungsschritt:

<figure markdown="span">
  ![Fokussiertes Sternprofil, das die Pixelstruktur des Simulatorbildschirms zeigt](BWMT_pixelstructure.png)
  <figcaption>Abbildung 22: PHD2's Star Profile-Tool zeigt Pixel.</figcaption>
</figure>

Wie du sehen kannst, ist das Sternprofil unregelmäßig und besteht nicht aus einem einzelnen symmetrischen „Buckel". Dies ist dann auch beim simulierten Stern der Fall, aber nicht so ausgeprägt:

<figure markdown="span">
  a)
  ![Fokussiertes Sternprofil, das die Pixelstruktur des Simulatorbildschirms zeigt](BWMT_pixelstructure_star.png)
  b)
  ![Unfokussiertes Sternprofil, das eine symmetrische Struktur zeigt](BWMT_pixelstructure_unfocused.png)
  <figcaption>Abbildung 23: PHD2's Star Profile-Tool zeigt Pixel in a), und ein symmetrischeres Profil wenn unfokussiert in b).
  </figcaption>
</figure>

Um das Sternprofil für Messungen zu verbessern, kannst du Folgendes tun:

- Abstand zwischen Montierung und Simulatorbildschirm erhöhen. Verringert Bogensekunden / px für den Simulatorbildschirm.
- Die Brennweite deines Leitfernrohrs verringern. Verringert Bogensekunden / px für das Leitfernrohrbild.
- Eine andere Leitkamera mit größeren Pixeln verwenden
- Einen anderen Bildschirm mit besserer Auflösung (höherer dpi) verwenden
- **Das Leitfernrohr defokussieren. Verwischt die Pixelstruktur künstlich.**

#### Erschütterungsfreier Boden

In meinem Fall führe ich Messungen in einem alten Gebäude mit Holzböden durch, so dass Personen, die neben der Montierung oder neben dem Simulatorbildschirm gehen, Ausschläge von mehr als 20" erzeugen können, d. h. das Bild des simulierten Sterns ändert seine Position um ungefähr 6 Pixel oder eine Distanz von 21 µm. Das ist etwa 1/3 eines Menschenhaares.

Es kann sogar sein, dass Personen, die Türen zuschlagen oder anderweitig Energie oder Vibrationen in das Haus einbringen (wie das Hüpfen eines Balls), von deinem Messaufbau wahrgenommen werden.

Wenn du die Wahl hast, stelle sicher, dass der Boden, auf dem deine Montierung steht, und alle Möbel, auf denen der Simulatorbildschirm steht, extrem stabil sind. Stelle zumindest (wenn möglich) sicher, dass solche Dinge während deiner Messungen nicht passieren (Personen, die herumlaufen oder Bälle hüpfen).

#### Belichtungszeit und Bildschirm-Aktualisierung

BWMT ist so konfiguriert, dass der Bildschirm alle 1/60 Sekunde oder gleichwertig alle 0,017 Sekunden aktualisiert wird. Die Belichtungszeit der Leitkamera sollte daher von dieser Rate abweichen.

### Den statistischen Fehler messen

Beim Betreten des „Measure"-Tabs zeigt BWMT auf der linken Seite (Nordhalbkugel, rechte Seite auf der Südhalbkugel), wo du den ersten Ausrichtungspunkt gesetzt hast, einen simulierten Stern an. Dieser Stern hat ein gaussförmiges Profil, das an den Positionen der Pixel abgetastet wird. Der Durchmesser dieses Sterns beträgt ungefähr 3 Pixel.

!!! warning "Den Stern defokussieren"
    Um ein schönes Sternprofil zu erhalten, musst du absichtlich defokussieren. **Defokussiere um einen großen Betrag.** Wenn du zum „Calibrate"-Tab zurückwechselst, solltest du die Nummern der Kalibrierungspunkte nicht mehr lesen können!

!!! warning "Ziел-Belichtungszeit verwenden"
    Wenn du eine Leitfernrohr-Belichtungszeit von 1 s anstrebst, solltest du die Messung auch bei 1 s durchführen. Um dies zu erreichen, musst du möglicherweise Graufilter verwenden. Stelle sicher, dass der Spitzenwert des simulierten Sternprofils mindestens 50% des Maximums deines Sensors erreicht (siehe „Saturation by Max-ADU value" im „Camera"-Tab in PHD2's erweiterten Einstellungen).

Schauen wir uns an, welche statistischen Schwankungen der Messaufbau meldet. Diese können sein: Luftströmungen, Kabelzug, Ungleichgewichte in RA und Dec, Vibrationen im Gebäude von vorbeifahrenden Personen oder Autos, die höhere Temperatur der Montierung und ihrer Schmiermittel (Vergleich Innen- zu Außentemperaturen), Schwankungen durch Spiel (in Dec) usw.

Um dies zu messen, erzeugen wir eine Situation, in der sich nichts ändern sollte: Wir deaktivieren alle Motoren und alle Bewegungen des simulierten Sterns. Deaktiviere also die Nachführung im Montierungstreiber und stelle sicher, dass die Simulation in BWMTs „Measure"-Weboberfläche gestoppt ist.

Starte das Looping in PHD2, falls es nicht bereits läuft. Bewege dann die Montierung **nur in RA**, um den simulierten Stern anzuzeigen, klicke auf den simulierten Stern, um ihn für die Nachführung auszuwählen, und dann &lt;SHIFT&gt;-klicke oder klicke auf das Symbol „Start Guiding" in PHD2.

!!! tip "Kalibrierung erzwingen"
    Mit Shift-Klick kannst du eine Kalibrierung erzwingen. Da wir oben ein neues Profil erstellt haben, sollte jetzt eine neue Kalibrierung erstellt werden. Du solltest eine neue Kalibrierung erzwingen, wenn du eine alte aktiv hast (PHD2 verwendet normalerweise eine gute Kalibrierung wieder), **aber du den optischen Aufbau geändert hast**, z. B. durch Hinzufügen eines Graufilters, um in den richtigen Belichtungsbereich zu kommen.

Lass es eine Weile laufen. Verwende jetzt den PHD2 Log Viewer, um einen Blick auf das Log zu werfen.

<figure markdown="span">
  ![BWMT ](BWMT_statistical_error.png)
  <figcaption>Abbildung 24: Nachführung während „nichts bewegt sich". Abstand zwischen grauen Linien ist 1".</figcaption>
</figure>

Was du daraus entnehmen kannst:

- Selbst wenn „nichts bewegt sich", erkennt PHD2 unterschiedliche Positionen des simulierten Leitsterns
- Die Bewegung sieht wie ein Random Walk aus
- Das Streudiagramm des ausgewählten Abschnitts ist weitgehend symmetrisch
- Es gab eine große Abweichung durch Personen, die im Raum gingen (abgewählt)
- RA RMS wird als 0,09 px gemeldet, das bedeutet, dass das Mitteln Messungen ergibt, die bis zu 1/10 eines Leitkamerapixels „gut" sind.
- Dec RMS ist mit 0,12 px etwas größer
- Drift liegt in der Größenordnung der Hälfte davon (wo es keine Drift geben sollte)
- Polausrichtungsfehler wird als 1,4' gemeldet

Bei gleicher Leitkamera und gleichem Leitfernrohr und ähnlicher Last auf der Montierung wird es schwer sein, bessere Werte als diese zu erreichen.

Wiederhole diese Messung an Position 25%, 50%, 75% und 100%. Dazu kannst du auf den Fortschrittsbalken in der Webanwendung klicken und die Schaltflächen „Schnell zurück" und „Schnell vor" verwenden. Wenn du die Position der Leitkamera verloren hast, drücke `back`, um die Ausrichtungspunkte anzuzeigen und dein Leitfernrohr zu positionieren und den simulierten Stern zu finden.

Alle diese Messungen sollten übereinstimmen und ähnliche Werte für RMS RA liefern.

Wenn die Werte inkonsistent sind und stark voneinander abweichen:

- Orientierung von Leitfernrohr und Simulatorbildschirm prüfen
- Eine andere Fokuseinstellung des Leitfernrohrs prüfen
- Auf Kabelzug prüfen und
- Ungleichgewichte in RA und Dec prüfen

## Eine Führungssequenz messen

### Wie die Simulationsgeschwindigkeit bestimmt wird

Wenn du den „Measure"-Tab betrittst, berechnet BWMT die Geschwindigkeit, mit der sich der simulierte Stern über den Bildschirm bewegt. Die Berechnung hängt davon ab, wie viele der drei Streifen im vorherigen Schritt gemessen wurden.

#### Theoretische Basis

Unabhängig von Messungen berechnet BWMT zunächst eine theoretische Geschwindigkeit aus der Geometrie deines Aufbaus:

```
pixel_pitch_arcsec = (screen_width_mm / screen_width_px / distance_m / 1000) × 206265
theoretical_velocity = 15 Bogensek./s / pixel_pitch_arcsec × cos(90° − Breite)
```

Der Faktor `cos(90° − Breite)` berücksichtigt, dass Sterne umso langsamer über den Himmel ziehen, je weiter du vom Äquator entfernt bist (mit zunehmendem absoluten Dec-Wert), und du bist in den meisten Fällen ziemlich weit davon entfernt, weil du auf den Simulatorbildschirm zeigst.

#### Geschwindigkeitsquelle

Abhängig davon, wie viele Streifen in Schritt 4 gemessen wurden, gilt einer von drei Fällen:

| Gemessene Streifen | Bezeichnung der Geschwindigkeitsquelle | Wie die Geschwindigkeit bestimmt wird |
|--------------------|----------------------------------------|---------------------------------------|
| 0                  | *geschätzt*                            | Theoretischer Wert aus Schritt 1 (konstant über den Bildschirm) |
| 1 oder 2           | *Teildurchschnitt*                     | Durchschnitt der gemessenen Streifengeschwindigkeiten (konstant über den Bildschirm) |
| 3                  | *interpoliert*                         | Quadratisches Polynom durch alle drei gemessenen Punkte; Geschwindigkeit variiert über den Bildschirm |

Die aktive Quelle wird im **Simulation Control**-Karte neben der aktuellen Geschwindigkeitsanzeige angezeigt. Wenn die Quelle *geschätzt* ist, wird sowohl in der Weboberfläche als auch auf dem Simulatorbildschirm eine Warnung angezeigt.

**Fall „geschätzt" — keine Messungen**

Die theoretische Geschwindigkeit wird unverändert verwendet. Dies ist die am wenigsten genaue Option: Sie nimmt an, dass die Montierung genau mit siderischer Rate nachführt, und ignoriert jeglichen mechanischen Versatz des Teleskops von der RA-Achse oder andere geometrische Effekte, die dazu führen, dass die scheinbare Bildschirmgeschwindigkeit von der reinen siderischen Rate abweicht.

**Fall „Teildurchschnitt" — 1 oder 2 Streifen gemessen**

Der Durchschnitt der verfügbaren gemessenen Streifengeschwindigkeiten wird als konstante Geschwindigkeit verwendet. Dies ist genauer als die theoretische Schätzung, aber da nur ein Teil des Bildschirms gemessen wurde, werden positionsabhängige Geschwindigkeitsvariationen nicht erfasst.

**Fall „interpoliert" — alle 3 Streifen gemessen**

Ein quadratisches Polynom wird durch die drei gemessenen `(Bildschirm_x, Geschwindigkeit)`-Paare an den linken, mittleren und rechten Streifenzentren angepasst. Während der Simulation wird die Geschwindigkeit des Sterns aus dieser Kurve an jeder x-Position nachgeschlagen, so dass er über den Bildschirm natürlich beschleunigt oder abbremst, um das echte Nachführverhalten der Montierung zu entsprechen. Die konstante Geschwindigkeit, die für die Dauer-Schätzung verwendet wird, ist das Maximum der drei gemessenen Werte.

### Führungsassistent-Lauf

Zuerst müssen wir PHD2 seine Nachführparameter mithilfe des Führungsassistenten optimieren lassen, dann können wir Messungen durchführen.

Starten wir jetzt den Führungsassistenten von PHD2. Dieser schaltet die Nachführung aus und verfolgt nur die Bewegung der Sterne und zeichnet direkt die Position des Leitsterns auf der Kamera auf.

Gehe dafür wie folgt vor:

- Bewege dich nach links des simulierten Sterns und aktiviere die Nachführung in der Montierung.

!!! tip "Südhalbkugel"
    Bewege dich stattdessen nach **rechts** des simulierten Sterns, damit die Montierung ihn nach links in den Bildausschnitt nachführt.

- Wenn das Leitkamerabild den Stern ungefähr in der Mitte hat, starte die Simulation in BWMTs Weboberfläche.
- Öffne PHD2's „Tools" > „Guiding Assistant", wähle den simulierten Stern, wenn er noch nicht ausgewählt ist, und starte die Nachführung.
- Lass „Measure Declination Backlash" aktiviert, dann drücke „Start".
- Lass es für mindestens eine vollständige Umdrehung des Schneckenrades laufen (sieh dir die „elapsed time" in der oberen rechten Tabelle an).
- Vergleiche diese Zeit mit der verbleibenden Simulationszeit, die auf dem Simulatorbildschirm angezeigt wird.
- Warte
- Drücke „Stop" im Führungsassistenten.
- Akzeptiere alle Änderungen, die der Führungsassistent empfiehlt.

!!! bug "Simulatorgeschwindigkeit ist systematisch zu hoch"
    Die Geschwindigkeit, mit der der Simulator den Bildschirm überquert, ist systematisch zu hoch.
    Der Grund dafür ist momentan unbekannt. Jede Hilfe ist willkommen.
    Falls nichts anderes hilft, wird eine zukünftige Version einen Regler enthalten, um die Geschwindigkeit nach oben oder unten anzupassen.

### Messung: Führungssequenz

!!! warning "Das Setup während der Messung nicht stören"
    Während der Messung vermeide es, die Sichtlinie zu kreuzen und um Montierung und Bildschirm herumzugehen! Sonst könnte PHD2 den simulierten Leitstern verlieren und die Nachführung stoppen.

    Gehe auch nicht neben der Montierung oder dem Simulatorbildschirm umher, da abhängig vom Boden, auf dem du misst, dein Gewicht Vibrationen oder Änderungen des Bodens erzeugen könnte, die zur Montierung oder zum Bildschirm übertragen werden und Ausschläge erzeugen.

Setze die Simulation durch Klicken auf die Schaltfläche „Zurück zum Anfang" auf 0% zurück und drehe das Leitfernrohr zurück, um auf den simulierten Stern zu zeigen.

Jetzt ist es Zeit, die Simulation zu starten:

1. Starte die Nachführung in der Montierung mit den Treibersteuerungen
2. Starte die Simulation durch Klicken auf die Play-Schaltfläche auf der Webseite.
3. Starte die Nachführung in PHD2
4. Sobald die Simulation zu Ende geht, stoppe zuerst die Nachführung in PHD2.
5. Stoppe die Nachführung der Montierung

BWMT zeigt jetzt die verbleibende Zeit an, die die Montierung benötigt, um den Bildschirm zu überqueren. Eine Minute und dann wieder 30 Sekunden vor dem Ende piept BWMT; der an den Simulator angeschlossene Bildschirm hat einen Lautsprecher. 10 Sekunden vor dem Ende der Simulation beginnt ein Countdown und BWMT piept 10 Mal. Nutze dies, um die Montierung zu stoppen.

Mithilfe des **PHD2 Log Viewers** kannst du jetzt die Leistung deiner Montierung analysieren.

## Geometrie-Visualisierungswerkzeug

Der `geometry`-Befehl (oder `bwmt -g`) öffnet eine 3D-Visualisierung, wie die Sichtlinie des Leitfernrohrs über den Simulatorbildschirm verläuft, wenn sich die Montierung in RA dreht. Es ist als Planungs- und Diagnosewerkzeug gedacht — nicht für den normalen Betrieb erforderlich.

### Geometrie aufrufen

```
bwmt -g                          # verwendet setup.yml im aktuellen Verzeichnis
bwmt -g --lat 48 --distance 5   # spezifische Werte überschreiben
geometry -c /path/to/setup.yml  # den dedizierten Einstiegspunkt aufrufen
```

### Konfigurationsparameter

Das Geometriewerkzeug liest fünf zusätzliche Parameter aus `setup.yml` unter dem Schlüssel `mount:`. Sie können auch über die **Mount Geometry**-Karte in der Web-UI (Configure-Schritt) gesetzt werden.

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `telescope_offset_m` | `0.27` | Abstand des Leitfernrohrs von der RA-Achse (m) |
| `telescope_offset_dec_m` | `-0.015` | Versatz von der Dec-Achse; negativ = Richtung Boden (m) |
| `angle_start_deg` | `0.0` | Anfang des RA-Schwenks (°) |
| `angle_stop_deg` | `-10.0` | Ende des RA-Schwenks (°) |
| `declination_deg` | *(keiner)* | Sichtlinien-Deklination; weglassen für äquatoriale Ausrichtung |

### Ausgabe-Diagramme

Das Werkzeug öffnet drei Abbildungen:

**Abbildung 1 – 3D-Ansicht**
Zeigt die RA-Rotationsachse (grün), den Teleskoppositionskreis (rote Punkte für alle 5°) und die vom `angle_start_deg` bis `angle_stop_deg` verfolgten Sichtlinien. Das blaue Rechteck ist der Simulatorbildschirm.

**Abbildung 2 – Bildschirmspuren und Geschwindigkeit**
Drei überlagerte Diagramme:
- *Bildschirmschnitt* – der Weg, den der Leitstern auf dem Bildschirm zurücklegt (mm).
- *Gesamtgeschwindigkeit* – Geschwindigkeit des Sterns entlang des Weges (mm/s) vs. Fortschritt (%).
  Die grüne gestrichelte Linie ist die siderische Referenzgeschwindigkeit bei dem gegebenen Abstand.
- *X-Geschwindigkeit* – horizontale Komponente der Geschwindigkeit (px/s), der für die PHD2-Konfiguration relevanteste Wert.

**Abbildung 3 – Geometrie-Zusammenfassungstabelle**
Eine kompakte Tabelle aller Eingabeparameter und berechneten Ergebnisse: X/Y-Spanne auf dem Bildschirm, Min-/Durchschnitts-/Maximalgeschwindigkeit (mm/s und px/s), Pixelabstand und siderische Referenz.

### Typischer Arbeitsablauf

1. Abstand, Breite und Bildschirmabmessungen in der BWMT-Hauptweboberfläche einstellen.
2. Den Teleskopversatz von der RA- und Dec-Achse mit einem Lineal messen.
3. Die Werte in der **Mount Geometry**-Karte (oder `setup.yml`) eingeben.
4. `bwmt -g` ausführen und Abbildung 2 prüfen, um zu verifizieren, dass das Geschwindigkeitsprofil über den Bildschirm akzeptabel gleichmäßig ist.
5. Die X-Geschwindigkeit aus Abbildung 3 mit der gemessenen Bildschirmgeschwindigkeit aus Schritt 4 des Hauptworkflows abgleichen.
