import argparse
import time
import api
from reassign_products import reassign_products

def main():
    st = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--products_path', default=r'data\result_df.csv')
    parser.add_argument('--initial_result_path', default=r'data\initial_result.csv')
    parser.add_argument('--locations_path', default=r'data\emplacements.csv')
    parser.add_argument('--PERCENTAGE_REASSIGN', default=20, type=float)
    parser.add_argument('--Weight_switch', default=True)

    args = parser.parse_args()

    reassign_products(
        products_path=args.products_path,
        initial_result_path=args.initial_result_path,
        locations_path=args.locations_path,
        PERCENTAGE_REASSIGN=args.PERCENTAGE_REASSIGN,
        Weight_switch=args.Weight_switch
    )

    # Create a dict from the parsed arguments
   # data = vars(args)

    # Call your API function and pass in the arguments
    #api.api_reassign_products(data)
    et = time.time()
    compilation_time = et-st
    print('Reassignment of products completed. Check final_solution.csv in the current directory for the result.')
    print(compilation_time)
if __name__ == '__main__':
    main()
