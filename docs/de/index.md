# Bad Weather Mount Tester

Wenn du eine neue Teleskop-Montierung kaufst, ist das Erste, was du tun solltest, den periodischen Fehler zu messen. Denn wenn der periodische Fehler wirklich groß ist, möchtest du dich beschweren und sie so schnell wie möglich zurückschicken. Leider gibt es nach dem Kauf von Astro-Equipment für eine unbestimmte Zeit fast immer schlechtes Wetter.

**Bad Weather Mount Tester kommt zur Rettung!**

Mit diesem Programm kannst du den periodischen Fehler deiner Montierung jederzeit und überall testen, vorausgesetzt du hast einen freien Computer, einen Monitor und ein bisschen Platz.

<picture>
  <img alt="Bad Weather Mount Tester Logo" src="BWMT_logo_b.svg">
</picture>

## Wie funktioniert Bad Weather Mount Tester?

Du verwendest einen kleinen Computer, um einen Stern zu simulieren, der sich über einen Monitor bewegt, und zeichnest diese Bewegung mit einer Nachführanwendung auf. Da der Monitor sehr regelmäßig ist, kann man den periodischen Fehler der Montierung jederzeit und überall messen, solange der Platz groß genug ist und ein Dach oben drüber ist.

!!! important
    Der Südhalbkugel-Modus wird momentan noch nicht unterstützt.

## Was will Bad Weather Mount Tester erreichen?

Mit relativ günstigem Material (deine Montierung, dein Leitfernrohr, ein Computer und ein Bildschirm) versuchen wir eine **Präzisionsmessung** durchzuführen: Wir messen den periodischen Fehler, der in einem Winkel übersetzt nur <u>wenige Bogensekunden</u> beträgt. 1 Bogensekunde ist 1/3600 eines Grades = 1". Lass uns ein Gefühl dafür entwickeln:

**Wie klein ist 1 Bogensekunde?**

Wenn du eine 1-Euro-Münze, die einen Durchmesser von 24,25 mm hat, auf eine Entfernung von 4800 m stellst, beträgt der Winkel von oben nach unten der Münze 1". Um so weit zu sehen — das ist zufällig die Entfernung zum Horizont an einem vollkommen windstillen Tag, wenn man am Ufer steht (für Augen einer Person von ca. 1,8 m Größe) — würde das nicht reichen, da das menschliche Auge eine Auflösung von ungefähr 1/60 eines Grades (1 Bogenminute = 1') hat. Du müsstest 60 Euros in einer Reihe aufstellen, zwei Taschenlampen an das linke und rechte Ende dieser Reihe stellen, und dann könnten deine Augen gerade eben erkennen, dass es zwei Lichter am Horizont gibt und nicht eines.

<picture>
  <img alt="Intuition für 1 Bogensekunde: Eine Strichfigur schaut auf eine Reihe von 60 EURO-Münzen in 4800 m Entfernung. In dieser Entfernung entspricht die gesamte Reihe 1 Bogenminute und 1 EURO mit einem Durchmesser von 24,25 mm entspricht 1 Bogensekunde" src="BWMT_1arcsec.svg">
</picture>
Quelle: 1€ Wikipedia

**Was bedeutet das für die Fertigungsanforderungen einer Montierung?**

Wenn man die Komponenten einer Schneckengetriebe-Montierung betrachtet, entspricht dies Fertigungstoleranzen, die an oder über der Präzision liegen, die normale Zerspanung leisten kann.

<picture>
  <a title="Herzi Pinki, CC BY-SA 3.0 &lt;https://creativecommons.org/licenses/by-sa/3.0&gt;, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Hourglass_Panta_Rhei,_Ybbsitz_-_worm_gear_detail.jpg"><img width="256" alt="Hourglass Panta Rhei, Ybbsitz - Schneckengetriebe-Detail" src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Hourglass_Panta_Rhei%2C_Ybbsitz_-_worm_gear_detail.jpg/256px-Hourglass_Panta_Rhei%2C_Ybbsitz_-_worm_gear_detail.jpg?20120513164256"></a>
</picture>

Beispiel eines Schneckengetriebes: Das Schneckenrad unten treibt das Schneckenrad oben an.

<picture>
  <img alt="abc" src="BWMT_wormdrive_AZEQ6.svg">
</picture>

Nimm zum Beispiel das Schneckenrad eines SkyWatcher AZ-EQ6: Es hat einen Außendurchmesser von 92,5 mm und 180 Zähne. An der Position der Zähne, d. h. auf dem Außendurchmesser, und wenn der Durchmesser genau 92,5 mm wäre, beträgt 1" 225 Nanometer (= λ/2). Für eine Bogensekunde Variation müssen die Zähne regelmäßig mit einem Abstand von 1,6144 mm +/- 1 in der letzten Stelle angeordnet sein (1 in der letzten Stelle entspricht +/- 100 nm ~ λ/4!). Normalerweise liegt die Bearbeitungsgenauigkeit in der Größenordnung von 0,001 mm, d. h. 1 µm, ein Faktor 10 zu groß. Ein ähnliches Argument gilt für das Schneckenrad (siehe Abbildung) und beide Unregelmäßigkeiten addieren sich, daher die Anforderung λ/4 zu erreichen. Jede Unebenheit oder Unregelmäßigkeit bei der Herstellung des Gewindes im Schneckenrad führt zu Abweichungen beim Nachführen.

Hochpreisige High-End-Montierungen, die einen maximalen periodischen Fehler (PE) spezifizieren, bieten meist &lt; +/- 5" oder &lt; +/- 10", was der erreichbaren Maschinengenauigkeit entspricht. Strain-Wave-Getriebe geben üblicherweise ähnliche "PE"-Werte an.

Beachte, dass hochpräzise Encoder-Montierungen absolute optische Encoder verwenden, wie z. B. das [Renishaw RESA](https://www.renishaw.com/en/--37823)-System, das in der Lage ist, die Position eines Lesekopfes auf einem Encoder-Ring bis auf 1 nm zu bestimmen, was dann von der Firmware verwendet wird, um die Fertigungstoleranzen zu korrigieren.

**Was bedeutet das für Bad Weather Mount Tester?**

Wir verwenden kostengünstiges, nur teilweise präzisions-bearbeitetes Equipment, um eine Präzisionsmessung durchzuführen. Insbesondere messen wir die Fertigungstoleranzen deiner Montierung, die in der Größenordnung einer halben Wellenlänge oder weniger liegen — _ohne_ eine optische Messung (Interferometrie) zu verwenden. Das bedeutet, wir müssen zuerst unseren Ansatz so verstehen und qualifizieren, dass wir Vertrauen in die gemessenen Werte haben können.

## Erste Schritte

- [Einrichtung](setting_up.md) — Voraussetzungen für Messungen und Installation von Bad Weather Mount Tester auf einem Computer
- [Handbuch](manual.md) — Verwendung von Bad Weather Mount Tester und vollständiger Messleitfaden
- [GitHub-Repository](https://github.com/jscheidtmann/BadWeatherMountTester) — Quellcode, Probleme und Versionen
