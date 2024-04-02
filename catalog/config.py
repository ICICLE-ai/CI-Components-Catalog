import os
import yaml

with open('/catalog/config.yaml', 'r') as f:
    config = yaml.safe_load(f)


# override with environment vars
if os.environ.get('neo4j_user'):
    config['neo4j_user'] = os.environ.get('neo4j_user')
    
if os.environ.get('neo4j_pw'):
    config['neo4j_pw'] = os.environ.get('neo4j_pw')
    
if os.environ.get('neo4j_url'):
    config['neo4j_url'] = os.environ.get('neo4j_url')
    
if os.environ.get('neo4j_backend'):
    config['neo4j_backend'] = os.environ.get('neo4j_backend')
    
if os.environ.get('neo4j_test_user'):
    config['neo4j_user'] = os.environ.get('neo4j_test_user')
    
if os.environ.get('neo4j_test_pw'):
    config['neo4j_pw'] = os.environ.get('neo4j_test_pw')
    
if os.environ.get('neo4j_test_url'):
    config['neo4j_url'] = os.environ.get('neo4j_test_url')

