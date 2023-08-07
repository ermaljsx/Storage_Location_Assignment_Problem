import argparse
from preprocess_data  import sales_analysis

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--sales_path', default=r'data\ventes.csv')
    parser.add_argument('--products_path', default=r'data\articles.csv')
    parser.add_argument('--initial_path', default=r'data\initial_result.csv')


    args = parser.parse_args()

    sales_analysis(
        products_path=args.products_path,
        sales_path=args.sales_path,
        initial_path=args.initial_path

        
    )

    # Create a dict from the parsed arguments
   # data = vars(args)

    # Call your API function and pass in the arguments
    #api.api_reassign_products(data)
 

    print('Analysis of products completed. Check result_df.csv in the current directory for the result.')

if __name__ == '__main__':
    main()
