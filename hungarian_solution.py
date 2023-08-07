import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
from utilities import calculation_cost
from tqdm import tqdm

#GLOBAL VARIABLES
NUMBER_OF_OPEN_DAYS_3_MONTHS = 66
NUMBER_OF_OPEN_DAYS_3_WEEKS = 15
NUMBER_OF_OPEN_DAYS_YEAR = 260
WORKER_TO_PICK = 10000
WORKER_TO_REPLENISH = 0.05
LOCATION_TO_REPLENISH = 0.8

#COEF for cost importance
PICKING_COEF = 0.9
REPLENISHMENT_COEF = 112.5
COEF_WEIGHT = 100




def cost_matrix(result_df,df_loc_available,df_loc,Weight_switch):
    location_df_cpy = df_loc_available.copy()
    product_df = result_df.copy()
    
    product_df[['MaxLl_p','MinLl_p']] = product_df[['LONG','LARG']].agg(['max','min'],axis=1)
    location_df_cpy[['MaxLl_l','MinLl_l']] = location_df_cpy[['LONGUEUR','LARGEUR']].agg(['max','min'],axis=1)

    picking_cost_matrix = np.full((len(product_df), len(df_loc)), np.inf)
    replenishment_cost_matrix = np.full((len(product_df), len(df_loc)), np.inf)
    
    gare_list_heavy = ['GARE01', 'GARE02', 'GARE03', 'GARE04', 'GARE05', 'GARENN']
    gare_list_light = ['GARE20','GARE21','GARE22','GARE23','GARE24']

    location_volume = location_df_cpy['Volume_Location']*location_df_cpy['RATIO']
    location_dim_ratio = location_df_cpy['dim_ratio']
    location_dim_max = location_dim_ratio*location_df_cpy['MaxLl_l']
    location_dim_min = location_dim_ratio*location_df_cpy['MinLl_l']
    location_dim_haut = location_dim_ratio*location_df_cpy['HAUTEUR']
    location_gare = location_df_cpy['ID_GARE']
    location_level = pd.to_numeric(location_df_cpy['LIB_NIVEAU'])
    location_cout = location_df_cpy['COUT_EMPL']

    for i, product in tqdm(product_df.iterrows(), total=len(product_df)):
        product_volume = product['Volume_Product']
        product_dim_max = product['MaxLl_p']
        product_dim_min = product['MinLl_p']
        product_haut = product['HAUT']
        product_poid = product['POIDS']
        product_nr_lines = product['Number_Lines']

        condition = ((location_volume >= product_volume) & 
                    (location_dim_haut >= product_haut) &
                    (location_dim_max >= product_dim_max) & 
                    (location_dim_min >= product_dim_min))

        loc_index = location_df_cpy[condition].index.tolist()
        if not loc_index:
            continue
        for j in loc_index:

            if (((product['Familly']=='Heavy') & (location_gare[j] not in gare_list_heavy) & ((location_level[j]<5)|(location_level[j]>35))) |
                ((product['Familly']=='Fragile') & (location_gare[j] not in gare_list_light)) & Weight_switch):

                        picking_cost_matrix[i, j] = COEF_WEIGHT * product['Product_FREQUENCY'] * location_cout[j]
                        replenishment_cost_matrix[i, j] = COEF_WEIGHT * product['Average_Volume/Day'] / (location_volume[j]*LOCATION_TO_REPLENISH)

            else:

                picking_cost_matrix[i, j] = product['Product_FREQUENCY'] * location_cout[j]
                replenishment_cost_matrix[i, j] = product['Average_Volume/Day'] / (location_volume[j]*LOCATION_TO_REPLENISH)
    return  picking_cost_matrix, replenishment_cost_matrix


def optimal_assignment(product_df,location_df,total_cost_matrix):
    #row_ind indicate the location index 
    #col_ind indicate the location index
    row_ind, col_ind = linear_sum_assignment(total_cost_matrix)
    #optimal assignment
    
    opt_ass = col_ind


    assigned_locations_df = pd.DataFrame(columns=['ID_Product','PREP','CODE_BARRE'])

    for i, code in enumerate(opt_ass):

        assigned_locations_df.loc[i]=[product_df.loc[i,'ID_Product'],product_df.loc[i,'PREP'],location_df.loc[code,'CODE_BARRE']]


    
    #final dataframe solution
    assigned_locations_df = pd.merge(assigned_locations_df, product_df, on=['ID_Product','PREP'])
    assigned_locations_df = pd.merge(assigned_locations_df, location_df, on=['CODE_BARRE'])
    assigned_locations_df['Quantity_Location'] = np.where(assigned_locations_df['HAUT']!=0,np.floor((assigned_locations_df['Volume_Location']*assigned_locations_df['RATIO']) / assigned_locations_df['Volume_Product']),np.floor(((assigned_locations_df['Volume_Location']*assigned_locations_df['RATIO'])/ (assigned_locations_df['LONG']*assigned_locations_df['LARG']))))
    df_all_assigned, solution_picking_cost,solution_replenishment_cost,nb_picking_workers,nb_replenishment_workers = calculation_cost(assigned_locations_df)
    

    return df_all_assigned

def assign_product_location(reassign_products,initial_solution,df_loc,Weight_switch):
     #assignment with balanced ratio coef

    #calculate the total_cost_matrix for the % of products to reassign
    picking_cost_matrix_1, replenishment_cost_matrix_1 = cost_matrix(reassign_products,df_loc,df_loc,Weight_switch)
    total_cost_matrix_1 = PICKING_COEF * picking_cost_matrix_1 + REPLENISHMENT_COEF * replenishment_cost_matrix_1
    #calculate the optimal solution for this product considering that all locations of the warehouse are avilable for them
    df_assigned_1 = optimal_assignment(reassign_products,df_loc,total_cost_matrix_1)
    #copy of initial solution
    new_initial_solution = initial_solution.copy()
        
    #checking for the clashes
    #merge the % of products assigned with initial solution
    df_res = pd.merge(df_assigned_1,new_initial_solution, on='CODE_BARRE')
    #filter all locations that have 2 products assigned in them
    df_filtered = df_res[df_res['ID_Product_x'] != df_res['ID_Product_y']]
    #check if there is no locations with 2 products assigned in it then we have no clashes
    if not (df_filtered.empty or (df_filtered['ID_Product_x']==df_filtered['ID_Product_y']).all() or (len(initial_solution)==len(reassign_products))):

        #select all the records of the initial solution product clashed with the reassigned product
        common_ids = np.unique(df_filtered['ID_Product_x'].tolist() + df_filtered['ID_Product_y'].tolist())
        df_clashed = initial_solution[initial_solution['ID_Product'].isin(common_ids)][['ID_Product','CODE_BARRE']]

        #add together all the id of products I choosed to reassign and the product clashed with during reassignment
        unique_ids = np.unique(reassign_products['ID_Product'].tolist() + df_clashed['ID_Product'].tolist())
        #declaring the new set of reassignment = % choosen + products from inital that clashed
        df_new_reassign = initial_solution[initial_solution['ID_Product'].isin(unique_ids)].reset_index()
        df_new_reassign = df_new_reassign[['ID_Product','PREP','LONG','LARG','HAUT','Volume_Product','Number_Lines','Product_FREQUENCY','Quantity_demand','Average_Volume/Day','POIDS','Familly']]                               
        #preparing all locations avialble (locations choosen by the reassignment, initial locations of the product befare the reassignment,and all other avilable locations not occupied by the inital solution)
        common_code_barre = np.unique(df_assigned_1['CODE_BARRE'].tolist() + df_clashed['CODE_BARRE'].tolist() + df_loc[~df_loc['CODE_BARRE'].isin(initial_solution['CODE_BARRE'])]['CODE_BARRE'].tolist())
        df_loc_available = df_loc[df_loc['CODE_BARRE'].isin(common_code_barre)]

        #calculate the total_cost_matrix for the new set of reassignment
        picking_cost_matrix_1_final, replenishment_cost_matrix_1_final = cost_matrix(df_new_reassign,df_loc_available,df_loc,Weight_switch)
        total_cost_matrix_1_final = PICKING_COEF * picking_cost_matrix_1_final + REPLENISHMENT_COEF * replenishment_cost_matrix_1_final
        #calculate the optimal solution for the new set of reassignment
        df_assigned_1 = optimal_assignment(df_new_reassign,df_loc_available,total_cost_matrix_1_final)

    #remove from the initial solution all products assigned
    new_initial_solution = initial_solution[~initial_solution['ID_Product'].isin(df_assigned_1['ID_Product'])]



    #Final Solution
    new_initial_solution = new_initial_solution[['ID_Product','CODE_BARRE','Product_FREQUENCY','Quantity_demand','LONG','LARG','HAUT','Volume_Product','Average_Volume/Day','PREP','Number_Lines','LONGUEUR','LARGEUR','HAUTEUR','COUT_EMPL','Volume_Location','TYPE','RATIO','Quantity_Location','Replenishment_Cost','Picking_Cost','Nb_Picking_Workers','Nb_Replenishment_Workers','ID_GARE']]
    df_assigned_1 = df_assigned_1[['ID_Product','CODE_BARRE','Product_FREQUENCY','Quantity_demand','LONG','LARG','HAUT','Volume_Product','Average_Volume/Day','PREP','Number_Lines','LONGUEUR','LARGEUR','HAUTEUR','COUT_EMPL','Volume_Location','TYPE','RATIO','Quantity_Location','Replenishment_Cost','Picking_Cost','Nb_Picking_Workers','Nb_Replenishment_Workers','ID_GARE']]
    df_final_result_1 = pd.concat([new_initial_solution,df_assigned_1]).reset_index()

    TOTAL_Picking_Cost_1 = np.sum(df_final_result_1['Picking_Cost'])
    TOTAL_Replenishment_Cost_1 = np.sum(df_final_result_1['Replenishment_Cost'])

    return df_final_result_1, TOTAL_Picking_Cost_1, TOTAL_Replenishment_Cost_1
