# Deriving Missing Information from Incomplete Seals

## Using City Data for Analysis

When analyzing an incomplete seal, you can use the available city data to derive missing information:

| No. | City              | Population | Founded            | Federal State          | Location in State | Capital Status          | Registration | Coordinates (Precise)  |
| --- | ----------------- | ---------- | ------------------ | ---------------------- | ----------------- | ----------------------- | ------------ | ---------------------- |
| 1   | Berlin            | 3,664,088  | 1237               | Berlin                 | -                 | Federal & State Capital | B            | 52.5170° N, 13.3889° E |
| 2   | Hamburg           | 1,852,478  | 1189               | Hamburg                | -                 | State Capital           | HH           | 53.5511° N, 9.9937° E  |
| 3   | Munich            | 1,488,202  | 1158               | Bavaria                | South             | State Capital           | M            | 48.1371° N, 11.5755° E |
| 4   | Cologne           | 1,083,498  | 50 BC              | North Rhine-Westphalia | West              |                         | K            | 50.9352° N, 6.9531° E  |
| 5   | Frankfurt am Main | 764,104    | 794                | Hesse                  | Southwest         |                         | F            | 50.1109° N, 8.6821° E  |
| 6   | Stuttgart         | 630,305    | 950                | Baden-Württemberg      | Central           | State Capital           | S            | 48.7833° N, 9.1833° E  |
| 7   | Düsseldorf        | 620,523    | 1288               | North Rhine-Westphalia | West              | State Capital           | D            | 51.2217° N, 6.7762° E  |
| 8   | Leipzig           | 597,493    | 1015               | Saxony                 | Northwest         |                         | L            | 51.3402° N, 12.3601° E |
| 9   | Dortmund          | 587,696    | 882                | North Rhine-Westphalia | West              |                         | DO           | 51.5142° N, 7.4684° E  |
| 10  | Essen             | 582,415    | 845                | North Rhine-Westphalia | West              |                         | E            | 51.4508° N, 7.0131° E  |
| 11  | Bremen            | 566,573    | 787                | Bremen                 | -                 | State Capital           | HB           | 53.0736° N, 8.8064° E  |
| 12  | Dresden           | 556,227    | 1206               | Saxony                 | East              | State Capital           | DD           | 51.0504° N, 13.7373° E |
| 13  | Hannover          | 534,049    | 1150               | Lower Saxony           | Central           | State Capital           | H            | 52.3739° N, 9.7356° E  |
| 14  | Nuremberg         | 515,543    | 1050               | Bavaria                | North             |                         | N            | 49.4610° N, 11.0619° E |
| 15  | Duisburg          | 495,885    | 883                | North Rhine-Westphalia | West              |                         | DU           | 51.4351° N, 6.7627° E  |
| 16  | Bochum            | 364,454    | 890                | North Rhine-Westphalia | West              |                         | BO           | 51.4818° N, 7.2162° E  |
| 17  | Wuppertal         | 355,004    | 1929 (Merger)      | North Rhine-Westphalia | West              |                         | W            | 51.2562° N, 7.1508° E  |
| 18  | Bielefeld         | 333,509    | 1214               | North Rhine-Westphalia | Northeast         |                         | BI           | 52.0211° N, 8.5347° E  |
| 19  | Bonn              | 330,579    | 1st Century BC     | North Rhine-Westphalia | South             | Former Federal Capital  | BN           | 50.7333° N, 7.1000° E  |
| 20  | Münster           | 316,403    | 793                | North Rhine-Westphalia | West              |                         | MS           | 51.9616° N, 7.6282° E  |

## Analysis Methods for Incomplete Seals

### 1. Identification Through Visible Elements

#### Short Registration Plate Recognizable
If the vehicle registration plate is visible, you can directly find the corresponding city in the table and derive all other information.

#### Coordinates Recognizable
With visible coordinates, you can match them with the table and identify the city.

#### Founding Year Recognizable
The shortened founding year in the center can be used for identification (e.g., "12" for Munich, founded 1158).

### 2. Derivation Through Seal Components

#### State Background
The colors of the background reveal the federal state. From this, you can narrow down the possible cities. But keep in mind that there can be many cities with similar orientation.

#### Population Frame
- Two-colored border with green spikes → over 1 million inhabitants
- Two-colored border with elevations → 500,000 to 1 million inhabitants
- Single-colored border → under 500,000 inhabitants

#### Capital Crown
- Crown with two underlines → Federal capital (Berlin)
- Crown with red underline → State capital
- Crown only → Former federal capital (Bonn)

#### Orientation Circle
The position of the yellow circle indicates the location of the city within the federal state.

### 3. Combined Analysis
By combining multiple visible elements, you can systematically narrow down the possibilities:

**Example**: 
- Blue-white background → Bavaria
- Crown with red underline → State capital
- Yellow circle in the south → Southern location
- Result: Munich

**Example**:
- Two-colored border with green spikes → over 1 million inhabitants
- Crown with two underlines → Federal capital
- Result: Berlin
