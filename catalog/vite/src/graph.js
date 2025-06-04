import { colorMapperFunctions, NVL } from '@neo4j-nvl/base';
import { ZoomInteraction, PanInteraction, ClickInteraction, DragNodeInteraction, HoverInteraction } from '@neo4j-nvl/interaction-handlers';


let nvl = null;


function formatLabel(key) {
    return key
      .replace(/([A-Z])/g, ' $1')    // Add space before capital letters
      .replace(/^./, str => str.toUpperCase()); // Capitalize first letter
  }
// show node properties on the side
function showNodeDetails(node) {
    const content = document.getElementById("property");
    if (!node || !node.properties) {
      content.innerHTML = "<p>No details available.</p>";
      return;
    }
  
    const attributes = [
      "id", "name", "owner", "primaryThrust", "status", "description", "componentVersion",
      "targetIcicleRelease", "license", "website", "sourceCode", "releaseNotes", "doi", "citation",
      "pypiPackage", "containerImage", "hpcModule", "unixPackage", "rustCrate", "javaJar",
      "artifactOther", "codeReviewConducted", "testsWritten", "securityReviewConducted",
      "biasAssessmentConducted", "usageDocumentationAvailable", "usageDocumentationUrl",
      "developerDocumentationAvailable", "developerDocumentationUrl",
      "trainingTutorialsAvailable", "trainingTutorialsUrl", "usageMetricsCollected"
    ];
  
    let propertiesHTML = `
      <ul style="list-style: none; padding: 0; margin: 0; max-width: 100%; word-break: break-word;">
    `;
  
    for (const key of attributes) {
      const value = node.properties[key];
  
      // Skip missing/empty/null values
      if (value === null || value === undefined || value === "") continue;
  
      const label = formatLabel(key);
      const displayValue =
        typeof value === "string" && value.startsWith("http")
          ? `<a href="${value}" target="_blank" style="word-break: break-all;">${value}</a>`
          : value;
  
      propertiesHTML += `
        <li style="padding: 6px 0; border-bottom: 1px solid #e0e0e0;">
          <strong>${label}:</strong> <span>${displayValue}</span>
        </li>
      `;
    }
  
    propertiesHTML += `</ul>`;
    content.innerHTML = propertiesHTML;
  }
  
  
async function getGraphData(){
try {
    const response = await fetch("https://catalogbackend.pods.icicleai.tapis.io/api/virtual-nodes");
    if (!response.ok) {
        throw new Error(`HTTP error Status: ${response.status}`);
    }
    const data = await response.json();
    return data;
} catch (error) {
    console.error("Error fetching graph data:", error);
    return null;
}
}

// setup interaction handlers
function setupHandlers(nvl) {
const zoom = new ZoomInteraction(nvl);
const pan = new PanInteraction(nvl);
const drag = new DragNodeInteraction(nvl);
const hover = new HoverInteraction(nvl)
const click = new ClickInteraction(nvl);

// hover to indicate clickable nodes
hover.updateCallback('onHover', (element) => {
    document.body.style.cursor = element ? "pointer" : "default";
});

// click nodes to display component properties, click twice to show expanded nodes
click.updateCallback("onNodeClick", async (node) => {
    // if not expandable, show details
    if (!node || !node.properties.versions){
    nvl.deselectAll();
    nvl.addAndUpdateElementsInGraph([{id: node.id, selected: true}],[]);
    showNodeDetails(node);
    return;
    } // 

    console.log(`Expanding virtual node: ${node.id}`);

    try {
        // Fetch expanded data (original nodes & relationships)
        const response = await fetch(`https://catalogbackend.pods.icicleai.tapis.io/api/expand-node?name=${encodeURIComponent(node.id.toString())}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const expandedData = await response.json(); // Get original nodes & relationships
        const expandedNodes = expandedData.nodes;
        const expandedRelationships = expandedData.relationships;

        // Remove virtual node and add original nodes & relationships
        const nodeIds = nvl.getNodes().map(n => n.id); // Get an array of IDs
        nvl.removeNodesWithIds(nodeIds);
        nvl.addAndUpdateElementsInGraph(expandedNodes, expandedRelationships);

        console.log(`Expanded into ${expandedNodes.length} nodes.`);
    } catch (error) {
        console.error("Error expanding virtual node:", error);
    }
});

// deselect node when clicking on the canvas, go back to the initial view
click.updateCallback('onCanvasClick', async () => {
    // console.log('Canvas clicked:');
    // clear the expanded nodes and relationships, load the virtual nodes
    try {
    // Fetch expanded data (original nodes & relationships)
    const virtualData = await getGraphData();
    if (!virtualData) {
        console.error("Failed to load data from backend");
        return;
    }
    const { nodes, relationships, nodeCount} = virtualData;

    // Remove virtual node and add original nodes & relationships
    const nodeIds = nvl.getNodes().map(n => n.id); // Get an array of IDs
    nvl.removeNodesWithIds(nodeIds);
    nvl.addAndUpdateElementsInGraph(nodes, relationships);
    document.getElementById("property").innerHTML = `<ul>` + `<li><strong>Total Components:</strong> ${nodeCount}</li>` + `</ul>` + `<p>Click on a component node to view its properties</p>`;
    nvl.deselectAll();
    } catch (error) {
    console.error("Error expanding virtual node:", error);
    }
    });
}


// create a new NVL instance
async function initializeGraph() {
    const virtualData = await getGraphData();
    if (!virtualData) {
        console.error("Failed to load data from backend");
        return;
    }
    const container = document.getElementById("graph")
    const { nodes, relationships, nodeCount} = virtualData;
    nvl = new NVL(container, nodes, relationships, {
        initialZoom: 0.3,
        minZoom: 0.5
    });
    document.getElementById("property").innerHTML = `<ul>` + `<li><strong>Total Components:</strong> ${nodeCount}</li>` + `</ul>` + `<p>Click on a component node to view its properties</p>`;

    // add interaction handlers
    setupHandlers(nvl);

    console.log("Graph rendered");
}


// button to toggle views
document.getElementById("toggleView").addEventListener("click", function () {
    window.location.href = "list.html";
});

// Invoke on page load
document.addEventListener("DOMContentLoaded", initializeGraph);
  