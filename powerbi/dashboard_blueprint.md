# Power BI Dashboard Blueprint — COVID Infectious Disease Trend Analytics

## Data Source
Import `data/processed/powerbi_fact_main.csv`.

## Model
Create a Calendar table and relate it to the main date field.

## Pages

### 1. Executive Overview
- KPI cards: Total Records, High Risk Rate, Average Value
- Monthly trend line chart
- Top categories bar chart

### 2. Deep-Dive Analysis
- Slicers: date, region/category, segment
- Matrix table with category performance
- Drill-through page for individual case/entity

### 3. ML Insights
- Prediction probability distribution
- Feature importance bar chart
- Confusion matrix table from model output

### 4. Recommendations
- Risk segments
- Business/clinical actions
- Monitoring plan

## Design
Use a clean blue/white executive theme. Keep 4–6 visuals per page.
