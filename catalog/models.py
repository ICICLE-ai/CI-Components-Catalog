import yaml
from neo4j import GraphDatabase
# testing things 123 123 

# Path to the dataset file.
DATASET = '../components-data.yaml'



'''
def neo4j_data():

    # Neo4j pod credentials
    user = "testing"
    pw = "0FFX88a80b4CMsZCmNLFPNVnrakGYe"
    url = f"bolt+s://{user}.pods.icicle.tapis.io:443"
    # url = "bolt://localhost:7687"
    
    
    # Connect to the Neo4j database.
    driver = GraphDatabase.driver(url, auth=(user, pw))

    # Load the component data from the YAML file.
    with open(DATASET, 'r') as f:
        data = yaml.safe_load(f)
    
    with driver.session() as session:
        # Define the Cypher queries to create the nodes and relationships.
        component_query = """
        CREATE (:Component {id: $id, name: $name, version: $version, public_access: $public_access, restricted_to_role: $restricted_to_role})
        """

        dependency_query = """
        MATCH (c1:Component {id: $from_id}), (c2:Component {id: $to_id})
        CREATE (c1)-[:DEPENDS_ON]->(c2)
        """
    
    session.run(component_query)
    
    result = session.run("MATCH (n) RETURN n")
    for c in result:
        return c
    
    
    
print(neo4j_data())

    

# Define a function to execute the queries.
def load_data(tx, data):
    # Create the component nodes.
    for component in data['components']:
        tx.run(component_query, id=component['id'], name=component['name'], version=component['version'], public_access=component['publicAccess'], restricted_to_role=component.get('restrictedToRole'))
    # Create the dependency relationships.
    for dependency in data['dependencies']:
        tx.run(dependency_query, from_id=dependency['from'], to_id=dependency['to'])

# Execute the queries in a transaction.
with driver.session() as session:
    session.write_transaction(load_data, data)
Note that this is just an example script, and you may need to modify it to fit your specific use case.
'''




def get_components_neo4j():
    """
    Proof of concept function connects to neo4j pod and returns components.
    """
    # Neo4j pod credentials
    user = "cicatalog"
    pw = "aBfjTWco9YmsuClxtirG2hK9fSCO0o"
    url = f"bolt+s://{user}.pods.icicle.tapis.io:443"
    
    # Connect to the Neo4j database.
    driver = GraphDatabase.driver(url, auth=(user, pw))
    
    result = []
    
    # note: format neo4j output in such a way to make it readable
    with driver.session() as session:
        catalog = session.run("MATCH (n) RETURN n")
    
        for c in catalog:
            node = c["n"]
            properties = dict(node.items())
            result.append(properties)
            
    return result

#print(get_components_neo4j())

def get_components():
    """
    Proof of concept function that returns all components in the catalog.
    """
    with open(DATASET, 'r') as f:
        components = yaml.safe_load(f)
    return components['components']

print(get_components())

def get_public_components():
    """
    Returns only the components for which publicAccess is true
    """
    return [c for c in get_components() if c['publicAccess']]


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
