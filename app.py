from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint
import json
from cross_section_optimiser import CrossSectionOptimizer
from load_calculator import LoadCaluculator
from joint_3 import Joint_3
from joint_1_2_4 import Joints

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
    
class CrossSectionOptimization(Resource):
    def post(self):
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        
        optimizer = CrossSectionOptimizer(
            data.get('material', {}),
            data.get('load', {}),
            data.get('footprint', {})
        )
        
        return jsonify(optimizer.optimizer())
        
        # material_attributes = [
        #     'partial_factor', 'density', 'bending_strength', 'shear_strength', 
        #     'compression_parallel', 'e_modulus', 'e_modulus_5', 
        #     'modification_factor_permanent_term', 'modification_factor_medium_term', 
        #     'modification_factor_instantaneous_term', 'creep_factor', 'creep_factor_solid_timber'
        # ]
        
        # load_attributes = [
        #     'P_L', 'M_L', 'I_L', 'SLS_L', 'gk', 'g_lead', 'g_acmp', 'psi_lead', 'psi_acmp', 
        #     'P_clm', 'M_clm', 'I_clm'
        # ]
        
        # footprint_attributes = [
        #     'beam_length', 'height'
        # ]

        # optimizer = CrossSectionOptimizer(
        #     {key: data.get(key) for key in material_attributes},
        #     {key: data.get(key) for key in load_attributes},
        #     {key: data.get(key) for key in footprint_attributes}
        # )
        
class LoadCalculation(Resource):
    def post(self):
        data = request.get_json() 
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        calculator = LoadCaluculator(
            data.get('material', {}),
            data.get('footprint', {})
        )
        
        return jsonify(calculator.calculator())
    
class JointDetail1(Resource):
    def post(self):
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        details = Joints(
            data.get('footprint', {}),
            data.get('cross_section', {})
        )
        
        return jsonify(details.calculate_joint_1())
    
class JointDetail2(Resource):
    def post(self):
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        details = Joints(
            data.get('footprint', {}),
            data.get('cross_section', {})
        )
        
        return jsonify(details.calculate_joint_2())
    
class JointDetail3(Resource):
    def post(self):
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        details = Joint_3(
            data.get('material', {}),
            data.get('cross_section', {})
        )
        
        return jsonify(details.calculate_capacity_and_status_for_graph())
    
class JointDetail4(Resource):
    def post(self):
        data = request.get_json()  
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        details = Joints(
            data.get('footprint', {}),
            data.get('cross_section', {})
        )
        
        return jsonify(details.calculate_joint_4())


#api resources 
api.add_resource(CrossSectionOptimization, '/cross_section')
api.add_resource(LoadCalculation, '/load_calculator')
api.add_resource(JointDetail1, '/joint1')
api.add_resource(JointDetail2, '/joint2')
api.add_resource(JointDetail3, '/joint3')
api.add_resource(JointDetail4, '/joint4')

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = 'http://127.0.0.1:5000/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Crisis management calculations"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        response = jsonify(json.load(f))
        # Add CORS headers to the Swagger JSON response
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

if __name__ == '__main__':
    app.run(debug=True)