import yaml
from neo4j import GraphDatabase
from config import config

# Path to the dataset file.
DATASET = '/catalog/components-data.yaml'
    
def get_components_neo4j():
    """
    Proof of concept function connects to neo4j pod and returns components.
    """
    # Neo4j pod credentials
    user = config['neo4j_user']
    pw = config['neo4j_pw']
    url = f"bolt+s://{user}.pods.icicle.tapis.io:443"
    
    # Connect to the Neo4j database.
    driver = GraphDatabase.driver(url, auth=(user, pw))
    
    result = []
    
    # note: format neo4j output in such a way to make it readable
    with driver.session() as session:
        catalog = session.run("MATCH (n) RETURN n")
    
        for c in catalog:
            node = c["n"] # extract n node from each record (to exclude irrelevant stuff neo4j adds)
            properties = dict(node.items()) # get dict of node's properties/vals
            result.append(properties)
            
    return result

def get_components():
    """
    Proof of concept function that returns all components in the catalog.
    """
    with open(DATASET, 'r') as f:
        components = yaml.safe_load(f)
    return components['components']


def get_public_components():
    """
    Returns only the components for which publicAccess is true
    """
    return [c for c in get_components_neo4j() if c['publicAccess']]


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
