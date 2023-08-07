from flask import Flask, request
from reassign_products import reassign_products
#from .heuristic_solution import heuristic_solution
#from .hungarian_solution import hungarian_solution

app = Flask(__name__)

@app.route('/reassign_products', methods=['POST'])
def api_reassign_products(data):

    reassign_products(data['products_path'], data['initial_solution_path'], data['locations_path'], data['reassign_percent'],data['weight_switch'])
    return {'message': 'Reassignment of products completed.'}



if __name__ == '__main__':
    app.run(debug=True)
