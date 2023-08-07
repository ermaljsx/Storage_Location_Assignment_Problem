import numpy as np
import pandas as pd
from utilities import load_dataframes, save_dataframe, calculation_cost
from hungarian_solution import assign_product_location






def initial_processing(result_df,df_initial,df_loc):
    #analysed data
    df_initial = pd.merge(df_initial, result_df, on=['ID_Product','PREP'], how='left')
    #merge with locations data-frame
    df_initial = pd.merge(df_initial,df_loc, on=['CODE_BARRE','ID_GARE'] , how='left')
    #initialize quantity of the product that can be placed in the location
    df_initial['Quantity_Location'] = np.where(df_initial['Volume_Product']!=0 ,np.floor((df_initial['Volume_Location']*df_initial['RATIO']) / df_initial['Volume_Product']),np.floor((df_initial['Volume_Location']*df_initial['RATIO']) / (df_initial['LONG']*df_initial['LARG'])))
    #calculate the costs
    df_initial_solution,initial_solution_picking_cost,initial_solution_replenishment_cost,initial_nb_picking_workers,initial_nb_replenishment_workers = calculation_cost(df_initial)

    return df_initial_solution,initial_solution_picking_cost,initial_solution_replenishment_cost

def reassign_selection(df_initial_result,PERCENTAGE_REASSIGN):
    # Select the top % of products with the worst total cost
    df_initial_result['total_cost']=0.9*df_initial_result['Picking_Cost'] + 112.5 * df_initial_result['Replenishment_Cost']
    sorted_products = df_initial_result.sort_values('total_cost',ascending=False)
    num_products = len(sorted_products)
    num_products_to_reassign = int(num_products * PERCENTAGE_REASSIGN)
    reassign_products = sorted_products.iloc[:num_products_to_reassign]
    reassign_products = reassign_products[['ID_Product','PREP','LONG','LARG','HAUT','Volume_Product','Number_Lines','Product_FREQUENCY','Quantity_demand','Average_Volume/Day','POIDS','Familly']].reset_index(drop=True)                               
    
    return reassign_products


def final_comparisson(final_picking_cost,final_replenishment_cost,initial_picking_cost,initial_replenishment_cost):

    comp_dictionary = {'Solutions':['Our Solution','Initial'],'Total Picking Cost':[final_picking_cost,initial_picking_cost], 'Total Replenishment Cost':[final_replenishment_cost,initial_replenishment_cost], 'Weighted_Sum':[final_picking_cost+final_replenishment_cost,initial_picking_cost+initial_replenishment_cost]}
    comp_df = pd.DataFrame(comp_dictionary)
    return comp_df





def reassign_products(
    products_path= r'data\result_df.csv',
    initial_result_path= r'data\initial_result.csv',
    locations_path= r'data\emplacements.csv',
    PERCENTAGE_REASSIGN=100,
    Weight_switch=True
):
    PERCENTAGE_REASSIGN = PERCENTAGE_REASSIGN/200
    #load dataframes
    result_df,df_initial,df_loc = load_dataframes(products_path, initial_result_path, locations_path)

    df_initial_solution,initial_solution_picking_cost,initial_solution_replenishment_cost = initial_processing(result_df,df_initial,df_loc)

    reassign_df = reassign_selection(df_initial_solution,PERCENTAGE_REASSIGN)

    df_final_solution,final_picking_cost,final_replenishment_cost = assign_product_location(reassign_df,df_initial_solution,df_loc,Weight_switch)
    
    comp_df = final_comparisson(final_picking_cost,final_replenishment_cost,initial_solution_picking_cost,initial_solution_replenishment_cost)
    save_dataframe(df_final_solution,'final_solution')
    save_dataframe(comp_df,'comparisson')