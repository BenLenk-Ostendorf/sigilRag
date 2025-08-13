# Lernziel 5: Fehler in Siegeln identifizieren und korrigieren

## Was Sie lernen werden

Um das fünfte Lernziel zu erreichen, müssen Sie Fehler in Siegeln identifizieren und diese korrigieren können.

## Korrekte Siegelstandards verstehen

Um Fehler zu identifizieren, müssen Sie zunächst die korrekten Standards für Stadtsiegel verstehen:

### Korrekte Komponentenzuordnung

#### Bundeslandshintergrund
- **Korrekt**: Farben entsprechen exakt der Landesflagge
- **Fehler**: Falsche Farben oder falsche Farbkombination für das Bundesland

#### Bevölkerungsrahmen
- **Korrekt**: 
  - Über 1 Million: Zweifarbiger Rand mit grünen Spitzen
  - 500.000-1 Million: Zweifarbiger Rand mit Erhebungen
  - Unter 500.000: Einfarbiger Rand
- **Fehler**: Falscher Rahmentyp für die Bevölkerungsklasse

#### Hauptstadtkrone
- **Korrekt**:
  - Bundeshauptstadt: Krone mit zwei Unterstrichen in umgekehrten deutschen Flaggenfarben
  - Landeshauptstadt: Krone mit rotem Unterstrich
  - Ehemalige Bundeshauptstadt (Bonn): Nur die Krone
  - Andere Städte: Keine Krone
- **Fehler**: Falsche Krone oder Krone bei nicht-Hauptstädten

#### Orientierungskreis
- **Korrekt**: Gelber Kreis positioniert entsprechend der geografischen Lage im Bundesland
- **Fehler**: Falsche Position des gelben Kreises oder bei Stadtstaaten nicht vollständig gelb

#### Textelemente
- **Kurzkennzeichen**: Muss exakt dem offiziellen Kfz-Kennzeichen entsprechen
- **Koordinaten**: Format "LAT|LON" mit korrekten Werten
- **Gründungsjahr**: Verkürzt auf erste zwei Ziffern des Gründungsjahrs

## Häufige Fehlertypen

### 1. Dateninkonsistenzen
- **Beispiel**: München mit einfarbigem Rand (korrekt wäre zweifarbig mit Spitzen für >1 Million Einwohner)
- **Beispiel**: Frankfurt mit Hauptstadtkrone (Frankfurt ist keine Hauptstadt)
- **Beispiel**: Berlin ohne Bundeshauptstadtkrone

### 2. Geografische Fehler
- **Beispiel**: München mit gelbem Kreis im Norden (korrekt: Süden)
- **Beispiel**: Hamburg mit Bundeslandfarben von Bayern
- **Beispiel**: Falsche Koordinaten für die Stadt

### 3. Textfehler
- **Beispiel**: "MUC" statt "M" für München
- **Beispiel**: Vollständiges Jahr "1158" statt "12" für München
- **Beispiel**: Falsche Koordinatenangabe

### 4. Statusfehler
- **Beispiel**: Düsseldorf ohne Landeshauptstadtkrone
- **Beispiel**: Köln mit Hauptstadtkrone (ist keine Hauptstadt)
- **Beispiel**: Bonn mit Landeshauptstadtkrone (zwei Unterstriche) statt nur der Krone (ein Unterstrich)

## Systematische Fehlerprüfung

### Schritt 1: Stadtidentifikation
1. Stadt anhand sichtbarer Elemente identifizieren
2. Korrekte Daten aus der Referenztabelle entnehmen
3. Soll-Ist-Vergleich durchführen

### Schritt 2: Komponentenprüfung
1. **Bundeslandshintergrund**: Stimmen die Farben?
2. **Bevölkerungsrahmen**: Entspricht der Rahmen der Einwohnerzahl?
3. **Hauptstadtkrone**: Ist der Status korrekt dargestellt?
4. **Orientierungskreis**: Stimmt die geografische Position?
5. **Textelemente**: Sind alle Angaben korrekt?