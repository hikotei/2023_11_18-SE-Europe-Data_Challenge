import pandas as pd

import matplotlib.pyplot as plt
import pyflux as pf


import argparse

file_path = "./data/gen_DE_B02.csv"




def load_data(file_path):
    # TODO: Load processed data from CSV file

    df = pd.read_csv(file_path)

    df['timestamp'] = df['StartTime'].astype('string')
    df['timestamp'] = df['timestamp'].str.replace('T', ' ')
    df['timestamp'] = df['timestamp'].str.replace('Z', '')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d %H:%M%z")

    return df

def split_data(df):
    # TODO: Split data into training and validation sets (the test set is already provided in data/test_data.csv)
    
    # Define split time
    split_stamp = pd.Timestamp(year=2023, month=1, day=1, hour=22,tz="Europe/Berlin")
    
    # Split data set
    X_train = df[df.timestamp <= split_stamp]
    X_val = df[df.timestamp > split_stamp]
    y_train = df[df.timestamp <= split_stamp]
    y_val = df[df.timestamp > split_stamp]

    return X_train, X_val, y_train, y_val

def train_model(X_train, y_train):
    # TODO: Initialize your model and train it
    #pf.acf_plot(X_train.quantity)
    #plt.plot(X_train.quantity)
    #plt.show()
    #plt.plot(X_train.quantity.diff())
    #plt.show()
    #pf.acf_plot(X_train.quantity.diff())
    
    model = pf.ARIMA(data=X_train, ar=4, ma=4, target='quantity', family=pf.Normal())
    x = model.fit("MLE")
    x.summary()
    #model.plot_fit(figsize=(15,5))
    model.plot_predict(h=20,past_values=20,figsize=(15,5))
    pass
    #return model


def validate_model():
    # TODO: Validate model based on F1 Score

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