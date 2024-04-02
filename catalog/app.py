from flask import Flask, render_template, redirect, request
import json
import requests


from iciflaskn import icicle_flaskn, auth
from config import config
import logging
import models

app = Flask(__name__)
app.register_blueprint(icicle_flaskn)
app.logger.setLevel(logging.INFO)

# Check config:
# sanity checks

# Log the neo4j backend flag
if 'neo4j_backend' not in config:
    raise Exception("no neo4j_backend in config. Quitting..")
else: 
    app.logger.info(f"using neo4j_backend: {config['neo4j_backend']}")

# Log the neo4j credentials
if 'neo4j_user' not in config:
    raise Exception("no neo4j_user in config. Quitting..")
else: 
    app.logger.info(f"using neo4j_user: {config['neo4j_user']}")
if 'neo4j_pw' not in config:
    raise Exception("no neo4j_pw in config. Quitting..")
else: 
    app.logger.info(f"using neo4j_pw: ********")  # Mask the password
if 'neo4j_url' not in config:
    raise Exception("no neo4j_url in config. Quitting..")
else: 
    app.logger.info(f"using neo4j_url: {config['neo4j_url']}")


    
# Set the secret key to some random bytes. 
# TODO: this key should be updated
app.secret_key = b'dsckj32487sj238193626%^#$' 


@app.route('/', methods=['GET'])
def root():
    """
    Redirect the root URL path to the main route.
    """
    return redirect("/data", 302)


@app.route('/data', methods=['GET'])
def get_data():
    """
    Main route displaying the table of components.
    """
    authenticated, user, roles = auth.is_logged_in()
    if not authenticated:
        logged_in = False
        message = 'NOTE: Only displaying public components.'
        components = models.get_public_components()
    else:
        logged_in = True
        message = f"Username: {user}; Roles: {roles}"
        components = models.get_components()
        # filter the components based on the user's roles:
        components = models.filter_components_by_roles(components, roles)
    
    total = len(components)
    return render_template('data.html', 
        components=components,
        total=total, 
        message=message, 
        logged_in=logged_in)


@app.route('/data/<cid>', methods=['GET'])
def get_component(cid):
    """
    Get the details of a specific component by its id.
    """
    authenticated, user, roles = auth.is_logged_in()
    if not authenticated:
        logged_in = False
        message = 'NOTE: Only displaying public components.'
        components = models.get_public_components()
    else:
        logged_in = True
        message = f"Username: {user}; Roles: {roles}"
        components = models.get_components()
        # filter the components based on the user's roles:
        components = models.filter_components_by_roles(components, roles)
    # get the specific component
    for c in components:
        if c['id'] == cid:
            component = c
            message = ""
            break
    else:
        message = "Component does not exist."
        component = None

    return render_template('details.html', 
        component_name=component['name'], 
        component=component,
        message=message)



# run the development server when started from the command line
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    
test_client = app.test_client()
