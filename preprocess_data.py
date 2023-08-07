import numpy as np
import pandas as pd
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
HEAVY_WEIGHT = 5000
LIGHT_WEIGHT = 200

def save_dataframe(df, filename):
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data')
    
    # Create 'data' directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    path = os.path.join(data_dir, f'{filename}.csv')
    df.to_csv(path, index=False)


def load_dataframes(products_path):
    result_df = pd.read_csv(products_path)
    return result_df


def update_df(product_df):
    product_df = product_df[['ID_Product', 'PREP','LONG', 'LARG', 'HAUT', 'QTE', 'Volume_Product', 'POIDS']]
    product_df['TYPE_OP'] = product_df['PREP']
    product_df['TYPE_OP'] = np.where(product_df['TYPE_OP']=='complet', 'COMPLET', 'UNIT')   
    return product_df

def calculations(sales_df):
    # extract the last 3 weeks of the year
    end_of_year = pd.to_datetime('2021-12-31')
    last_3_weeks = end_of_year - pd.DateOffset(weeks=3)
    # extract the last 3 months of the year
    last_3_months = end_of_year - pd.DateOffset(months=3)
    #set DATE_LIVRAISON as date format
    sales_df['DATE_LIVRAISON'] = sales_df['DATE_LIVRAISON'].replace(0, '01/01/2021')
    sales_df['DATE_LIVRAISON'] = pd.to_datetime(sales_df['DATE_LIVRAISON'], format='%d/%m/%Y').fillna(pd.to_datetime('01/01/2021', format='%d/%m/%Y'))

    #calculate numbr of lignes for full period
    sales_df['Number_Lines'] = sales_df[['ID_Product','TYPE_OP']].groupby(['ID_Product','TYPE_OP'])['ID_Product'].transform('count')
    #calculate numbr of lignes for last 3 Months (omly for frequency calculation)
    sales_df['Number_Lines_M'] = np.where(sales_df['DATE_LIVRAISON']>=last_3_months,sales_df[['ID_Product','TYPE_OP']].groupby(['ID_Product','TYPE_OP'])['ID_Product'].transform('count'),0)
    #calculate numbr of lignes for last 3 Weeks (omly for frequency calculation)
    sales_df['Number_Lines_W'] = np.where(sales_df['DATE_LIVRAISON']>=last_3_weeks,sales_df[['ID_Product','TYPE_OP']].groupby(['ID_Product','TYPE_OP'])['ID_Product'].transform('count'),0)
    #calculate Product Frequency for last 3 Months
    sales_df['Product_FREQUENCY_M'] = np.where(sales_df['DATE_LIVRAISON']>=last_3_months,sales_df['Number_Lines_M']/NUMBER_OF_OPEN_DAYS_3_MONTHS,0)
    #calculate Product Frequency for last 3 Weeks
    sales_df['Product_FREQUENCY_W'] = np.where(sales_df['DATE_LIVRAISON']>=last_3_weeks,sales_df['Number_Lines_W']/NUMBER_OF_OPEN_DAYS_3_WEEKS,0)
    #Product Frequency deppending on the last 3 months and last 3 weeks
    sales_df['Product_FREQUENCY'] = np.where(sales_df['Product_FREQUENCY_M']>sales_df['Product_FREQUENCY_W'],sales_df['Product_FREQUENCY_M'],sales_df['Product_FREQUENCY_W'])
    #Product Frequency for other products not included in the last 3 months is based on full period
    sales_df['Product_FREQUENCY'] = np.where(sales_df['Product_FREQUENCY']==0, sales_df['Number_Lines']/NUMBER_OF_OPEN_DAYS_YEAR, sales_df['Product_FREQUENCY'])
    
    #caluclate the quantty demanded on each product for full period
    sales_df['Quantity_demand'] = sales_df[['ID_Product','TYPE_OP', 'QTE_COLISEE']].groupby(['ID_Product','TYPE_OP'])['QTE_COLISEE'].transform('sum')    
    #caluclate the quantty demanded on each product for last 3 Months
    sales_df['Quantity_demand_M'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_months,sales_df[['ID_Product','TYPE_OP', 'QTE_COLISEE']].groupby(['ID_Product','TYPE_OP'])['QTE_COLISEE'].transform('sum'),0)    
    #caluclate the quantty demanded on each product for las 3 Weeks
    sales_df['Quantity_demand_W'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_weeks,sales_df[['ID_Product','TYPE_OP', 'QTE_COLISEE']].groupby(['ID_Product','TYPE_OP'])['QTE_COLISEE'].transform('sum'),0)    
    #create a mask to separate 2d products
    mask_2d = sales_df['Volume_Product'] == 0
    #caluclate the Average_Volume/Day on each 3d product for las 3 Weeks
    sales_df.loc[~mask_2d, 'Average_Volume/Day_W'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_weeks,sales_df['Quantity_demand_W']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_3_WEEKS,0)
    #caluclate the Average_Volume/Day on each 3d product for las 3 Months
    sales_df.loc[~mask_2d, 'Average_Volume/Day_M'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_months,sales_df['Quantity_demand_M']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_3_MONTHS,0)
    #Average_Volume/Day deppending on the last 3 months and last 3 weeks
    sales_df.loc[~mask_2d,'Average_Volume/Day'] = np.where(sales_df['Average_Volume/Day_M']>sales_df['Average_Volume/Day_W'],sales_df['Average_Volume/Day_M'],sales_df['Average_Volume/Day_W'])
    #Average_Volume/Day for other 3d products not included in the last 3 months is based on full period
    sales_df.loc[~mask_2d, 'Average_Volume/Day'] = np.where(sales_df['Average_Volume/Day']==0,  sales_df['Quantity_demand']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_YEAR, sales_df['Average_Volume/Day'])
    #temporary volume on products that don't have the Hight dimension
    volume_temp = np.floor(sales_df.loc[mask_2d, 'LONG']*sales_df.loc[mask_2d, 'LARG'])
    #caluclate the Average_Volume/Day on each 2d product for las 3 Weeks
    sales_df.loc[mask_2d, 'Average_Volume/Day_W'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_weeks,sales_df['Quantity_demand_W']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_3_WEEKS,0)
    #caluclate the Average_Volume/Day on each 2d product for las 3 Months
    sales_df.loc[mask_2d, 'Average_Volume/Day_M'] =  np.where(sales_df['DATE_LIVRAISON']>=last_3_months,sales_df['Quantity_demand_M']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_3_MONTHS,0)
    #Average_Volume/Day deppending on the last 3 months and last 3 weeks
    sales_df.loc[mask_2d,'Average_Volume/Day'] = np.where(sales_df['Average_Volume/Day_M']>sales_df['Average_Volume/Day_W'],sales_df['Average_Volume/Day_M'],sales_df['Average_Volume/Day_W'])
    #Average_Volume/Day for other 2d products not included in the last 3 months is based on full period
    sales_df.loc[mask_2d, 'Average_Volume/Day'] = np.where(sales_df['Average_Volume/Day']==0,  sales_df['Quantity_demand']*sales_df['Volume_Product']/NUMBER_OF_OPEN_DAYS_YEAR, sales_df['Average_Volume/Day'])
    
    #drop unnecessary columns
    sales_df.drop(['Product_FREQUENCY_M','Product_FREQUENCY_W', 'Number_Lines_M', 'Number_Lines_W','Quantity_demand_M','Quantity_demand_W','Average_Volume/Day_M','Average_Volume/Day_W'],axis=1,inplace=True)
    
    #this block of code is to get each unique product based on ID_Product and TYPE_OP and form the article dataframe with the sales analyses on each product
    final_dict = {'ID_Product':[], 'TYPE_OP':[], 'Number_Lines':[], 'Product_FREQUENCY':[], 'Quantity_demand':[], 'Average_Volume/Day':[]}
    grouped = sales_df.groupby(['ID_Product','TYPE_OP']) # group DataFrame by product_id
    dfs = [group for _, group in grouped] # create list of DataFrames, where each DataFrame corresponds to a unique product_id
    for df1 in dfs:
            temp_row = df1.head(1)
            final_dict['ID_Product'].append(temp_row['ID_Product'].values[0])
            final_dict['TYPE_OP'].append(temp_row['TYPE_OP'].values[0])
            final_dict['Number_Lines'].append(temp_row['Number_Lines'].values[0])
            final_dict['Product_FREQUENCY'].append(temp_row['Product_FREQUENCY'].values[0])
            final_dict['Quantity_demand'].append(temp_row['Quantity_demand'].values[0])
            final_dict['Average_Volume/Day'].append(temp_row['Average_Volume/Day'].values[0])
    final_df = pd.DataFrame.from_dict(final_dict).reset_index() 
    
    return final_df


def frequency(sales_df,product_df):
    sales_df.fillna(0, inplace=True)
    sales_df['TYPE_OP'] = np.where(sales_df['TYPE_OP']==0 ,'UNIT','COMPLET')
    dfu = update_df(product_df)
    sales_df =  pd.merge(sales_df, dfu, on=['ID_Product', 'TYPE_OP'], how='left')
    df_cal = calculations(sales_df)
    result_df = pd.merge(dfu, df_cal, on=['ID_Product', 'TYPE_OP'], how='left')
    result_df['Familly'] = 'Normal'
    result_df.loc[result_df['POIDS']<LIGHT_WEIGHT,'Familly'] = 'Fragile'
    result_df.loc[result_df['POIDS']>HEAVY_WEIGHT,'Familly'] = 'Heavy'

    save_dataframe(result_df,'result_df')

def sales_analysis(
          products_path = r'data\articles.csv',
          sales_path = r'data\ventes.csv',
          initial_path = r'data\initial_result.csv'):
          
    df_product= load_dataframes(products_path)
    df_sales =load_dataframes(sales_path)
    df_initial = load_dataframes(initial_path)
    df_product = df_product[df_product['ID_Product'].isin(df_initial['ID_Product'])]
    frequency(df_sales,df_product)
