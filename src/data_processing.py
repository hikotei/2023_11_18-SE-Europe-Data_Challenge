import argparse
import pandas as pd
import os

regions = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']

def list_csv_files(directory):
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
    return csv_files


def load_data(file_path):
    # TODO: Load data from CSV file

    csv_files_list = list_csv_files(file_path)

    # df_all = pd.dataframe()
    df_list = []

    os.chdir(file_path)

    # get data
    for csv_file in csv_files_list :
        df_temp = pd.read_csv(csv_file)
        df_list.append(df_temp)

    os.chdir("./")

    return df_list

def clean_data(df):
    # TODO: Handle missing values, outliers, etc.

    return df_clean

def preprocess_data(df):
    # TODO: Generate new features, transform existing features, resampling, etc.

    return df_processed

def save_data(df, output_file):
    # TODO: Save processed data to a CSV file
    pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='Data processing script for Energy Forecasting Hackathon')
    parser.add_argument(
        '--input_file',
        type=str,
        default='data/raw_data.csv',
        help='Path to the raw data file to process'
    )
    parser.add_argument(
        '--output_file', 
        type=str, 
        default='data/processed_data.csv', 
        help='Path to save the processed data'
    )
    return parser.parse_args()

def main(input_file, output_file):
    df = load_data(input_file)
    df_clean = clean_data(df)
    df_processed = preprocess_data(df_clean)
    save_data(df_processed, output_file)

if __name__ == "__main__":

    # print(list_csv_files("./data"))
    # print(load_data("./data"))

    # args = parse_arguments()
    # main(args.input_file, args.output_file)