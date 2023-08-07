
# Warehouse Product Reassignment

The Warehouse Product Reassignment program is designed to assign products to picking locations in a warehouse in order to minimize picking and replenishment costs. The program uses a Hungarian algorithm-based approach to optimize the assignment process.The project is divided into two parts: data preprocessing and product assignment.

## Data Preprocessing (this part is not necessary if the user has the analysed file from a third party program but the format of data should be the same as in result_df.csv file)

### preprocess_data.py

This script performs the necessary data preprocessing steps to prepare the data for product assignment. It includes the following functions:

- `save_dataframe(df, filename)`: Saves a dataframe to a CSV file.
- `load_dataframes(products_path)`: Loads the product data from a CSV file.
- `update_df(product_df)`: Updates the product dataframe by selecting relevant columns and adding a column for the operation type.
- `calculations(sales_df)`: Performs calculations on the sales data to derive additional metrics such as product frequency and quantity demanded.
- `frequency(sales_df, product_df)`: Performs the frequency analysis on the sales and product data to generate the final dataframe with analyzed product information.

To run the data preprocessing script, execute the following command:

```
python sales_analysis.py --sales_path <path_to_sales> --products_path <path_to_products> --initial_path <path_to_initial_result>
```

By default, the script assumes that the sales data is located in the `data/ventes.csv` file, the product data is located in the `data/articles.csv` file, and the initial result data is located in the `data/initial_result.csv` file. You can provide custom file paths as command-line arguments.

After running the script, the analyzed product data will be saved as `result_df.csv` in the `data` directory.

## Product Assignment

### hungarian_solution.py

This script contains the logic for assigning products to picking locations using the Hungarian algorithm. It includes the following functions:

- `cost_matrix(result_df, df_loc_available, df_loc, Weight_switch)`: Calculates the cost matrix for product assignment based on product and location data.
- `optimal_assignment(product_df, location_df, total_cost_matrix)`: Finds the optimal assignment of products to locations using the Hungarian algorithm.
- `assign_product_location(reassign_products, initial_solution, df_loc, Weight_switch)`: Assigns products to locations based on the initial solution and the products selected for reassignment.
- `reassign_products(products_path, initial_result_path, locations_path, PERCENTAGE_REASSIGN, Weight_switch)`: Coordinates the process of reassigning products to locations based on the given parameters.

To run the product assignment script, execute the following command:

```
python cli.py --products_path <path_to_result_df> --initial_result_path <path_to_initial_solution> --locations_path <path_to_df_loc> --PERCENTAGE_REASSIGN <reassign_percentage> --Weight_switch <algorithm>
```

By default, the script assumes that the result dataframe is located in the `data/result_df.csv` file, the initial solution dataframe is located in the `data/initial_result.csv` file, the locations dataframe is located in the `data/emplacements.csv` file, the reassignment percentage is 20%, and the Weight switch algorithm is enabled. You can provide custom file paths and parameter values as command-line arguments.

After running the script, the final product assignment solution will be saved as `final_solution.csv` in the `data` directory. A comparison of the costs between the initial solution and the final solution will be saved as `comparisson.csv` in the `data` directory.

## Running the Project

To run the entire project, follow these steps:

1. Preprocess the data by running the data preprocessing script:

```
python sales_analysis.py --sales_path <path_to_sales> --products_path <path_to_products> --initial_path <path_to_initial_result>
```
2. Prepare the input data:

   
   - **result_df.csv**: This file contains information about the products to be assigned. It should include columns such as `ID_Product`, `PREP`, `LONG`, `LARG`, `HAUT`, `Volume_Product`, `Number_Lines`, `Product_FREQUENCY`, `Quantity_demand`, `Average_Volume/Day`, `POIDS`, and `Familly`.(this file will be genrated from the first script if the user dose not have it before)

   - **initial_result.csv**: This file contains the initial solution or assignment of products to locations. It should include columns `ID_Product`, `CODE_BARRE`, and any other relevant information.

   - **emplacements.csv**: This file contains information about the picking locations in the warehouse. It should include columns such as `CODE_BARRE`, `LONGUEUR`, `LARGEUR`, `HAUTEUR`, `LIB_NIVEAU`, `COUT_EMPL`, `ID_GARE`, `Volume_Location`, and `TYPE`.



3. Run the product assignment script:

```
python cli.py --products_path <path_to_result_df> --initial_result_path <path_to_initial_solution> --locations_path <path_to_df_loc> --PERCENTAGE_REASSIGN <reassign_percentage> --Weight_switch <algorithm>
```

By default, the scripts assume that the necessary data files are located in the `data` directory. You can provide custom file paths as command-line arguments.

 - Replace `<path_to_result_df>`, `<path_to_initial_solution>`, and `<path_to_df_loc>` with the actual file paths of the respective input files.
   - `<reassign_percentage>` is an optional parameter that specifies the percentage of products to be reassigned. By default, it is set to 20.
   - `<algorithm>` is an optional parameter that specifies the algorithm to be used for the reassignment. By default, it is set to True.

   If you omit the command-line arguments, the program will use the default file paths and parameters.

4. The program will execute the product reassignment process and display the total picking cost, total replenishment cost, and weighted sum for both the final solution and the initial solution.

5. After completion, you can find the final solution in a file named `final_solution.csv` and the comparison between the final and initial solutions in a file named `comparison.csv` in the program directory.


## Prerequisites

Before running the program, make sure you have the following:

- Python 3.x installed
- Required dependencies installed (numpy, pandas, scipy, tqdm)


## Customization

You can customize the program behavior by modifying the following variables in the `utilities.py` file:

- `NUMBER_OF_OPEN_DAYS_3_MONTHS`, `NUMBER_OF_OPEN_DAYS_3_WEEKS`, `NUMBER_OF_OPEN_DAYS_YEAR`: Constants representing the number of open days in different time periods. Modify these values as per your specific requirements.

- `WORKER_TO_PICK`, `WORKER_TO_REPLENISH`: Constants representing the number of workers required for picking and replenishment tasks. Adjust these values according to your warehouse's workforce capacity.

- `WEIGHT_PICK`, `WEIGHT_REPLENISH`: Constants representing the weights for picking and replenishment costs in the cost calculation. Modify these values to prioritize one cost over the other.

- `LOCATION_TO_REPLENISH`: Constant representing the replenishment factor for location volume calculation. Adjust this value based on your warehouse's replenishment needs.

## Contributing

Contributions to the Warehouse Product Reassignment program are welcome. If you find any issues or have suggestions for improvements.
Note: If you encounter any issues or errors, please refer to the documentation or contact the project maintainer for assistance(Ermal Belul).


---

This README file provides an overview of the Warehouse Product Reassignment program and guides users on how to run it. If you have any further questions or need assistance, please feel free to ask.









