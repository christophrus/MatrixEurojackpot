# Matrix-Eurojackpot

Eine kleine, spielerische Simulation/Visualisierung: die Ziehungsvorhersage für Eurojackpot, präsentiert als "Matrix-Computer" Simulation. Diese README erklärt, wie das Skript funktioniert, wie man es startet und welche Mechaniken (CSV, Seed, deterministische Zufallsfunktion, Warmup) dahinterstecken — unter der Prämisse, dass wir in einer deterministischen Matrix-Computer-Simulation leben.

## Kurze Prämisse (für den Stil)
Stell dir vor, die Welt läuft in einer deterministischen Matrix: dieselben Eingaben (Datum, historische Ziehungsdaten, optionaler Seed-String) führen immer zur selben Ausgabe. Genau das nutzt diese Demo: sie berechnet deterministisch fünf Hauptzahlen und zwei Eurozahlen für die nächste Eurojackpot-Ziehung, zeigt eine Matrix-Rain-Animation im Hintergrund und tippt die Ergebnisse im Vordergrund aus.

## Dateien im Repository
- `index.html` — das ganze Programm: Canvas-Matrix-Effekt, CSV-Loader, deterministische Generator-Logik, UI, Audio.
- `history.csv` — historische Ziehungsdaten (wird vom Skript geladen). Das Format ist: Datum,5x Hauptzahlen,2x Eurozahlen (kommasepariert) pro Zeile.

## Voraussetzungen
- Ein moderner Browser (Chrome, Firefox, Edge).
- Die Seite muss über HTTP(S) geladen werden, nicht über `file://`, weil `fetch('history.csv')` sonst scheitern kann. Daher empfiehlt sich ein einfacher lokaler Webserver.

### Starten eines einfachen Servers (PowerShell)
Python (falls installiert):

```powershell
# im Projektverzeichnis (d:\Github\MatrixEurojackpot)
python -m http.server 8000
# dann im Browser öffnen: http://localhost:8000
```

Oder mit Node (falls installiert):

```powershell
# mit npx (keine Installation notwendig)
npx http-server -p 8000
# dann: http://localhost:8000
```

Oder einfach die Datei `index.html` in einem Browser öffnen, falls Ihr Browser `fetch` von lokalen Dateien erlaubt — empfohlen wird jedoch ein lokaler Server.

## So funktioniert das Script (Kurzfassung)
1. Beim Klick auf "Start Simulation":
   - Versteckt die UI-Controls.
   - Erstellt eine `AudioContext` (für die warmup- und victory-Sounds).
   - Zeigt die weiße, halbtransparente Textbox (zentriert) und leert sie.
   - Lädt `history.csv` asynchron in kleinen Chunks (z.B. 200 Zeilen pro Durchgang), um den UI-Thread nicht zu blockieren.
2. Matrix-Hintergrund startet (Canvas mit fallenden Zeichen). Das Script überwacht, ob jede Spalte mindestens einmal den unteren Bildschirmrand erreicht hat — das ist der "Warmup"-Zustand.
   - Während Warmup läuft, gibt es einen leisen Ton-Loop (warmerup sound). Sobald alle Spalten mindestens einmal unten waren (oder ein Timeout erreicht ist), wird der Warmup gestoppt.
3. Nach Warmup (oder Timeout) wird die deterministische Generierung gestartet:
   - Die Funktion summiert alle Zahlen aus `history` (Chunked, um Hänger zu verhindern) zu `prevSum`.
   - Aus dem gewünschten Ziehungsdatum (Nächstes Ziehungsdatum: Dienstag/Freitag 21:00) werden Jahr/Monat/Tag/Wochentag extrahiert.
   - Ein optionaler Seed-String wird positionsabhängig in eine Zahl umgewandelt.
   - Eine einfache, deterministische Pseudozufallsfunktion auf Basis von `Math.sin(seed)` wird verwendet, kombiniert mit `prevSum`, Datum und dem Seed-Number, damit dieselben Eingaben immer dieselben Ausgaben erzeugen.
   - Es werden 5 eindeutige Hauptzahlen (1–50) und 2 eindeutige Eurozahlen (1–12) erzeugt und sortiert.
4. UI-Animationen:
   - Lade-Spinner wird gezeigt, dann verschwindet er nach Ende der Animation.
   - Text wird zeichenweise getippt (typewriter effect). Die Zahlen selbst werden kurz animiert (rasende Zufallszahlen) und landen dann auf den deterministischen Endwerten.
   - Am Ende spielt ein kurzer Victory-Sound.

## Wichtige Implementierungsdetails
- Chunked CSV-Parsing: `loadCSV()` liest die Datei und verarbeitet sie in Blöcken (z.B. 200 Zeilen), mit `await new Promise(r => setTimeout(r,0))` zwischen den Blöcken. Das hält die UI reaktionsfähig.
- Defensive Parsing & Robustheit: malformed Zeilen in `history.csv` werden übersprungen. Werte werden mit `Number.isFinite` geprüft, damit keine `NaN`-Summen die Deterministik zerstören.
- Determinismus: Die Pseudozufallsfunktion ist bewusst einfach und deterministisch (kein echtes PRNG):
  ```js
  function pseudoRandom(seed, range) {
    let x = Math.sin(seed) * 10000;
    return Math.floor(Math.abs(x) % range) + 1;
  }
  ```
  - Die verwendeten Seed-Komponenten (Datum, prevSum, seedNum und kleine Offsets) sorgen dafür, dass bei gleichen Eingaben das gleiche Ergebnis entsteht.
- Warmup-Mechanik: Das Script beobachtet, ob jede Matrix-Spalte einmal den Boden berührt hat. Erst dann (oder nach Timeout) wird mit der Anzeige begonnen. So ist sichergestellt, dass der Matrix-Hintergrund sichtbar "gefüllt" ist, bevor der Text einblendet.
- Audio: Erzeugt per OscillatorNode (WebAudio). `AudioContext` wird beim Start erstellt (User-Gesture), damit Autoplay-Policy nicht blockiert.

## UI / Styling
- Die Textbox ist zentriert (`#textContainer`) und hat eine semi-transparente weiße Hintergrundfarbe; der Text inside ist linksbündig (`#output`).
- Spinner (`#loading`) wird während der Berechnung gezeigt.

## Troubleshooting
- Kein Text sichtbar:
  - Prüfe die DevTools-Konsole (F12). Häufige Ursachen:
    - `fetch('history.csv')` schlägt fehl (404) oder ist durch `file://`-Kontext blockiert — starte lokalen Server.
    - JavaScript-Fehler: siehst du Exceptions? Kopiere die ersten Fehler hierher, ich helfe weiter.
    - AudioContext-Fehler: Browser kann AudioContext nur nach Benutzerinteraktion starten (der Start-Button sorgt dafür).
- Ergebnisse scheinen falsch oder "NaN" auftauchen:
  - Prüfe `history.csv` auf beschädigte Zeilen. Das Skript loggt und überspringt solche Zeilen, aber wenn viele Zeilen inkorrekt sind, ändert das die Summe.

## Anpassungen — was und wo
- `history.csv` formatieren: jede Zeile `DD-MM-YYYY,n1,n2,n3,n4,n5,e1,e2`
- Farben / Box-Breite: in `index.html` im `<style>`-Block `#textContainer` / `#output` anpassen (background, width, padding).
- Längere/andere Animations-Behavior: `animateNumbers()` und `typeOutText()` anpassen.

## Sicherheit und deterministische Ethik (kurz)
Diese Demo ist rein illustrativ. Determinismus und Vorhersage sind künstlerische/technische Spielereien — in der echten Welt sind Lotterien zufällig und reguliert.
