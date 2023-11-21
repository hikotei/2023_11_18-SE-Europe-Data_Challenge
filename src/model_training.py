import pandas as pd
import statsmodels.api as sm
import argparse
import pickle


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
    
    We ommit y-lables as we use autoregression only and no external regressors

    """

    # Define cut off
    cut_off_percentage = 0.8
    cut_off = int(cut_off_percentage*len(df))

    # Split data set
    X_train = df[:cut_off]
    X_val = df[cut_off:]
    y_train = df[:cut_off]
    y_val = df[cut_off:]
    
    return X_train, X_val, y_train, y_val

def train_model(X_train : pd.DataFrame, y_train : pd.DataFrame):
    """ 
    Method trains an ARMA (4,12) Model for green generation and load for each coutntry

    Input: Training data (pd.DataFrame)
    Returns: List of dictionaries containing the models
    
    """
    
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

    # Model Training and initialization
    for country in country_labels:
        
        green_gen_dict[country] = country + "_green_MAW"
        load_dict[country] = country + "_load_MAW"
    
        # Train models based on X_train
        model_gen_training_dict[country] = sm.tsa.SARIMAX(X_train[green_gen_dict[country]], order=(4,0,12)).fit()
        model_load_training_dict[country] = sm.tsa.SARIMAX(X_train[load_dict[country]], order=(4,0,12)).fit()

        print(country+" has been trained successfully")
    
    model = [model_gen_training_dict,model_load_training_dict]
    
    return model

def save_model(model, model_path):
    # TODO: Save your trained model
    pickle.dump(model,model_path)
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

    args = parse_arguments()
    main(args.input_file, args.model_file)