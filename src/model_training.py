import pandas as pd

import matplotlib.pyplot as plt
import pyflux as pf

import argparse

file_path = "./data/gen_DE_B02.csv"

def load_data(file_path):

    df_main = pd.read_csv(file_path)
    df_main.set_index('timestamp', inplace=True)
    df_main.index = pd.to_datetime(df_main.index)
    df_main = df_main.asfreq('H')

    return df

def split_data(df):

    # Define split time as 80% of the data set
    split_stamp = df.index[int(len(df)*0.8)]

    # Split data set into features (X) and target variable (y)
    X_train = df[df.index <= split_stamp].drop(columns=['max_surplus_country_code_next_hr'])
    X_test = df[df.index > split_stamp].drop(columns=['max_surplus_country_code_next_hr'])

    y_train = df[df.index <= split_stamp]['max_surplus_country_code_next_hr']
    y_test = df[df.index > split_stamp]['max_surplus_country_code_next_hr']

    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):

    relevant_countries = ['DK', 'UK', 'SE', 'DE']
    relevant_cols = [col for col in X_train.columns if ('green_surplus' in col and col.split('_')[0] in relevant_countries)]
    df_green_surplus= X_train[relevant_cols]

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

        res_order_df = pd.DataFrame(all_res)

    else : # resort to historic best lags from test phase

        data = {
        'country': ['DE_green_surplus_MAW', 'SE_green_surplus_MAW', 'DK_green_surplus_MAW', 'UK_green_surplus_MAW'],
        'p': [3, 5, 5, 5],
        'q': [5, 3, 4, 4]
    }

    res_order_df = pd.DataFrame(data)

    return res_order_df


def validate_model(res_order_df):
    # TODO: Validate model based on F1 Score

    model_dict = {}
    df_forecast = pd.DataFrame()
    h = 24

    for data_name in relevant_cols :

        # demean data
        mean = df_green_surplus[data_name].mean()
        data = df_green_surplus[data_name] - mean
        # set frequency to hourly
        data = data.asfreq('H')
        
        res_row = all_res_df[all_res_df['country'] == data_name]
        order = (res_row['p'], 0, res_row['q'])

        final_model = ARIMA(data, order=order)
        final_fit = final_model.fit()
        model_dict[data_name] = final_fit

        # In-sample predictions
        predictions = final_fit.predict()

        # Make forecast for next h hours
        forecast = model_dict[data_name].forecast(steps=h)

        # Add forecast + mean to df_forecast
        mean = df_green_surplus[data_name].mean()
        df_forecast[data_name] = forecast + mean
        
        # Plot the original data, in sample predictions, and fcast
        plt.figure(figsize=(20, 5))

        plt.plot(data, label='Actual Data')
        plt.plot(predictions, label='In-sample Predictions', color='red', lw=1, linestyle='--', alpha=0.5)
        plt.plot(forecast, label='Forecast', color='green', lw=2, linestyle='-')

        plt.title(f"{data_name} - ARMA({order}) In-sample Predictions")
        plt.legend()
        plt.show()

    # calculate which fcast is highest and put in column 'max_surplus_country_name'
    df_forecast['max_surplus_country_name'] = df_forecast.apply(lambda row: max(relevant_countries, key=lambda country: row[f"{country}_green_surplus_MAW"]), axis=1)

    return


def save_model(model, model_path):
    # TODO: Save your trained model
    pass

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
    
    #print(pd.to_datetime(time))
    #year,month,day,hour,minunte,na_1,na_2 = time.replace("T","-").replace(":","-").replace("+","-").split("-")
    #print(string_parts)

    #pd.to_datetime(time,"yyyy-mm-dd")
    df = load_data(file_path)
    X_train, X_val, y_train, y_val = split_data(df)
    train_model(X_train,y_train)

    #args = parse_arguments()
    #main(args.input_file, args.model_file)