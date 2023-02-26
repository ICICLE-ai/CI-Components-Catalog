import yaml

# testing things

# Path to the dataset file.
DATASET = '/catalog/components-data.yaml'


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

