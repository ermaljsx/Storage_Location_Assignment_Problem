import pandas as pd
import numpy as np
import os


#GLOBAL VARIABLES
NUMBER_OF_OPEN_DAYS_3_MONTHS = 66
NUMBER_OF_OPEN_DAYS_3_WEEKS = 15
NUMBER_OF_OPEN_DAYS_YEAR = 260
WORKER_TO_PICK = 10000
WORKER_TO_REPLENISH = 0.05
WEIGHT_PICK = 0.0001
WEIGHT_REPLENISH = 10000
LOCATION_TO_REPLENISH = 0.8

def save_dataframe(df, filename):
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data')
    
    # Create 'data' directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    path = os.path.join(data_dir, f'{filename}.csv')
    df.to_csv(path, index=False)


def load_dataframes(products_path, initial_solution_path, locations_path):
    result_df = pd.read_csv(products_path)
    initial_solution_df = pd.read_csv(initial_solution_path)
    # read location dataframe
    df_loc=pd.read_csv(locations_path,usecols=['CODE_BARRE','LONGUEUR','LARGEUR','HAUTEUR','LIB_NIVEAU','COUT_EMPL','ID_GARE','Volume_Location','TYPE'])
    #Ratio to determine useful volume based on the type of location
    df_loc['RATIO'] = np.where(df_loc['TYPE'].str.contains('palette', case=False), 1, 0.75)
    df_loc['dim_ratio'] = np.where(df_loc['RATIO']==0.75, df_loc['RATIO']**(1/3), 1)
    
    return result_df, initial_solution_df, df_loc



def calculation_cost(df_all_assigned_product):
    
    df_assigned = df_all_assigned_product.copy()

    # Calculate replenishment cost
    df_assigned['Replenishment_Cost'] = df_assigned['Average_Volume/Day'] / (df_assigned['Volume_Location']*df_assigned['RATIO']*LOCATION_TO_REPLENISH)

    # Calculate picking cost 
    df_assigned['Picking_Cost'] = df_assigned['Product_FREQUENCY'] * df_assigned['COUT_EMPL']
    
    #Calculate the number of workesers
    df_assigned['Nb_Picking_Workers'] = df_assigned['Picking_Cost'] / WORKER_TO_PICK
    df_assigned['Nb_Replenishment_Workers'] = df_assigned['Replenishment_Cost'] / WORKER_TO_REPLENISH
    
    # Calculate solution costs and number of workers
    solution_picking_cost = df_assigned['Picking_Cost'].sum()
    solution_replenishment_cost = df_assigned['Replenishment_Cost'].sum()
    nb_picking_workers = df_assigned['Nb_Picking_Workers'].sum()
    nb_replenishment_workers = df_assigned['Nb_Replenishment_Workers'].sum()

    return df_assigned, solution_picking_cost, solution_replenishment_cost, nb_picking_workers, nb_replenishment_workers