import yaml
import os
from neo4j import GraphDatabase
from config import config
from app import app

# Path to the dataset file.
DATASET = '/catalog/components-data.yaml'

def get_components_neo4j():
    """
    Proof of concept function connects to neo4j pod and returns components.
    """
    
    # Neo4j pod credentials
    user = config['neo4j_user']
    pw = config['neo4j_pw']
    url = config['neo4j_url']
        
    # url = f"bolt+s://{user}.pods.icicle.tapis.io:443"
    
    # Connect to the Neo4j database (added logging statements)
    try:
        app.logger.info("Connecting to Neo4j database...")
        driver = GraphDatabase.driver(url, auth=(user, pw))
        app.logger.info("Successfully connected to Neo4j pod")
    except Exception as e:
        raise Exception(f"Failed to connect to Neo4j database; debug: {e}")
    
    result = []
    
    # note: format neo4j output in such a way to make it readable
    with driver.session() as session:
        app.logger.info("Running query to get components from Neo4j...")
        catalog = session.run("MATCH (n) RETURN n")
    
        for c in catalog:
            node = c["n"] # extract n node from each record (to exclude irrelevant stuff neo4j adds)
            properties = dict(node.items()) # get dict of node's properties/vals
            result.append(properties)
            
        session.close()
        
    app.logger.info("Successfully retrieved components from Neo4j")
    return result
    
    driver.close()

def get_components_file():
    """
    Proof of concept function that returns all components in the catalog from local YAML file within repo.
    """
    with open(DATASET, 'r') as f:
        components = yaml.safe_load(f)
        
    app.logger.info("Successfully retrieved components from local YAML file")   
    return components['components']


def get_components():
    """
    Proof of concept function that returns all components either from local YAML file or neo4j pod.
    """
    if config['neo4j_backend']:
        return get_components_neo4j()
    else:
        return get_components_file()
    

def get_public_components():
    """
    Returns only the components for which publicAccess is true
    """
    if config['neo4j_backend']:
        return [c for c in get_components_neo4j() if c['publicAccess']]
    else:
        return [c for c in get_components_file() if c['publicAccess']]


def filter_components_by_roles(components, user_roles):
    """
    Filter a list of components based on the roles occupied by a user.
      components: list of component objects (dict).
      user_roles: list of roles (strings) a user occupies.
    """
    result = []
    for c in components:
        required_role = c.get('restrictedToRole')
        # if the component is restricted to a role, check if the role is in the user's roles
        # and only add it to the returned roles if it is.
        if required_role:
            if required_role in user_roles:
                result.append(c)
        else:
            result.append(c)
    return result
