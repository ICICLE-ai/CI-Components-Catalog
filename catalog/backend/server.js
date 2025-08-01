import express from 'express';
import * as dotenv from 'dotenv';
import cors from 'cors';
import neo4j from 'neo4j-driver';

dotenv.config(); // Load neo4j secrets from .env file

const app = express();
const PORT = 3001;

const db = 'neo4j';
// Enable CORS for Vite to call backend
app.use(cors());

// Connect to Neo4j
const driver = neo4j.driver(process.env.NEO4J_URL,
    neo4j.auth.basic(process.env.NEO4J_USER, process.env.NEO4J_PASSWORD)
);

// Color mapping from primary thusts
const thrustColor = {
  "core/Software": "#f80808ff",
  "core/CI4AI": "#76fa65ff",
  "core/AI4CI": "#4D96FF",
  "core/FoundationAI": "#ee923dff",
  "core/PADI": "#845EC2",
  "core/VA": "#ff7871ff",
  "useInspired/DA": "#efef12ff",
  "useInspired/AE": "#39e495ff",
  "useInspired/SF": "#003e85ff",
  "Other": "#000000ff"
};


// fetch virtual nodes(aggregated by name)
async function fetchVirtualNodes() {
  const session = driver.session()
  try{
    const result = await session.run("MATCH (n) RETURN count(n) AS nodeCount", {database: db});
    const nodeCount = result.records[0].get("nodeCount").toNumber();
    const nodeResult = await session.run("MATCH (n) RETURN n", {database: db});
    const relationshipResult = await session.run("MATCH (n)-[r]->(m) RETURN n, r, m", {database: db});

    const node_map = new Map()
    const relationship_map = new Map()

    // aggregate nodes
    nodeResult.records.forEach(record => {
      const node = record.get("n");
      const name = node.properties.name.toString();
      const thrust = node.properties.primaryThrust || "Other";
      console.log("virtual nodes fetchinging");
      console.log(thrust);
      const color = thrustColor[thrust] || thrustColor["Other"];
      if(!node_map.has(name)){
        node_map.set(name, {
          id: name,
          size: 100,
          properties: {name: name, versions:[node.properties.componentVersion.toString()]},
          color: color,
          caption: name
        });
      }
      else{
        node_map.get(name).properties.versions.push(node.properties.componentVersion.toString());
      }
    });

    // aggreegate relationships
    relationshipResult.records.forEach(record => {
      const relationship = record.get("r");
      const node1 = record.get("n");
      const node2 = record.get("m");
      const from = node1.properties.name.toString();
      const to = node2.properties.name.toString();
      const key = `${from}-${to}`;
      if(!relationship_map.has(key)){
        relationship_map.set(key, {
          id: key,
          caption: relationship.type.toString(),
          from: from,
          to: to,
          width: 5
        });
      }
    });
    return {nodes: Array.from(node_map.values()), relationships: Array.from(relationship_map.values()), nodeCount};
  }
  catch (error) {
    console.error("Error fetching data from neo4j database:", error);
  } finally {
      await session.close();
  }
}

// fetch data from neo4j database
async function fetchData() {
    const session = driver.session()
    try{
      const result = await session.run("MATCH (n) RETURN count(n) AS nodeCount", {database: db});
      const nodeCount = result.records[0].get("nodeCount").toNumber();
      // console.log(`Node count: ${nodeCount}`);
      const nodeResult = await session.run("MATCH (n) RETURN n", {database: db});
      const relationshipResult = await session.run("MATCH (n)-[r]->(m) RETURN n, r, m", {database: db});
      
      // get nodes and relationships
      // Map for deduplicate
      const nodes_map = new Map()
      const relationships = [];
  
      nodeResult.records.forEach(record => {
        const node = record.get("n");
        console.log("getting nodes");
        console.log(node);
        // add node into nodes(auto deduplicate)
        const thrust = node.properties.primaryThrust || "Other";
        console.log(thrust);
        const color = thrustColor[thrust] || thrustColor["Other"];
        nodes_map.set(node.identity.toString(), {
            id: node.identity.toString(),
            properties: node.properties,
            size: 100,
            color: color,
            caption: node.properties.name.toString()
        });
      });
  
      relationshipResult.records.forEach(record => {
          const relationship = record.get("r");
          const node1 = record.get("n");
          const node2 = record.get("m");
          // add relationship
          relationships.push({
            id: relationship.identity.toString(),
            caption: relationship.type.toString(),
            from: node1.identity.toString(),
            to: node2.identity.toString(),
            width: 5
        });
      });
  
      const nodes = Array.from(nodes_map.values());
      // console.log(nodes)
      // console.log(relationships)
      return { nodes, relationships, nodeCount };
    }catch (error) {
      console.error("Error fetching data from neo4j database:", error);
    } finally {
        await session.close();
    }
  }
  

async function fetchExpandedNode(nodeName){
  if(!nodeName){
    throw new Error("Missing node name");
  }
  const session = driver.session()
  try{
    console.log(`Expanding node: ${nodeName}`);
    // console.log(`type of nodeName: ${typeof nodeName}`);
    const nodeResult = await session.run('MATCH (n) WHERE n.name = $nodeName RETURN n',{nodeName}, {database: db});
    const relationshipResult = await session.run('MATCH (n)-[r]-(m) WHERE n.name = $nodeName RETURN n, r, m',{nodeName}, {database: db});

    const nodes_map = new Map()
    const relationships = [];
      // for version updates
    const nodeList = [];

    nodeResult.records.forEach(record => {
      const node = record.get("n");
      const thrust = node.properties.primaryThrust || "Other";
      const color = thrustColor[thrust] || thrustColor["Other"];
      const nodeData = {
        id: node.identity.toString(),
        properties: node.properties,
        size: 100,
        color: color,
        caption: node.properties.name.toString()
      }
      nodes_map.set(node.identity.toString(), nodeData);
      nodeList.push(nodeData);
    });


    // generate node version update relationships
    nodeList.sort((a, b) => a.properties.componentVersion - b.properties.componentVersion);

    // add version update relationships between consecutive versions
    for (let i = 0; i < nodeList.length - 1; i++) {
        relationships.push({
            id: `version-update-${nodeList[i].id}-${nodeList[i + 1].id}`,
            caption: "VERSION_UPDATE",
            from: nodeList[i].id,
            to: nodeList[i + 1].id,
            width: 8,
            color: "#FFA500" // orange for version updates
        });
    }

    relationshipResult.records.forEach(record => {
        const relationship = record.get("r");
        const node1 = record.get("n");
        const node2 = record.get("m");
        // add relationship
        relationships.push({
          id: relationship.identity.toString(),
          caption: relationship.type.toString(),
          from: node1.identity.toString(),
          to: node2.identity.toString(),
          width: 5
      });
        // add nodes
        const thrust1 = node1.properties.primaryThrust || "Other";
        const color1 = thrustColor[thrust1] || thrustColor["Other"];
        const thrust2 = node2.properties.primaryThrust || "Other";
        const color2 = thrustColor[thrust2] || thrustColor["Other"];
        nodes_map.set(node1.identity.toString(), {
          id: node1.identity.toString(),
          properties: node1.properties,
          size: 100,
          color: color1,
          caption: node1.properties.name.toString()
      });
      nodes_map.set(node2.identity.toString(), {
        id: node2.identity.toString(),
        properties: node2.properties,
        size: 100,
        color: color2,
        caption: node2.properties.name.toString()
    });
    });

    const nodes = Array.from(nodes_map.values());
    // console.log(nodes)
    // console.log(relationships)
    return { nodes, relationships};
  }catch (error) {
    console.error("Error fetching data from neo4j database:", error);
  } finally {
      await session.close();
  }
}

async function fetchNodeDetail(nodeID){
  console.log(`Fetching node detail for ID: ${nodeID}`);
  if(!nodeID){
    throw new Error("Missing node ID");
  }
  const session = driver.session()
  try{
    console.log(`Fetching node: ${nodeID}`);
    // console.log(`type of nodeName: ${typeof nodeName}`);
    const nodeResult = await session.run('MATCH (n) WHERE ID(n) = $nodeID RETURN n',{nodeID: Number(nodeID)}, {database: db});
    if (nodeResult.records.length === 0) {
      console.warn("No node found with this ID.");
      return null;
    }

    const node = nodeResult.records[0].get("n");
    const nodeDetail = {
      id: node.identity.toString(),
      properties: node.properties
    }

    return nodeDetail;
  }catch (error) {
    console.error("Error fetching data from neo4j database:", error);
  } finally {
      await session.close();
  }
}


 // API  
// fetch data from Neo4j
app.get('/api/data', async (req, res) => {
    const data = await fetchData();
    res.json(data);
});

// fetch virtual nodes from Neo4j
app.get('/api/virtual-nodes', async (req, res) => {
  const data = await fetchVirtualNodes();
  res.json(data);
});

// fetch expanded data from Neo4j
app.get("/api/expand-node", async (req, res) => {
  const nodeName = req.query.name;
  try {
      const expandedData = await fetchExpandedNode(nodeName);
      res.json(expandedData);
  } catch (error) {
      res.status(500).json({ error: error.message });
  }
});

// fetch node detail by id
app.get("/api/node-detail", async (req, res) => {
  const nodeID = req.query.id;
  try {
      const nodeDetail = await fetchNodeDetail(nodeID);
      res.json(nodeDetail);
  } catch (error) {
      res.status(500).json({ error: error.message });
  }
});

// Start the backend server
app.listen(PORT, () => console.log(`Backend running at http://localhost:${PORT}`));
