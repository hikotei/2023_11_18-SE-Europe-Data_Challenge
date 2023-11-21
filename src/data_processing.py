import argparse
import pandas as pd
import os
from typing import Dict, List

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PROBLEMS !!!
# UK generation data receives 2 columns : Actual Aggregated, Actual Consumption on request
# -> Actual Aggregated values are taken for UK and Actual Consumption values are removed
# -> There is also a large gap in the middle of the year for UK green energy generation
# -> Also no load data for UK in second half of year so we canntot calculate green surplus
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  Defining Params

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

# dictionary to map country codes to labels
country_codes_dict = {'SP': 0, 'UK': 1, 'DE': 2, 'DK': 3, 'SE': 4, 'HU': 5, 'IT': 6, 'PO': 7, 'NL': 8}
country_labels = ['HU', 'IT', 'PO', 'SP', 'UK', 'DE', 'DK', 'SE', 'NE']

# List of generated energy types that are classified as GREEN to be used in calculation of surplus green energy production per country
green_energy_types_list = ["B01", "B09", "B10", "B11", "B12", "B13", "B15", "B16", "B18", "B19"]

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def load_data(file_path: str) -> dict:

    """
    Load data from the specified file_path.
    
    Parameters:
    - file_path (str): Path to the directory containing CSV files.
    
    Returns:
    - dict: A dictionary where keys are file names without the extension and values are DataFrames.
    """

    # Lists all CSV files that begin with "load" or "gen"
    csv_files_list = [file for file in os.listdir(file_path) if file.endswith(".csv") and (file.startswith("load") or file.startswith("gen"))]

    df_dict = {}

    # Get data
    wd = os.getcwd()
    os.chdir(file_path)

    for csv_file in csv_files_list:
        df_temp = pd.read_csv(csv_file)

        dict_key = csv_file.replace(".csv", "")
        df_dict[dict_key] = df_temp

    os.chdir(wd)

    return df_dict

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def clean_data(df_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:

    """
    Clean and preprocess dataframes in df_dict by handling missing values.
    
    - The 'StartTime' column is converted to a timestamp index.
    - Data is reindexed to an hourly level.
    - Linear interpolation is applied to fill missing values.

    Parameters:
    - df_dict (Dict[str, pd.DataFrame]): A dictionary containing DataFrame objects to be cleaned.

    Returns:
    - Dict[str, pd.DataFrame]: A dictionary where keys are the names of DataFrames, and values are cleaned DataFrames.
    """

    df_dict_clean = {}

    for df_name, df in df_dict.items():

        if df.empty:
            print('-' * 15)
            print(f'cleaning: {df_name} is empty')
            print('-' * 15)
            continue

        # Create a new timestamp index based on interval start time
        df['timestamp'] = df['StartTime'].astype('string')
        df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%dT%H:%M%zZ")
        df.set_index('timestamp', inplace=True)

        # Get start and end time of data
        start = pd.to_datetime(df.index.min())
        end = pd.to_datetime(df.index.max())

        # Estimate interval
        interval_in_data = round(((end - start) / df.shape[0]).seconds / 60)
        interval_estimated = min(15, 60, key=lambda x: abs(interval_in_data - x))
        dates = pd.date_range(start=start, end=end, freq=f'{interval_estimated} Min')

        # Reindex data based on the original interval, missing values get NaN
        df_reindexed = df.reindex(dates)

        # Interpolate data
        df_clean = df_reindexed.interpolate(method='linear')

        # Save to the output dict
        df_dict_clean[df_name] = df_clean

    return df_dict_clean


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def preprocess_data(df_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:

    """
    Preprocesses data by generating new features, resampling and aggregating.

    - For each country, power type, and unit, a new column is created with hourly aggregated values. (eg DE_load_MAW or DE_B01_MAW)
    - Green energy are created by summing values of given green energy types. (eg DE_green_MAW)
        ["B01", "B09", "B10", "B11", "B12", "B13", "B15", "B16", "B18", "B19"]
    - Green energy surplus is calculated as the difference between green energy production and load for each country. (eg DE_green_surplus_MAW)
    - new column with country name (eg 'DE') with highest surplus of green energy at each hour. (eg max_surplus_country_name)
    - new column with country code (eg 2) with highest surplus of green energy at each hour. (eg max_surplus_country_code)
    - new column with country code (eg 2) with highest surplus of green energy in next hour. (eg max_surplus_country_code_next_hr)
        this is also the target variable / label to be predicted


    Parameters:
    - df_dict (Dict[str, pd.DataFrame]): A dictionary containing DataFrame objects to be preprocessed.

    Returns:
    - pd.DataFrame: The preprocessed DataFrame.
    """

    df_processed = pd.DataFrame()
    country_list: List[str] = []

    print('start preprocessing')

    for df_name, df in df_dict.items():

        if df.empty:
            print('-' * 15)
            print(f'processing: {df_name} is empty')
            print('-' * 15)
            continue

        # All csv files (gen and load) have columns 'AreaID' and 'UnitName'
        UnitName = df['UnitName'][0]
        country = df_name.split('_')[1]  # Alternative
        # Add country to country_list if it's new
        if country not in country_list:
            country_list.append(country)

        # Determine whether it's a gen or load file
        if df_name.startswith('load'):
            pwr_type = 'load'
        else:
            pwr_type = df['PsrType'][0]

        # Resample (aggregate) to hourly level and sum
        df_resampled = df.resample("1h", label="left").sum()
        # Assign a new column name including country, power type, and unit information
        new_name = f"{country}_{pwr_type}"
        df_resampled.rename(columns={df_resampled.columns[0]: new_name}, inplace=True)

        # Concatenate to the output dataframe
        df_processed = pd.concat([df_processed, df_resampled], axis=1)

        if 'timestamp' not in df_processed.columns:
            print('add timestamp')
            df_processed['timestamp'] = df_resampled.index

    for country in country_list:
        # Take the sum over all green energies
        green_columns = [col for col in df_processed.columns
                         if col.startswith(f"{country}_")
                         and any(energy_type in col for energy_type in green_energy_types_list)]

        # Sum of green energies
        df_processed[f"green_energy_{country}"] = df_processed[green_columns].sum(axis=1)

        # Green energy surplus = difference between DE_green_energy and DE_load
        load_col = f"{country}_load"
        if (load_col in df_processed.columns) : load = df_processed[load_col]
        else : load = 0

        green_col = f"green_energy_{country}"
        if (green_col in df_processed.columns) : green_energy = df_processed[green_col]
        else : green_energy = 0

        df_processed[f"{country}_green_surplus"] = green_energy - load

    # Add column with the country that has the highest surplus of green energy at each hour
    df_processed['max_surplus_country_name'] = df_processed.apply(
        lambda row: max(country_list, key=lambda country: row[f"{country}_green_surplus"]), axis=1
    )

    # Map the country code based on the order defined in country_code_order
    df_processed['max_surplus_country_code'] = df_processed['max_surplus_country_name'].map(country_codes_dict)
    df_processed['max_surplus_country_code_next_hr'] = df_processed['max_surplus_country_code'].shift(-1)

    return df_processed

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def save_data(df: pd.DataFrame, output_file: str) -> None:

    """
    Save the DataFrame to a CSV file.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be saved.
    - output_file (str): The path to the output CSV file.

    Returns:
    - None
    """

    df.to_csv(output_file, index=False)

    return

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def parse_arguments():

    parser = argparse.ArgumentParser(description='Data processing script for Energy Forecasting Hackathon')

    parser.add_argument(
        '--input_dir',
        type=str,
        default='./data',
        help='Path to the raw data files to process'
    )

    parser.add_argument(
        '--output_file', 
        type=str, 
        default='data/processed_data.csv', 
        help='Path to save the processed data'
    )
    return parser.parse_args()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def main(input_dir, output_file):

    df_dict = load_data(input_dir)
    df_dict_clean = clean_data(df_dict)
    df_processed = preprocess_data(df_dict_clean)
    save_data(df_processed, output_file)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

if __name__ == "__main__":

    print(os.getcwd())
    args = parse_arguments()
    main(args.input_dir, args.output_file)
    print('done')