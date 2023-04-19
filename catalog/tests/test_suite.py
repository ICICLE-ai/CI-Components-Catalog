import pytest
import sys
import os
from neo4j import GraphDatabase

# Add the path to the catalog directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from catalog import app
from catalog.app import test_client
from catalog.models import get_components_neo4j, get_components_file, get_components, get_public_components
import json

@pytest.fixture
def neo4j_fixture():
    """
    Create fixture to pass test data into test-neo4j container instance.
    Make sure to include these keys: 'id', 'name', and 'publicAccess'
    """
    
    driver = GraphDatabase.driver(config['neo4j_url'], auth=(config['neo4j_user'], config['neo4j_pw']))
    with driver.session() as session:
        session.run("CREATE (:Person {id: 'Jason', name: 'Kim', age: 30, publicAccess: true})")
        session.run("CREATE (:Person {id: 'Joe', name: 'Stubbs', age: 35, publicAccess: false})")
    yield driver
    
    with driver.session() as session:
        session.run("MATCH (p:Person) DELETE p")
        session.close()
    driver.close()

    
def test_get_components_neo4j(neo4j_fixture):
    
    # Call the function and get the result
    result = get_components_neo4j()

    # Assert that the result matches the expected output
    assert result == [{'id': 'Jason', 'name': 'Kim', 'age': 30, 'publicAccess': True}, 
                      {'id': 'Joe', 'name': 'Stubbs', 'age': 35, 'publicAccess': False}]


def test_get_public_components(neo4j_fixture):
    
    # get component with public key set to true
    result = get_public_components()
    
    # Assert that result only contains the component(s) set as public
    assert len(result) == 1
    assert result[0]['id'] == 'Jason'
    
    
def test_data_route(neo4j_fixture):
    
    # Make a request to the /data route    
    with test_client as client:
        response = client.get('/data')
        assert response.status_code == 200


def test_data_cid_route(neo4j_fixture):
    # Make a request to the /data/<cid> route for a valid cid
    with test_client as client:
        response = client.get('/data/Jason')
        assert response.status_code == 200
            
    # Make a request to the /data/<cid> route for an invalid/nonexistant cid
    with test_client as client:
        response = client.get('/data/Bob')
        assert response.status_code == 500

