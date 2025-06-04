function formatLabel(key) {
    return key
      .replace(/([A-Z])/g, ' $1')        // Add space before capitals
      .replace(/^./, str => str.toUpperCase()); // Capitalize first letter
  }

async function initializeDetail() {
    let node = JSON.parse(sessionStorage.getItem("selectedNode"));
    // need to fetch from the db again
    if (!node){
        console.log("No node found in session storage. Fetching from URL parameters.");
        const params = new URLSearchParams(window.location.search);
        const nodeID = Number(params.get("id"));
        console.log(`Fetching node detail for ID: ${nodeID}`);

        const response = await fetch(`https://catalogbackend.pods.icicleai.tapis.io/api/node-detail?id=${encodeURIComponent(nodeID)}`);
        if (!response.ok) {
            console.error("Error fetching node detail:", response.statusText);
            return;
        }
        node = await response.json();
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

    const tbody = document.querySelector("#dataTable tbody");
    tbody.innerHTML = ""; // clear
    if (node && node.properties) {
    console.log(node.properties)
    attributes.forEach(attr => {
        // console.log(node.properties[attr])
        const value = node.properties[attr] ?? ""; // show blank if missing
        const row = document.createElement("tr");

        row.innerHTML = `
        <td><strong>${formatLabel(attr)}</strong></td>
        <td>${value}</td>
        `;

        tbody.appendChild(row);
    });
    } else {
    tbody.innerHTML = `<tr><td colspan="2">No data available.</td></tr>`;
    }
}

document.getElementById("returnList").addEventListener("click", () => {
    window.location.href = "list.html";
  });

// Invoke on page load
document.addEventListener("DOMContentLoaded", initializeDetail);
