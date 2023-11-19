# SE-Europe-Data_Challenge_Template

GOAL = predict which European country (by code 1 to 9) will have the highest surplus of green energy in the next hour.

FCAST VARIABLE = the surplus of green energy is the difference between the summation of all generated green energy and the consumed energy (load).

DATA = you can only use data up to 01-01-2023

### Data Import

- [x] write code to get ENTSOE Data through API

You will need to provide a security token to make the ENTSO-E API calls. You can use the following one:
1d9cd4bd-f8aa-476c-8cc1-3442dc91506d

If the first token reaches its API calls rate limit, you can use the next token:
fb81432a-3853-4c30-a105-117c86a433ca

### Data Processing

#### UPDATE

-> The green energies, you can use the ones mentioned above: ["B01", "B09", "B10", "B11", "B12", "B13", "B15", "B16", "B18", "B19"].

-> The key is in the resampling of 1 hour intervals.
    - Is it possible to group data where there is more than one data in an hour? Yes, in fact that's what you should do! Example: I have 4 values in the same hour, I will have to find the most reliable way to represent those 4 values as one.
    - If I only have data for one hour, what do I do? Only the data of that hour is taken, the other 23 hours are not taken.
    - If I have only 15 minutes of data for one hour, what do I do? There are operations that can be applied to fill in the other 3 and get the value of the hour. This is for you to decide.

-> When is it considered that there is no data? The key is that you have to gather all countries and adjust the intervals regularly to 1H, when there are countries that have no data at a certain time or day, that is simply 0 (or the NaN should be set to 0 as the challenge explains, it is part of handling the missing data).

-> How to interpolate the data: "Missing values in the dataset should be imputed as the mean between the preceding and following values". 
    Example:
    #Interpolate any missing data
    df.interpolate(method='linear', limit_direction='both', inplace=True)

We have decided to accept any solution, whether or not the predictions of 442 values are reached, and to correct each solution one by one. That is to say, even if you try the F1-score and it gives you a low score, it will not be so, as it will be corrected one by one. Also, in order to give you more time, we have decided to leave one more day to make the deliveries. So the final date is Tuesday 21st at 10 CET.

---

Missing values in the dataset should be imputed as the mean between the preceding and following values. Data with resolution finer than 1 hour must be resampled to an hourly level.

identify what energy types each column represent, and discard the ones that are not green energy sources (You can refer to the ENTSO-E Transparency portal API documentation to understand how the energy source types are represented)

end up with a single CSV file which includes columns per country representing the following values: generated green energy per energy type (one column per wind, solar, etc), and load. Make sure that all those values are in the same units (MAW).

check the exact columns that will need to appear in your dataset by looking at the test.csv file provided inside the data folder.

You will also need to add an additional column that will be your label: the ID of the country with the bigger surplus of green energy for the next hour.

The country IDs used to evaluate your model will be the following:

SP: 0, # Spain  
UK: 1, # United Kingdom  
DE: 2, # Germany  
DK: 3, # Denmark  
HU: 5, # Hungary  
SE: 4, # Sweden  
IT: 6, # Italy  
PO: 7, # Poland  
NL: 8  # Netherlands  

### Model

Your model predictions with the test data should be stored in the same format at the example_predictions.json file provided where for each entry (data point of your time series) you have a country ID predicted for the next hour. 

The final file should be called predictions.json. This file will be the one used to evaluate your model performance on F1-score macro.

### Train Test Split

Green Generation
Load

Ziel = diese beiden fcasten damit Surplus geschätzt werden

Train = 80%

Model 1 = ARMA (1,1)
Model 2 = ARMA (2,2)

t=80

Test = 20%

1) zusammenhängende i - step ahead fcast mit i in {1,...,20} auf basis von fcast also fcast 2 = beta * fcast 1
  
2) 1-step ahead fcast, aber dann 2-step auf basis von realisiertem werte in h=1
3) mache 1-step ahead (t=81) fcast mit beta1 , gegeben realisation fitte neues ARMA und mache nächsten 1-step (t=82) fcast mit beta2
   
### Evaluation
If we download 2022 data
database resampled by hour
there is only 442 rows left
