# Bad Weather Mount Tester Referenz

Diese Referenz beschreibt jede Simulatoranzeige und jedes Element der Weboberfläche für jeden der fünf Tabs in BWMTs Weboberfläche.

Schritt-für-Schritt-Anleitungen zur Verwendung dieser Bildschirme in der richtigen Reihenfolge findest du im [Handbuch](manual.md).

---

## Configure-Tab

Der Configure-Tab ist der erste Schritt. Hier gibst du alle Informationen über deine Montierung, Leitkamera und den
Simulatorbildschirm ein, damit BWMT die korrekten Parameter für PHD2 berechnen kann.

Das schrittweise Einrichtungsverfahren findest du unter [BWMT und die Ausrüstung
konfigurieren](manual.md#bwmt-und-die-ausrustung-konfigurieren) im Handbuch.

### Simulatoranzeige

<figure markdown="span">
  ![BWMT Suchbildschirm mit Pfeilmustern auf schwarzem Hintergrund](BWMT_configure.png)
  <figcaption>Die Simulatoranzeige des Configure-Tabs: ein Suchbildschirm mit Richtungspfeilen.</figcaption>
</figure>

Wenn der Webbrowser eine Verbindung zu BWMT herstellt, wechselt der Simulator vom Wartebildschirm zum
**Suchbildschirm**. Der Suchbildschirm zeigt Richtungspfeile auf schwarzem Hintergrund. Die Pfeile führen dich dazu, das
Leitfernrohr in die richtige Richtung auf dem Simulatorbildschirm zu bewegen:

- **Große Pfeile** zeigen von allen Richtungen zur Bildschirmmitte und helfen dir, vom aktuellen Standpunkt des Leitfernrohrs aus zu navigieren.
- **Kleines rotes Kreuz** markiert die linke Seite des Bildschirms (Nordhalbkugel) oder die rechte Seite (Südhalbkugel)
  – die Startposition für den Ausrichtungsschritt.
- **Vertikale Linien bei 25 % und 75 %** der Bildschirmbreite werden im Configure-Modus angezeigt, um die besten
  Positionen zur Überprüfung der Fokusgleichmäßigkeit über den Bildschirm zu markieren.

### Weboberfläche

<figure markdown="span">
  ![BWMT Konfigurations-Webseite](BWMT_web_configure.png)
  <figcaption>Die Weboberfläche des Configure-Tabs mit allen Eingabekarten.</figcaption>
</figure>

Die Weboberfläche des Configure-Tabs ist in mehrere Karten unterteilt.

#### Montierungskonfiguration

| Feld | Einheit | Beschreibung |
|---|---|---|
| **Breite** | Grad (Dezimal) | Die Breite, auf die deine Montierung eingestellt ist. Umrechnung von Sexagesimalgrad (dd° mm'): `dd + mm / 60`. Sowohl `.` als auch `,` werden als Dezimaltrennzeichen akzeptiert. |
| **Brennweite des Leitfernrohrs** | mm | Die *effektive* Brennweite des Leitfernrohrs. Bei Verwendung eines Reducers multiplizieren: z. B. 420 mm × 0,5 = 210 mm. |
| **Entfernung zum Bildschirm** | m | Abstand von der Dec-Rotationsachse zum Simulatorbildschirm. Drehe die RA-Achse, bis die Dec-Achse waagerecht ist, bevor du misst. |
| **Hauptperiode der Montierung** | s | Die Zeit für eine vollständige Schneckenradumdrehung (für Schneckengetriebe-Montierungen mit siderischer Nachführung). Optional – nur informativ. |

#### Montierungsgeometrie

Diese optionalen Felder werden vom [Geometrie-Visualisierungswerkzeug](manual.md#geometrie-visualisierungswerkzeug)
verwendet und sind für normale Messungen nicht erforderlich.

| Feld | Einheit | Beschreibung |
| --- | --- | --- |
| **Teleskopversatz RA** | m | Abstand des Leitfernrohrs von der RA-Rotationsachse. |
| **Teleskopversatz Dec** | m | Versatz von der Dec-Achse; negative Werte zeigen in Richtung Boden. |
| **Schwenkstartwinkel** | ° | Startwinkel des vom Geometriewerkzeug modellierten RA-Schwenks. |
| **Schwenkendwinkel** | ° | Endwinkel des vom Geometriewerkzeug modellierten RA-Schwenks. |
| **Deklination** | ° | Sichtlinien-Deklination für das Geometriemodell. Weglassen für äquatoriale Ausrichtung. |

#### Leitkamera

| Feld | Einheit | Beschreibung |
| --- | --- | --- |
| **Pixelgröße** | µm | Physikalische Größe eines Kamerapixels. Quadratische Pixel werden angenommen. |
| **Breite** | px | Sensorbreite in Pixeln. |
| **Höhe** | px | Sensorhöhe in Pixeln. |
| **Auflösung** *(berechnet)* | Bogensek./px | Winkelauflösung der Leitkamera im Abstand zum Simulator. Wird automatisch angezeigt; nicht editierbar. |

#### Bildschirm

| Feld | Einheit | Beschreibung |
|---|---|---|
| **Bildschirmbreite** | mm | Die physikalische Breite des aktiven Anzeigebereichs, mit einem Lineal vom äußersten linken bis zum äußersten rechten Pixel gemessen. |
| **Pixelabstand** *(berechnet)* | mm/px und Bogensek./px | Physikalische Größe eines Simulatorpixels und sein Winkelmaß aus Sicht des Leitfernrohrs. Wird automatisch angezeigt. |

#### Berechnete Werte

BWMT berechnet diese Größen aus den obigen Feldern und zeigt sie schreibgeschützt an.

| Wert | Beschreibung |
|---|---|
| **Effektive Brennweite für PHD2** | Die Brennweite, die in das PHD2-Nachführprofil eingetragen werden muss. Da das Leitfernrohr auf den nahen Simulatorbildschirm statt auf Unendlich fokussiert ist, weicht die effektive Brennweite von der Nennbrennweite ab. Formel: `effective_fl = (focal_length × distance) / (distance − focal_length)`. |
| **Empfohlenes Binning** | Das optimale Kamera-Binning, damit ein gebinntes Kamerapixel denselben Winkel abdeckt wie ein Simulatorpixel. Diesen Wert in PHD2 einstellen; falls der genaue Wert nicht verfügbar ist, das nächstgelegene verfügbare Binning wählen. |
| **Messdauer** | Geschätzte Zeit (in Minuten), die die Montierung benötigt, um den gesamten Simulatorbildschirm bei siderischer Rate zu überqueren, berücksichtigt die Breite über `cos(90° − Breite)`. Dies ist ein grober Schätzwert – der genaue Wert hängt von der Position des Leitfernrohrs relativ zur RA-Achse ab. |
| **Bereich auf dem Simulator** | Breite × Höhe (in mm) des durch das Leitfernrohr sichtbaren Bereichs auf dem Simulatorbildschirm, berechnet aus der Sensorgröße und der effektiven Brennweite. |
| **Dec-Ziel** | Der Deklinationswert für den Kalibrierungsassistenten von PHD2 beim Schwenken auf den Bildschirm. Nordhalbkugel: `−(90° − Breite)`. Südhalbkugel: `+(90° − |Breite|)`. |

---

## Align-Tab

Der Align-Tab ist der zweite Schritt. Hier passt du die physikalische Höhe von Montierung und Bildschirm an, damit das
Leitfernrohr entlang der Mittellinie nachführt, und richtest den Bildschirm durch Hin- und Herbewegen in RA genau
südlich (oder nördlich) der Montierung aus.

Das schrittweise Ausrichtungsverfahren findest du unter [Montierung und Bildschirm
ausrichten](manual.md#montierung-und-bildschirm-ausrichten) im Handbuch.

### Simulatoranzeige

<figure markdown="span">
  ![Ausrichtungsbildschirm mit horizontalen Linien und einer roten Nulllinie](BWMT_align.png)
  <figcaption>Die Simulatoranzeige des Align-Tabs: horizontale Referenzlinien und Pixelskala.</figcaption>
</figure>

Die Ausrichtungs-Simulatoranzeige zeigt:

| Element | Beschreibung |
|---|---|
| **Rote Nulllinie** | Die horizontale Mitte des Bildschirms. Auf beiden Seiten wird der Text *Null* angezeigt. Richte das Leitfernrohr so aus, dass das PHD2-Bullseye diese Linie kreuzt. |
| **Parallele graue Linien** | Horizontale Referenzlinien im Abstand von 50 Pixeln ober- und unterhalb der Nulllinie, die eine Skalenreferenz für den vertikalen Versatz bieten. |
| **Pixelskalenbeschriftungen** | Zahlen am linken und rechten Rand des Bildschirms, die den Pixelversatz von der Mittellinie anzeigen, sodass du quantifizieren kannst, wie weit das Leitfernrohr von der Mitte entfernt ist. |

### Weboberfläche

Die Weboberfläche des Align-Tabs zeigt halbkugelspezifische Textanweisungen, die an das Ausrichtungsverfahren erinnern.
Es gibt keine interaktiven Steuerelemente außer den **Zurück**- und **Weiter**-Navigationsschaltflächen.

- **Nordhalbkugel**: Die Anweisungen erklären die Bewegung von links nach rechts in RA und die Verwendung der
  Azimutschrauben, um die horizontale Linie auf beiden Seiten anzupassen.
- **Südhalbkugel**: Die Anweisungen sind gespiegelt (von rechts nach links, Start von der rechten Seite).

---

## Calibrate-Tab

Der Calibrate-Tab ist der dritte Schritt. Du zeichnest den Weg auf, den die Montierung über den Simulatorbildschirm
nimmt, indem du Kalibrierungspunkte setzt. BWMT passt eine Ellipse an diese Punkte an und verwendet sie während der
Simulation.

Das schrittweise Kalibrierungsverfahren findest du unter [Den Simulator
kalibrieren](manual.md#den-simulator-kalibrieren) im Handbuch.

### Simulatoranzeige

<figure markdown="span">
  a) Das Hovern über der Webseite zeigt ein Fadenkreuz auf dem Simulatorbildschirm.
  ![Schritt 1a: Hovern zeigt Fadenkreuz auf dem Simulatorbildschirm](BWMT_calibration_step1a.png)

  b) Ein Linksklick setzt einen nummerierten Kalibrierungspunkt.
  ![Schritt 1b: Klicken setzt einen Kalibrierungspunkt auf dem Simulatorbildschirm](BWMT_calibration_step1b.png)
  <figcaption>Simulatoranzeige des Calibrate-Tabs: Das Fadenkreuz und nummerierte Kalibrierungspunkte erscheinen auf dem s
  chwarzen Bildschirm.</figcaption>
</figure>

Die Kalibrierungs-Simulatoranzeige zeigt:

| Element | Beschreibung |
| --- | --- |
| **Fadenkreuz** | Ein Kreuz, das der Mauszeiger-Position in der Kalibrierungsvorschau folgt. Es erscheint auf dem physikalischen Simulatorbildschirm, damit du in PHD2 sehen kannst, wohin BWMT denkt, dass das Leitfernrohr zeigt. |
| **Nummerierte Kalibrierungspunkte** | Jeder gesetzte Punkt wird mit seiner Sequenznummer angezeigt. Nordhalbkugel: #1 ist links und die Nummern erhöhen sich nach rechts. Südhalbkugel: #1 ist rechts und die Nummern erhöhen sich nach links. |
| **Verbindungslinie** | Eine Linie, die aufeinanderfolgende Kalibrierungspunkte verbindet und den Bogen zeigt, den die Montierung beschreibt. |

### Weboberfläche

<figure markdown="span">
  ![Kalibrierungs-Weboberfläche mit Vorschau-Canvas und Steuerelementen](BWMT_web_calibration.png)
  <figcaption>Die Weboberfläche des Calibrate-Tabs: Kalibrierungsvorschau-Canvas, Steuerelemente und Ellipsen-Fit-Parameter.</figcaption>
</figure>

#### Kalibrierungsvorschau-Canvas

Ein verkleinert dargestelltes Live-Bild des Simulatorbildschirms wird als Canvas angezeigt. Interaktion:

| Aktion | Auswirkung |
| --- | --- |
| **Schweben** | Bewegt das Fadenkreuz sowohl im Canvas als auch auf dem physikalischen Simulatorbildschirm. |
| **Linksklick** | Setzt einen neuen Kalibrierungspunkt an der aktuellen Fadenkreuzposition. |
| **Pfeiltasten** (↑ ↓ ← →) | Feinjustiert den aktuell ausgewählten Punkt um ein Pixel. Nur aktiv, wenn der Cursor über dem Canvas ist. |
| **S / E / D / F** | Alternative Feinjustierungstasten (S=oben, E=links, D=unten, F=rechts). |
| **Q oder BildAuf** | Wählt den vorherigen Kalibrierungspunkt aus. |
| **A oder BildAb** | Wählt den nächsten Kalibrierungspunkt aus. |

#### Steuerelemente

| Steuerelement | Beschreibung |
| --- | --- |
| **Punktanzahl** | Zeigt die Gesamtzahl der bisher aufgezeichneten Kalibrierungspunkte an. |
| **Zurücksetzen** | Löscht alle Kalibrierungspunkte und löscht den Ellipsen-Fit. |
| **Ausgewählten löschen** | Entfernt den aktuell ausgewählten Kalibrierungspunkt. |

#### Ellipsen-Fit-Parameter

Werden automatisch angezeigt, wenn fünf oder mehr Kalibrierungspunkte gesetzt wurden. Dies sind die Ergebnisse eines
Fits einer Ellipse an die aufgezeichneten Punkte.

| Parameter | Einheit | Beschreibung |
|---|---|---|
| **Mittelpunkt X** | m | Horizontale Position des Ellipsenmittelpunkts auf dem Simulatorbildschirm. |
| **Mittelpunkt Y** | m | Vertikale Position des Ellipsenmittelpunkts auf dem Simulatorbildschirm. |
| **Große Halbachse** | m | Länge der längeren Halbachse der angepassten Ellipse. |
| **Kleine Halbachse** | m | Länge der kürzeren Halbachse der angepassten Ellipse. |

---

## Velocity-Tab

Der Velocity-Tab ist der vierte Schritt. Du misst, wie schnell die Montierung den Simulatorbildschirm an drei Positionen
(linker, mittlerer, rechter Streifen) mit einer Stoppuhr überquert. Die gemessene Geschwindigkeit wird dann für eine
höhere Genauigkeit während der Simulation verwendet.

Das schrittweise Verfahren zur Geschwindigkeitsmessung findest du unter [Bildschirmgeschwindigkeit
messen](manual.md#bildschirmgeschwindigkeit-messen) im Handbuch.

### Simulatoranzeige

<figure markdown="span">
  ![Geschwindigkeitsbildschirm mit drei vertikalen Messstreifen](BWMT_velocity.png)
  <figcaption>Die Simulatoranzeige des Velocity-Tabs: drei vertikale Streifen zur Zeitmessung der Montierungsdurchquerung.</figcaption>
</figure>

Die Velocity-Simulatoranzeige zeigt drei vertikale Streifen auf schwarzem Hintergrund:

| Element | Beschreibung |
| --- | --- |
| **Linker Streifen** | Vertikaler Streifen im linken Drittel des Bildschirms, beschriftet mit "LEFT". Zeitmessung starten, wenn das PHD2-Bullseye den Streifen betritt; stoppen, wenn es ihn verlässt. |
| **Mittlerer Streifen** | Vertikaler Streifen in der Mitte des Bildschirms, beschriftet mit "MIDDLE". |
| **Rechter Streifen** | Vertikaler Streifen im rechten Drittel des Bildschirms, beschriftet mit "RIGHT". |
| **Streifenbreite** | Jeder Streifen ist so bemessen, dass die Montierung bei der erwarteten siderischen Geschwindigkeit etwa 3 Minuten benötigt, um ihn zu überqueren. |

Nordhalbkugel: links → Mitte → rechts messen. Südhalbkugel: rechts → Mitte → links messen (die Weboberfläche wechselt
die Stoppuhr-Auswahl automatisch in der richtigen Reihenfolge).

### Weboberfläche

<figure markdown="span">
  ![Velocity-Weboberfläche mit Stoppuhr und aufgezeichneten Zeiten](BWMT_web_velocity.png)
  <figcaption>Die Weboberfläche des Velocity-Tabs: Streifenauswahl, Stoppuhr, aufgezeichnete Zeiten und Geschwindigkeitsstatistiken.</figcaption>
</figure>

#### Streifenauswahl

Drei Schaltflächen — **Links**, **Mitte**, **Rechts** — wählen aus, in welchem Streifen die nächste Stoppuhrmessung
gespeichert wird. Der aktuell aktive Streifen ist hervorgehoben.

#### Stoppuhr

| Steuerelement | Beschreibung |
| --- | --- |
| **Zeitanzeige** | Zeigt die verstrichene Zeit im Format MM:SS.mmm (Minuten, Sekunden, Millisekunden) an. |
| **Start** | Startet die Zeitmessung. Drücken, wenn das Bullseye-Zentrum von PHD2 den ausgewählten Streifen betritt. |
| **Stop** | Stoppt die Zeitmessung und zeichnet die Zeit im ausgewählten Streifen auf. Drücken, wenn das Bullseye-Zentrum den Streifen verlässt. |
| **Zurücksetzen** | Löscht die Stoppuhr-Anzeige, ohne eine aufgezeichnete Streifenzeit zu beeinflussen. |

#### Aufgezeichnete Zeiten

Ein dreispaltiges Raster zeigt eine Karte pro Streifen. Jede Karte zeigt:

| Element | Beschreibung |
|---|---|
| **Aufgezeichnete Zeit** | Die zuletzt für diesen Streifen gemessene Zeit (MM:SS.mmm). |
| **Geschwindigkeit** | Abgeleitete Geschwindigkeit in Pixel pro Sekunde: `Streifenbreite_px / Überquerungszeit_s`. |
| **Löschen** | Löscht die aufgezeichnete Zeit für diesen Streifen und ermöglicht eine Wiederholungsmessung. |

#### Geschwindigkeitsstatistiken

| Wert | Beschreibung |
|---|---|
| **Streifenbreite** | Breite jedes Streifens in Pixeln. |
| **Erwartete Überquerungszeit** | Die theoretische Zeit (Sekunden) für die Montierung, um einen Streifen bei der aus der Konfiguration berechneten siderischen Geschwindigkeit zu überqueren. |
| **Min / Mittel / Max Geschwindigkeit** | Minimum, Durchschnitt und Maximum der über alle drei Streifen aufgezeichneten Geschwindigkeiten (px/s). |

---

## Measure-Tab

Der Measure-Tab ist der fünfte und letzte Schritt. Die Simulation läuft hier: BWMT bewegt einen gaußförmigen Stern mit
der gemessenen Geschwindigkeit über den Simulatorbildschirm, während PHD2 darauf führt.

Das vollständige Messverfahren — einschließlich der statistischen Fehlermessung und der Nachführsequenzen — findest du
unter [Qualifizierung des Messaufbaus](manual.md#qualifizierung-des-messaufbaus) und [Eine Nachführungssequenz
messen](manual.md#eine-nachfuhrungssequenz-messen) im Handbuch.

### Simulatoranzeige

Wenn der Measure-Tab aufgerufen wird, zeigt der Simulator einen **simulierten gaußförmigen Stern** an der Startposition
an:

- **Nordhalbkugel**: Der Stern erscheint auf der linken Seite des Bildschirms (wo der erste Kalibrierungspunkt gesetzt wurde).
- **Südhalbkugel**: Der Stern erscheint auf der rechten Seite.

Der Stern hat ein gaußförmiges Intensitätsprofil, das an Pixelpositionen abgetastet wird, mit einem Durchmesser von etwa
3 Pixeln. Um ein gutes Nachführprofil zu erhalten, stelle das Leitfernrohr vor Beginn der Messung absichtlich unscharf.

Weitere Simulatoranzeigeelemente während der Simulation:

| Element | Beschreibung |
| --- | --- |
| **Countdown-Überlagerung** | Eine Minute und 30 Sekunden vor dem Ende erscheint ein Countdown auf dem Bildschirm. Zehn Sekunden vor dem Ende piept BWMT 10 Mal. |
| **Warnüberlagerung** | Wenn keine Geschwindigkeitsstreifen gemessen wurden (nur geschätzte Geschwindigkeit), wird eine Warnung auf dem Simulatorbildschirm angezeigt. |

### Weboberfläche

<figure markdown="span">
  ![Measure-Tab-Weboberfläche mit Simulationsstatus und Mediensteuerelementen](BWMT_web_measure.png)
  <figcaption>Die Weboberfläche des Measure-Tabs: Simulationsstatus, Geschwindigkeit und Medienplayer-Steuerelemente.</figcaption>
</figure>

#### Simulationsstatus

| Element | Beschreibung |
| --- | --- |
| **Statusanzeige** | Zeigt den aktuellen Simulationszustand an: *Bereit*, *Läuft* oder *Abgeschlossen*. |
| **Verbleibende Zeit** | Countdown der verbleibenden Zeit in der Simulationssequenz. |
| **Fortschrittsbalken** | Visueller Prozentbalken. Klicke auf eine beliebige Stelle des Balkens, um zu dieser Position in der Simulation zu springen. |
| **Vergangene / Gesamtzeit** | Zeigt an, wie viel Zeit vergangen ist und die Gesamtdauer der Simulation. |

#### Simulationsparameter

| Element | Beschreibung |
|---|---|
| **Aktuelle Geschwindigkeit** | Die aktuelle Geschwindigkeit des Sterns in px/s. Die Quellenbezeichnung gibt an, wie diese Geschwindigkeit bestimmt wurde – siehe [Bestimmung der Simulationsgeschwindigkeit durch BWMT](manual.md#bestimmung-der-simulationsgeschwindigkeit-durch-bwmt). |
| **Geschwindigkeitsquelle** | Eine von: *geschätzt* (keine Streifenmessungen; theoretischer Wert), *Teildurchschnitt* (1–2 Streifen gemessen; konstanter Durchschnitt), oder *interpoliert* (alle 3 Streifen gemessen; quadratische Kurve über den Bildschirm). |
| **Geschwindigkeits-Override** | Ein optionales Eingabefeld (px/s), das die berechnete Geschwindigkeit überschreibt. Nützlich, wenn die Simulation systematisch zu schnell oder zu langsam läuft. |
| **Anwenden** | Wendet den Override-Wert sofort an. |
| **Löschen** | Entfernt den Override und kehrt zur berechneten Geschwindigkeit zurück. |

#### Mediensteuerung

| Schaltfläche | Aktion |
|---|---|
| ⏮ | Simulation auf den Anfang zurücksetzen (0 %). |
| ⏪ | 10 Sekunden zurückspringen. |
| ▶ / ⏸ | Simulation starten oder pausieren. |
| ⏩ | 10 Sekunden vorspringen. |
| ⏹ | Simulation stoppen und den Stern zur Startposition zurückbringen. |

#### Navigation

| Steuerelement | Beschreibung |
|---|---|
| **Zurück** | Kehrt zum Calibrate-Tab zurück, damit du die Kalibrierungspunkte verwenden kannst, um das Leitfernrohr auf dem Simulatorbildschirm neu zu positionieren. |
| **Aktuelle Konfiguration** | Öffnet die aktuelle Konfiguration als herunterladbare YAML-Datei in einem neuen Browser-Tab. |
| **Weiter** | *(Im letzten Tab deaktiviert)* |
