import argparse
import pandas as pd
import os

regions = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']

# UK double values in generation due to 2 columns : Actual Aggregated, Actual Consumption
# Also no load data for UK since ca. 2019

def list_csv_files(directory):
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
    return csv_files

def load_data(file_path):
    # TODO: Load data from CSV file
    csv_files_list = list_csv_files(file_path)

    # df_all = pd.dataframe()
    df_dict = {}

    os.chdir(file_path)

    # get data
    for csv_file in csv_files_list :
        df_temp = pd.read_csv(csv_file)

        dict_key = csv_file.replace(".csv", "")
        df_dict[dict_key] = df_temp

    os.chdir("./")

    return df_dict

def clean_data(df):
    # TODO: Handle missing values, outliers, etc.

    df['timestamp'] = df['StartTime'].astype('string')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%dT%H:%M%zZ")
    df.set_index('timestamp', inplace=True)

    start = pd.to_datetime(df.index.min())
    end = pd.to_datetime(df.index.max())

    interval_in_min = round(((end - start) / df.shape[0]).seconds / 60)
    dates = pd.date_range(start=start, end=end, freq=f'{interval_in_min} Min')

    df_reindexed = df.reindex(dates)
    df_clean = df_reindexed.interpolate(method='linear')

    return df_clean

def preprocess_data(df):
    # TODO: Generate new features, transform existing features, resampling & aggregate, etc.

    # aggregate to hourly level
    df.resample("1h", label="left").sum()

    df_processed = 

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

# if __name__ == "__main__":

#     # args = parse_arguments()
#     # main(args.input_file, args.output_file)