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

def train_model(X_train, y_train,p,q):
    # TODO: Initialize your model and train it

    model = pf.ARIMA(data=X_train, integ=0 ,ar=p, ma=q, target='quantity', family=pf.Normal())
    x = model.fit("MLE")
    x.summary()
    return model

def validate_model(model,X_val,y_val):
    score = abs(model.predict(h=1)-X_val)
    return score

if __name__ == "__main__":

    # Max ARIMA Coefficients
    p_max=5
    q_max=5

    df = load_data(file_path)
    X_train, X_val, y_train, y_val = split_data(df)
        

    for p in range(0,p_max):
        for q in range(0,q_max):
            model = train_model(X_train,y_train,p=p,q=q)
            score = validate_model()





