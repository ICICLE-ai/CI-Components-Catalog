# Change Log
All notable changes to this project will be documented in this file.

## 0.1.0 - 2023-04-20
This is the initial public release of the ICICLE CI Components Catlog, a web-based application
that tracks all major products developed by the ICICLE AI Institute. Using the Catalog, members within 
ICICLE as well as their collaborators and the general public can learn about the products being produced.

### Breaking Changes:
- None.

### New features:
- This initial release provides version 0.1.0 of the components schema in LinkML and JSONSchema format.
- Component data are stored in a flat file and served via a Flask application on hosted on the Tapis Pods
service at https://components.pods.icicle.tapis.io/. 
- This initial version supports private components, restricted to either ICICLE members of specific 
groups of members; this functionality utilizes authentication and authorization based on Tapis.

### Bug fixes:
- None.