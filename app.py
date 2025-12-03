import sys
import os
from flask import Flask, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound

# Create the main Flask app for the landing page
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Import the Gym Scheduling app
# We need to add the Gym scheduling directory to sys.path to handle imports correctly
gym_scheduling_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Gym scheduling')
sys.path.append(gym_scheduling_path)

try:
    # Use importlib because the directory has a space in the name
    import importlib.util
    spec = importlib.util.spec_from_file_location("gym_app_module", os.path.join(gym_scheduling_path, "app.py"))
    gym_module = importlib.util.module_from_spec(spec)
    sys.modules["gym_app_module"] = gym_module
    spec.loader.exec_module(gym_module)
    
    gym_app = gym_module.app
    
    # Mount the Gym Scheduling app at /gym-scheduling
    # We need to set the script root so URLs are generated correctly
    gym_app.config['APPLICATION_ROOT'] = '/gym-scheduling'
    
    # Combine the apps using DispatcherMiddleware
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/gym-scheduling': gym_app
    })
    
    print("Gym Scheduling app mounted successfully at /gym-scheduling")
except Exception as e:
    print(f"Error mounting Gym Scheduling app: {e}")
    # Define a route to show the error
    @app.route('/gym-scheduling')
    @app.route('/gym-scheduling/')
    def gym_scheduling_error():
        return f"<h1>Error mounting Gym Scheduling app</h1><pre>{e}</pre>", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
