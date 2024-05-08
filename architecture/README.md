# ICICLE Architecture Conceptual Components

This directory contains a list of ICICLE conceptual components for building architecture diagrams.
It contains the following files:

1. ``architecture-component-schema.yaml`` -- The schema governing the structure of the components. 
2. ``common_arch_v1.yml`` -- The actual components. 



## Validate the Architecture Components 

```
docker run -v $(pwd):/work  -w /work/ --rm -it jstubbs/linkml linkml-validate -s architecture/architecture-component-schema.yaml architecture/common_arch_v1.yml
```

## Visualization in Neo4j

You can visualize the architecture data using the hosted Neo4j instance serving the most recent 
version of the data. The connection information is as follows: 

* URL: bolt+s://cicatalog.pods.icicle.tapis.io
* Port: 443
* User: cicatalog 
* Password: Ask on the ICICLE Slack channel.

The data can be visualized in a browser using the 
https://browser.neo4j.io/ website. 

### Common Queries

When working with the data, the following 
queries may be helpful: 

* Select all nodes: ``match (n) return n``
* Select the nodes for a specific project: ``MATCH (n) WHERE n.primaryThrust = 'useInspired/DA' RETURN n``
* Select all nodes from two projects: ``MATCH (n) WHERE (n.primaryThrust = 'useInspired/DA') OR (n.primaryThrust = 'useInspired/AE')  RETURN n``
* Select the nodes for a project or nodes that are
  common (i.e., not part of a specific project)
  ``MATCH (n) WHERE (n.primaryThrust = 'useInspired/DA') OR (NOT EXISTS(n.primaryThrust))  RETURN n``
* Provide the list of components to pull in, by id: ``MATCH (n) WHERE (n.id = 'mc') OR (n.id = 'ui') OR (n.id = 'int_plane') OR (n.id = 'authn_z') OR (n.id = 'ml_edge_to_center_middleware') RETURN n``


### Updating the Data (Admins)
We have automated the ETL pipeline that updates the Neo4j instance above from the current dataset in the 
git repository. It is a Tapis workflow and can be launched from the Tapis UI:

1. Log in to the Tapis UI with your TACC account: https://icicle.tapis.io/tapis-ui/#
2. Navigate to the pipelines: https://icicle.tapis.io/tapis-ui/#/workflows/pipelines/IKLE/
3. Click ``Run`` for the  ``reference_architecture_pipeline`` 

