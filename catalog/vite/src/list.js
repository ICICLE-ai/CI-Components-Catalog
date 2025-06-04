async function getData(){
    try {
      const response = await fetch("https://catalogbackend.pods.icicleai.tapis.io/api/data");
      if (!response.ok) {
          throw new Error(`HTTP error Status: ${response.status}`);
      }
      const data = await response.json();
      return data; // Return { nodes, relationships, nodeCount }
    } catch (error) {
        console.error("Error fetching graph data:", error);
        return null;
    }
}


// create list data
async function initializeList(){
    const { nodes, relationships, nodeCount } = await getData();
    const tableBody = document.querySelector("#dataTable tbody");

    tableBody.innerHTML = "";
    nodes.forEach(node => {
      const encodedID = encodeURIComponent(node.id);
      const detailLink = document.createElement("a");
      detailLink.href = `detail.html?id=${encodedID}`;
      detailLink.textContent = "(Details)";
      detailLink.addEventListener("click", () => {
        sessionStorage.setItem("selectedNode", JSON.stringify(node));
        console.log(node)
      });
      const row = document.createElement("tr");

        // Set the rest of the cells using innerHTML
      row.innerHTML = `
      <td>${node.properties.name}</td>
      <td>${node.properties.primaryThrust}</td>
      <td>${node.properties.status}</td>
      <td>${node.properties.description}</td>
      <td>${node.properties.componentVersion}</td>
      <td>${node.properties.targetIcicleRelease}</td>
      `;

    // append the link to the first cell
      row.querySelector("td").appendChild(detailLink);
    // append the row to the table
      tableBody.appendChild(row);
    });
    $("#dataTable").DataTable({
        destroy: true,
        paging: true,
        searching: true,
        ordering: true,
        responsive: true,
        scrollY: false, 
        pageLength: 10
    }); 
}

// button to toggle views
document.getElementById("toggleView").addEventListener("click", function () {
    window.location.href = "index.html";
});
  
  
// Invoke on page load
document.addEventListener("DOMContentLoaded", initializeList);