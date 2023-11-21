import pandas as pd
import statsmodels.api as sm
import argparse
import pickle

import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning, ModelWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', ModelWarning)
warnings.simplefilter('ignore', UserWarning)

def load_data(file_path : str):

    """ 
    Method loads data from CSV file

    """

    df = pd.read_csv(file_path)

    return df

def split_data(df : pd.DataFrame):

    """ 
    Method splits data into training and validation sets 
    (the test set is already provided in data/test_data.csv)
    
    We ommit y-labels as we use autoregression only and no external regressors

    """

    print('Splitting data ...')
    # Define cut off
    cut_off_percentage = 0.8
    cut_off = int(cut_off_percentage*len(df))

    # Split data set
    X_train = df[:cut_off]
    X_val = df[cut_off:]

    X_val.to_csv('data/test_data.csv', index=False)
    
    y_train = df[:cut_off]
    y_val = df[cut_off:]
    
    return X_train, X_val, y_train, y_val

def train_model(X_train : pd.DataFrame, y_train : pd.DataFrame):

    """ 
    Method trains an ARMA (4,12) Model for green generation and load for each coutntry

    Input: Training data (pd.DataFrame)
    Returns: List of dictionaries containing the models
    
    """
    
    print('Training models ...')
    model = list()

    # Green energy generation dictionary
    # Key: country (str), Value: colum_name (str) 
    green_gen_dict = dict()
    
    # Load dictionary
    # Key: country (str), Value: colum_name (str) 
    load_dict = dict()

    # Model dictionaries
    # Key: country (str), Value: ARMA(4,12) (Model) 
    model_gen_training_dict = dict()
    model_load_training_dict = dict()
    
    country_labels = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']
    
    find_best_lags_bool = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # If needed ... Find best lags for each country

    if (find_best_lags_bool == True) :
            
        p_vals = range(3,6)
        q_vals = range(3,6)

        all_res = []
        for idx, data_name in enumerate(relevant_cols) :

            print('= '*30)
            print(f"start {data_name} {idx+1}/{len(relevant_cols)}")

            # demean data
            mean = df_green_surplus[data_name].mean()
            data = df_green_surplus[data_name] - mean
            # set frequency to hourly
            data = data.asfreq('H')

            # Create dataframe to store results
            results = []

            # Loop through p and q values
            for p_val in p_vals:
                for q_val in q_vals:

                    print(f"p={p_val}, q={q_val}")

                    try:
                        # Fit ARIMA model
                        order = (p_val, 0, q_val)
                        model = ARIMA(data, order=order)
                        fit_model = model.fit(low_memory=True)

                        # Get BIC and AIC values
                        bic = fit_model.bic
                        aic = fit_model.aic

                        # Save results in the dataframe
                        results.append({'country' : data_name, 'mean' : mean,
                                        'p': p_val, 'q': q_val, 
                                        'BIC': bic, 'AIC': aic, 'IC_comb' : bic+aic})

                    except Exception as e:
                        print(f"An error occurred: {e}")

            results_df = pd.DataFrame(results)
            print(results_df)

            # Find the best p and q based on lowest combined AIC and BIC
            best_params = results_df.loc[results_df['IC_comb'].idxmin()]
            print('-'*30)
            print(f"Best p = {best_params['p']}, best q = {best_params['q']}")
            print('-'*30)

            # save best params p and q in dataframe for each loop iteration
            all_res.append(best_params)

        all_res_df = pd.DataFrame(all_res)
        
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # Take given lag order to reduce computation time
    lag_order = (4,0,12)

    # Model Training and initialization
    for idx, country in enumerate(country_labels):

        print(f"{idx+1}/{len(country_labels)} ... {country} start", end='')
        green_gen_dict[country] = "green_energy_" + country
        load_dict[country] = country + "_load"
    
        # Train models based on X_train
        model_gen_training_dict[country] = sm.tsa.SARIMAX(X_train[green_gen_dict[country]], order=lag_order).fit(disp=False)
        model_load_training_dict[country] = sm.tsa.SARIMAX(X_train[load_dict[country]], order=lag_order).fit(disp=False)
        print(f"... training done")
    
    model = [model_gen_training_dict, model_load_training_dict]
    
    return model

def save_model(model, model_path):

    """
    Save the trained model to the specified model_path
    """

    with open(model_path, 'wb') as file:
        pickle.dump(model, file)

    print(f"models have been saved in .pkl file")

    return

def parse_arguments():

    parser = argparse.ArgumentParser(description='Model training script for Energy Forecasting Hackathon')

    parser.add_argument(
        '--input_file', 
        type=str, 
        default='data/processed_data.csv', 
        help='Path to the processed data file to train the model'
    )

    parser.add_argument(
        '--model_file', 
        type=str, 
        default='models/model.pkl', 
        help='Path to save the trained model'
    )
    return parser.parse_args()

def main(input_file, model_file):

    df = load_data(input_file)
    X_train, X_val, y_train, y_val = split_data(df)
    model = train_model(X_train, y_train)
    save_model(model, model_file)

if __name__ == "__main__":

    args = parse_arguments()
    main(args.input_file, args.model_file)