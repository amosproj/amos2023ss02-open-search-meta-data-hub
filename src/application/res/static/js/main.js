// Function to display an alert with "Hello World!"
function sendAlert() {
  alert("Hello World!");
}

// Function to perform a simple search
function performSearch(searchString) {
  $.ajax({
    url: "/search/simple", // URL for the search API
    data: { searchString: searchString }, // Search query parameters
    success: function (result) { // Callback function on successful response
      displaySearchResults(result.hits.hits); // Display the search results
    }
  });
}

// Function to perform an advanced search
function performAdvancedSearch(searchInfo) {
  $.ajax({
    url: "/search/advanced", // URL for the advanced search API
    data: { searchString: JSON.stringify(searchInfo) }, // Convert searchInfo to JSON and send as query parameter
    success: function (result) { // Callback function on successful response
      displaySearchResults(result.hits.hits); // Display the search results
    }
  });
}

// Function to display the search results
function displaySearchResults(hits) {
  var counter = 1;
  $("#resBody").html(""); // Clear the search results table body
  hits.forEach(function (hit) { // Iterate over each search result
    // Append a new row to the search results table
    $("#resBody").append("<tr><td>" + counter + "</td><td>" + hit._source.FileName + "</td><td>" + hit._source.FileInodeChangeDate + "</td></tr>");
    counter++;
  });
  $("#resTable").show(); // Show the search results table
}

// Function to extract search information from the input fields
function extractSearchInfo() {
  var searchInfo = {};
  var parameterCount = parseInt($('#countParams').val());

  for (var i = 0; i <= parameterCount; i++) {
    var parameterName = $('#parameterName' + i).val(); // Get the parameter name from the input field
    var operator = $('#operators' + i).val(); // Get the operator from the select field
    var searchValue = $('#searchValue' + i).val(); // Get the search value from the input field

    var operatorName;
    switch (operator) { // Convert the operator to a readable format
      case "=":
        operatorName = "EQUALS";
        break;
      case ">":
        operatorName = "GREATER_THAN";
        break;
      case ">=":
        operatorName = "GREATER_THAN_OR_EQUALS";
        break;
      case "<":
        operatorName = "LESS_THAN";
        break;
      case "<=":
        operatorName = "LESS_THAN_OR_EQUALS";
        break;
      case "<>":
        operatorName = "NOT_EQUALS";
        break;
    }

    // Add the parameter and its search information to the searchInfo object
    searchInfo[parameterName] = {
      search_content: searchValue,
      operator: operatorName
    };
  }

  return searchInfo; // Return the searchInfo object
}

$(document).ready(function () {
  // Event handler for the simple search button
  $("#searchButton").on("click", function () {
    var searchString = $("#searchField").val(); // Get the search query from the input field
    performSearch(searchString); // Perform the simple search
  });

  // Event handler for the advanced search button
  $("#advancedSearchButton").on("click", function () {
    var searchInfo = extractSearchInfo(); // Extract the search information from the input fields
    performAdvancedSearch(searchInfo); // Perform the advanced search
  });

  // Event handler for the advanced search toggle button
  $("#advancedSearchToggleButton").on("click", function () {
    $("#simpleSearch").hide(); // Hide the simple search section
    $("#advancedSearch").show(); // Show the advanced search section
  });

  // Event handler for the simple search toggle button
  $("#simpleSearchToggleButton").on("click", function () {
    $("#advancedSearch").hide(); // Hide the advanced search section
    $("#simpleSearch").show(); // Show the simple search section
  });

  // Event handler for the "Add Parameter" button
  $("#addParameterButton").on("click", function () {
    var parameterCount = parseInt($('#countParams').val()) + 1; // Increment the parameter count
    $('#countParams').val(parameterCount); // Update the parameter count input field

    // Create a new parameter input field group
    var newParameter = `
      <div class="input-group mb-3">
        <input type="text" class="form-control form-input" placeholder="Parameter Name" id="parameterName${parameterCount}">
        <select class="form-control" id="operators${parameterCount}">
          <option>=</option>
          <option>></option>
          <option>>=</option>
          <option><</option>
          <option><=</option>
          <option><></option>
        </select>
        <input type="text" class="form-control form-input" placeholder="Search Value" id="searchValue${parameterCount}">
      </div>`;

    $('#searchParameters').append(newParameter); // Append the new parameter input field group
  });
});

function showDetails(button) {
  // Get the hit details from the button's data-hit attribute
  var hit = JSON.parse(button.dataset.hit);

  // Create a table with the details
  var table = '<table class="table">';
  for (var key in hit) {
      table += '<tr><th>' + key + '</th><td>' + hit[key] + '</td></tr>';
  }
  table += '</table>';

  // Insert the table into the modal
  document.getElementById('detailsTable').innerHTML = table;

  // Show the modal
  $('#myModal').modal('show');
}