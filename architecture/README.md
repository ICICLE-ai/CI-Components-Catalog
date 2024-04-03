# ICICLE Architecture Conceptual Components

This directory contains a list of ICICLE conceptual components for building architecture diagrams.
It contains the following files:

1. ``architecture-component-schema.yaml`` -- The schema governing the structure of the components. 
2. ``common_arch_v1.yml`` -- The actual components. 



## Validate the Architecture Components 

```
docker run -v $(pwd):/work  -w /work/ --rm -it jstubbs/linkml linkml-validate -s architecture/architecture-component-schema.yaml architecture/common_arch_v1.yml
```