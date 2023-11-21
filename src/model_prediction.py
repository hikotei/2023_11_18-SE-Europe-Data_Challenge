import pandas as pd
import argparse
import pickle
import statsmodels.api as sm

def load_data(file_path):

    # Load test data from CSV file
    df = pd.read_csv(file_path)

    return df

def load_model(model_path):
    # Load the trained model

    with open(model_path,'rb') as f:
        model =pickle.load(f)

    return model

def make_predictions(df, model):

    # Use the model to make predictions on the test data
    
    green_gen_dict = dict()
    load_dict = dict()
    
    model_gen_training_dict = model[0]
    model_load_training_dict = model[1]
    
    model_gen_test_dict = model[0]
    model_load_test_dict = model[1]

    surplus_pred_df = pd.DataFrame()

    country_labels = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']

    
    country_codes_dict = {'SP': 0, 'UK': 1, 'DE': 2, 'DK': 3, 'SE': 4, 'HU': 5, 'IT': 6, 'PO': 7, 'NL': 8}

    # Model Training and initialization
    for country in country_labels:

        green_gen_dict[country] = "green_energy_" + country
        load_dict[country] = country + "_load"

        model_gen_test_dict[country] = sm.tsa.SARIMAX(df[green_gen_dict[country]], order=(4,0,12)).filter(model_gen_training_dict[country].params)
        model_load_test_dict[country] = sm.tsa.SARIMAX(df[load_dict[country]], order=(4,0,12)).filter(model_load_training_dict[country].params)
    
        surplus_pred_df[country] = model_gen_test_dict[country].predict() - model_load_test_dict[country].predict()

    # lots of data missing from UK, so drop it
    surplus_pred_df = surplus_pred_df.drop('UK',axis=1)

    print(surplus_pred_df.head())
    surplus_pred_df["Max"]=surplus_pred_df.idxmax(axis=1)
    predictions = surplus_pred_df["Max"].map(country_codes_dict)

    return predictions

def save_predictions(predictions, predictions_file):

    # Save predictions to a JSON file
    res_df = pd.DataFrame({'target' : predictions})
    res_df.to_json(predictions_file)

    pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='Prediction script for Energy Forecasting Hackathon')
    parser.add_argument(
        '--input_file', 
        type=str, 
        default='./data/test_data.csv', 
        help='Path to the test data file to make predictions'
    )
    parser.add_argument(
        '--model_file', 
        type=str, 
        default='models/model.pkl',
        help='Path to the trained model file'
    )
    parser.add_argument(
        '--output_file', 
        type=str, 
        default='predictions/predictions.json', 
        help='Path to save the predictions'
    )
    return parser.parse_args()

def main(input_file, model_file, output_file):
    df = load_data(input_file)
    model = load_model(model_file)
    predictions = make_predictions(df, model)
    save_predictions(predictions, output_file)

if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_file, args.model_file, args.output_file)
