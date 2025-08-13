# Fehlende Informationen aus unvollständigen Siegeln ableiten

## Verwendung der Stadtdaten zur Analyse

Wenn Sie ein unvollständiges Siegel analysieren, können Sie die verfügbaren Stadtdaten nutzen, um fehlende Informationen zu erschließen:

| Nr. | Stadt              | Einwohner  | Gegründet          | Bundesland             | Lage im Bundesland | Hauptstadtstatus        | Kennzeichen | Koordinaten (Präzise)  |
| --- | ----------------- | ---------- | ------------------ | ---------------------- | ----------------- | ----------------------- | ----------- | ---------------------- |
| 1   | Berlin            | 3,664,088  | 1237               | Berlin                 | -                 | Bundes- & Landeshauptstadt | B           | 52.5170° N, 13.3889° E |
| 2   | Hamburg           | 1,852,478  | 1189               | Hamburg                | -                 | Landeshauptstadt           | HH          | 53.5511° N, 9.9937° E  |
| 3   | München           | 1,488,202  | 1158               | Bayern                 | Süd               | Landeshauptstadt           | M           | 48.1371° N, 11.5755° E |
| 4   | Köln              | 1,083,498  | 50 v. Chr.         | Nordrhein-Westfalen    | West              |                         | K           | 50.9352° N, 6.9531° E  |
| 5   | Frankfurt am Main | 764,104    | 794                | Hessen                 | Südwest           |                         | F           | 50.1109° N, 8.6821° E  |
| 6   | Stuttgart         | 630,305    | 950                | Baden-Württemberg      | Zentral           | Landeshauptstadt           | S           | 48.7833° N, 9.1833° E  |
| 7   | Düsseldorf        | 620,523    | 1288               | Nordrhein-Westfalen    | West              | Landeshauptstadt           | D           | 51.2217° N, 6.7762° E  |
| 8   | Leipzig           | 597,493    | 1015               | Sachsen                | Nordwest          |                         | L           | 51.3402° N, 12.3601° E |
| 9   | Dortmund          | 587,696    | 882                | Nordrhein-Westfalen    | West              |                         | DO          | 51.5142° N, 7.4684° E  |
| 10  | Essen             | 582,415    | 845                | Nordrhein-Westfalen    | West              |                         | E           | 51.4508° N, 7.0131° E  |
| 11  | Bremen            | 566,573    | 787                | Bremen                 | -                 | Landeshauptstadt           | HB          | 53.0736° N, 8.8064° E  |
| 12  | Dresden           | 556,227    | 1206               | Sachsen                | Ost               | Landeshauptstadt           | DD          | 51.0504° N, 13.7373° E |
| 13  | Hannover          | 534,049    | 1150               | Niedersachsen          | Zentral           | Landeshauptstadt           | H           | 52.3739° N, 9.7356° E  |
| 14  | Nürnberg          | 515,543    | 1050               | Bayern                 | Nord              |                         | N           | 49.4610° N, 11.0619° E |
| 15  | Duisburg          | 495,885    | 883                | Nordrhein-Westfalen    | West              |                         | DU          | 51.4351° N, 6.7627° E  |
| 16  | Bochum            | 364,454    | 890                | Nordrhein-Westfalen    | West              |                         | BO          | 51.4818° N, 7.2162° E  |
| 17  | Wuppertal         | 355,004    | 1929 (Zusammenschluss) | Nordrhein-Westfalen    | West              |                         | W           | 51.2562° N, 7.1508° E  |
| 18  | Bielefeld         | 333,509    | 1214               | Nordrhein-Westfalen    | Nordost           |                         | BI          | 52.0211° N, 8.5347° E  |
| 19  | Bonn              | 330,579    | 1. Jh. v. Chr.     | Nordrhein-Westfalen    | Süd               | Ehemalige Bundeshauptstadt  | BN          | 50.7333° N, 7.1000° E  |
| 20  | Münster           | 316,403    | 793                | Nordrhein-Westfalen    | West              |                         | MS          | 51.9616° N, 7.6282° E  |

## Analysemethoden für unvollständige Siegel

### 1. Identifikation durch sichtbare Elemente

#### Kurzkennzeichen erkennbar
Wenn das Kfz-Kennzeichen sichtbar ist, können Sie direkt die entsprechende Stadt in der Tabelle finden und alle anderen Informationen ableiten.

#### Koordinaten erkennbar
Bei sichtbaren Koordinaten können Sie diese mit der Tabelle abgleichen und die Stadt identifizieren.

#### Gründungsjahr erkennbar
Das verkürzte Gründungsjahr im Zentrum kann zur Identifikation genutzt werden (z.B. "12" für München, gegründet 1158).

### 2. Ableitung durch Siegelkomponenten

#### Bundeslandshintergrund
Die Farben des Hintergrunds verraten das Bundesland. Daraus können Sie die möglichen Städte eingrenzen. Aber bedenken Sie, dass es viele Städte auch mit ähnlicher Orientierung geben kann.

#### Bevölkerungsrahmen
- Zweifarbiger Rand mit grünen Spitzen → über 1 Million Einwohner
- Zweifarbiger Rand mit Erhebungen → 500.000 bis 1 Million Einwohner
- Einfarbiger Rand → unter 500.000 Einwohner

#### Hauptstadtkrone
- Krone mit zwei Unterstrichen → Bundeshauptstadt (Berlin)
- Krone mit rotem Unterstrich → Landeshauptstadt
- Nur Krone → ehemalige Bundeshauptstadt (Bonn)

#### Orientierungskreis
Die Position des gelben Kreises zeigt die Lage der Stadt im Bundesland an.

### 3. Kombinierte Analyse
Durch die Kombination mehrerer sichtbarer Elemente können Sie systematisch die Möglichkeiten eingrenzen:

**Beispiel**: 
- Blau-weißer Hintergrund → Bayern
- Krone mit rotem Unterstrich → Landeshauptstadt
- Gelber Kreis im Süden → südliche Lage
- Ergebnis: München

**Beispiel**:
- Zweifarbiger Rand mit grünen Spitzen → über 1 Million Einwohner
- Krone mit zwei Unterstrichen → Bundeshauptstadt
- Ergebnis: Berlin
