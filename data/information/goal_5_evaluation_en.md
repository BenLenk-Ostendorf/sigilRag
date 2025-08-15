# Learning Goal 5: Identifying and Correcting Errors in Seals

## What You Will Learn

To achieve the fifth learning goal, you must be able to identify errors in seals and correct them.

## Understanding Correct Seal Standards

To identify errors, you must first understand the correct standards for city seals:

### Correct Component Assignment

#### State Background
- **Correct**: Colors correspond exactly to the state flag
- **Error**: Wrong colors or wrong color combination for the federal state

#### Population Frame
- **Correct**: 
  - Over 1 million: Two-colored border with green spikes
  - 500,000-1 million: Two-colored border with elevations
  - Under 500,000: Single-colored border
- **Error**: Wrong frame type for the population class

#### Capital Crown
- **Correct**:
  - Federal capital: Crown with two underlines in inverted German flag colors
  - State capital: Crown with red underline
  - Former federal capital (Bonn): Crown only
  - Other cities: No crown
- **Error**: Wrong crown or crown for non-capital cities

#### Orientation Circle
- **Correct**: Yellow circle positioned according to geographic location in the federal state
- **Error**: Wrong position of yellow circle or not completely yellow for city-states

#### Text Elements
- **Short Registration Plate**: Must exactly match the official vehicle registration plate
- **Coordinates**: Format "LAT|LON" with correct values
- **Founding Year**: Shortened to first two digits of the founding year

## Common Error Types

### 1. Data Inconsistencies
- **Example**: Munich with single-colored border (correct would be two-colored with spikes for >1 million inhabitants)
- **Example**: Frankfurt with capital crown (Frankfurt is not a capital)
- **Example**: Berlin without federal capital crown

### 2. Geographic Errors
- **Example**: Munich with yellow circle in the north (correct: south)
- **Example**: Hamburg with federal state colors of Bavaria
- **Example**: Wrong coordinates for the city

### 3. Text Errors
- **Example**: "MUC" instead of "M" for Munich
- **Example**: Complete year "1158" instead of "12" for Munich
- **Example**: Wrong coordinate specification

### 4. Status Errors
- **Example**: Düsseldorf without state capital crown
- **Example**: Cologne with capital crown (is not a capital)
- **Example**: Bonn with state capital crown (two underlines) instead of crown only (one underline)

## Systematic Error Checking

### Step 1: City Identification
1. Identify city based on visible elements
2. Extract correct data from reference table
3. Perform target-actual comparison

### Step 2: Component Checking
1. **State Background**: Do the colors match?
2. **Population Frame**: Does the frame correspond to the population?
3. **Capital Crown**: Is the status correctly represented?
4. **Orientation Circle**: Is the geographic position correct?
5. **Text Elements**: Are all specifications correct?
