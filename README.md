<img src="logo.jpeg" align="right" width="250"  />

# Schneider Electric European Hackathon 2023

Hackathon organized by NUWE and Schneider Electric ([Link to Event](https://nuwe.io/dev/competitions/schneider-electric-european-2023))  

Division: EcoForecast: Revolutionizing Green Energy Surplus Prediction in Europe  

Team: **CleanCoders**  

### About The Project: 

||Description|
|------|---------------------------------------------------------------------------------------------------------------|
| Goal | Predict which European country (by code 1 to 9) will have the highest surplus of green energy in the next hour. |
| Forecast Variable | The surplus of green energy is the difference between the summation of all generated green energy and the consumed energy (load). |
| Data | You can only use data up to 2023-01-01. |

### Repo Structure
 
     |__README.md
     |__requirements.txt
     |
     |__data
     |  |__processed_data.csv
     |  |__[...]                      # various gen and load .csv files for each country
     |
     |__src
     |  |__data_ingestion.py          # import data and save to .csv files in ./data
     |  |__data_processing.py         # preprocess data (reindex, interpolate, features, and labeling)
     |  |__model_training.py          # train SARIMA model
     |  |__model_prediction.py        # output predictions
     |  |__utils.py                   # util functions to process get requests to ENTSO-E API                      
     |
     |__models
     |  |__model.pkl
     |
     |__z_notebooks
     |  |__[...]                      # various ipynb for exploratory data analysis etc
     |
     |__scripts
     |  |__run_pipeline.sh
     |
     |__predictions
     |  |__predictions.json

### Data Import

get ENTSOE Data through API with security tokens:
- 1d9cd4bd-f8aa-476c-8cc1-3442dc91506d
- fb81432a-3853-4c30-a105-117c86a433ca

### Data Processing

Green energies are defined as: ["B01", "B09", "B10", "B11", "B12", "B13", "B15", "B16", "B18", "B19"].  
(See ENTSO-E [API - user guide](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_psrtype:~:text=Hourly-,A.5.%20PsrType,-Code) for further information.)

| Code | Meaning |
|------|--------|
| B01 | Biomass |
| B09 | Geothermal |
| B10 | Hydro Pumped Storage |
| B11 | Hydro Run-of-river and poundage |
| B12 | Hydro Water Reservoir |
| B13 | Marine |
| B15 | Nuclear |
| B16 | Solar |
| B18 | Wind Offshore |
| B19 | Wind Onshore |

- Imported data is first reindexed based on its original frequency either in 15 min or 60 min intervals, missing intervals get NaN.
- The data is then resampled and aggregated to hourly intervals.
- Linear interpolation where missing values in the dataset are imputed as the mean between the preceding and following values.

``` py
# Example:
df.interpolate(method='linear', limit_direction='both', inplace=True)
```
 
- Green energy types are summed up to a column representing total green energy production per country (e.g. DE_green_energy)
- Using load data (e.g. DE_load) we can then calculate surplus green energy production by subtracting load from total green energy production by country (e.g. DE_green_surplus)
  
You will also need to add an additional column that will be your label: the ID of the country with the bigger surplus of green energy for the next hour.
The country IDs used to evaluate your model will be the following:

| Country Label | Code | Name             |
|---------------|------|------------------|
| SP            | 0    | Spain            |
| UK            | 1    | United Kingdom   |
| DE            | 2    | Germany          |
| DK            | 3    | Denmark          |
| HU            | 5    | Hungary          |
| SE            | 4    | Sweden           |
| IT            | 6    | Italy            |
| PO            | 7    | Poland           |
| NL            | 8    | Netherlands      |

### Model

SARIMA-X from statsmodels

### Train Test Split

- Train = 80% and Test = 20%
- F1 Macro Score used as metric

### Prediction

- 1 step ahead forecast are made
