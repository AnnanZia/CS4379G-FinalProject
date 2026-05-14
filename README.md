# U.S. Crop Yield & Weather Analysis

## Project Overview

This project analyzes crop yield data across all states in the United States to identify long-term agricultural production patterns and regional differences. The analysis primarily focuses on corn because it provided the most complete and consistent dataset across production, acreage, and yield measurements.

The project explores:
- Crop production trends across the U.S.
- Corn yield, acreage, and production analysis
- Weather pattern analysis using temperature and precipitation data
- Relationships between weather conditions and agricultural productivity
- Identification of an optimal weather range for maximizing corn yield

The project also includes a Streamlit dashboard for interactive data visualization and exploration.

---

## Project Structure

```text
project-folder/
│
├── app.py
├── README.md
├── notebook.ipynb
├── Narrative_Draft.pdf
├── .gitignore
├── data/
│   ├── us_state_corn.csv
│   ├── us_state_crop_yield.csv
│   └── us_state_monthly_weather.csv
```

---

## How to Run the Project

1. Make sure the `data` folder is located in the same directory as `app.py`.

2. Ensure the `data` folder contains all 3 required dataset files.

3. Install the required Python libraries if needed : pandas, matplotlib, seaborn, plotly, streamlit

4. Run the notebook by restarting Kernal and then Run all.

4. Run the Streamlit dashboard using:

```bash
streamlit run app.py
```

5. The dashboard will open automatically in your browser.

---

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit

---

## Key Findings

- Corn production is heavily concentrated in Midwestern states.
- Corn yield has steadily increased over time due to advancements in agricultural technology.
- Weather conditions significantly impact agricultural productivity.
- Corn yield appears to be maximized near:
  - **31 inches of annual rainfall**
  - **66°F average temperature**
- Agricultural revenue does not always directly correlate with production levels due to market volatility.