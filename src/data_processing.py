import argparse
import pandas as pd
import os

# regions = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']

regions = {
    'HU': '10YHU-MAVIR----U',
    'IT': '10YIT-GRTN-----B',
    'PO': '10YPL-AREA-----S',
    'SP': '10YES-REE------0',
    'UK': '10Y1001A1001A92E',
    'DE': '10Y1001A1001A83F',
    'DK': '10Y1001A1001A65H',
    'SE': '10YSE-1--------K',
    'NE': '10YNL----------L',
}

reversed_regions = {v: k for k, v in regions.items()}

# UK double values in generation due to 2 columns : Actual Aggregated, Actual Consumption
# Also no load data for UK since ca. 2019

def load_data(file_path) -> dict:

    """
    loads data from file_path 
    """

    os.chdir(file_path)
    # Lists all csv files that begin with "load" or "gen"
    csv_files_list = [file for file in os.listdir(file_path) 
                      if (file.endswith(".csv") and (file.startswith("load") or file.startswith("gen")))]

    df_dict = {}

    # get data
    for csv_file in csv_files_list :
        df_temp = pd.read_csv(csv_file)

        dict_key = csv_file.replace(".csv", "")
        df_dict[dict_key] = df_temp

    os.chdir("./")

    return df_dict

def clean_data(df_dict) -> dict:

    """ 
    Handles missing values, outliers, etc. 
    """

    df_dict_clean = {}

    for df_name, df in df_dict.items(): 

        if (df.empty) :
            print('-'*15)
            print(f'{df_name} is empty')
            print('-'*15)
            continue

        df['timestamp'] = df['StartTime'].astype('string')
        df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%dT%H:%M%zZ")
        df.set_index('timestamp', inplace=True)

        start = pd.to_datetime(df.index.min())
        end = pd.to_datetime(df.index.max())

        interval_in_min = round(((end - start) / df.shape[0]).seconds / 60)
        dates = pd.date_range(start=start, end=end, freq=f'{interval_in_min} Min')

        df_reindexed = df.reindex(dates)
        df_clean = df_reindexed.interpolate(method='linear')

        df_dict_clean[df_name] = df_clean

    return df_dict_clean

def preprocess_data(df_dict):
    
    """ 
    Generates new features, transform existing features, resampling & aggregate, etc. 
    """

    df_processed = pd.DataFrame()

    for df_name, df in df_dict.items(): 

        if (df.empty) :
            print('-'*15)
            print(f'{df_name} is empty')
            print('-'*15)
            continue

        AreaID = df['AreaID'][0]
        country = reversed_regions[AreaID]
        # country = df_name.str.split('_').str.get(1)

        UnitName = df['UnitName'][0]
        
        if df_name.startswith('load') : pwr_type = 'load'
        else : pwr_type = PsrType = df['PsrType'][0]

        # Resample to hourly level and sum
        df_resampled = df.resample("1h", label="left").sum()

        new_name = f"{country}_{UnitName}_{pwr_type}"
        print(new_name)

        df_resampled.rename(columns={'quantity': new_name}, inplace=True)

        df_processed = pd.concat([df_processed, df_resampled], axis=1)

    return df_processed

def save_data(df, output_file):

    """ 
    Generates new features, transform existing features, resampling & aggregate, etc. 
    """

    # TODO: better name including dates
    df.to_csv(f'{output_file}/all_data.csv', index=False)

    return

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

    print(f"cwd = {os.getcwd()}")
    print(list_csv_files("./data"))
    # df_dict = load_data("./data")
    # df_dict_clean = clean_data(df_dict)
    # df_prepro = preprocess_data(df_dict)
    # print(df_prepro)

#     # args = parse_arguments()
#     # main(args.input_file, args.output_file)