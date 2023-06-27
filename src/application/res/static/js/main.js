$(document).ready(function(){

  $("#advancedSearchToggleButton").on("click", function () {
    $("#simpleSearch").hide(); // Hide the simple search section
    $("#advancedSearch").show(); // Show the advanced search section
  });

  // Event handler for the simple search toggle button
  $("#simpleSearchToggleButton").on("click", function () {
    $("#advancedSearch").hide(); // Hide the advanced search section
    $("#simpleSearch").show(); // Show the simple search section
  });

  let rowIdx = 0;

  $('#addRow').on('click', function () {
    // Increment the row index when button is clicked
    rowIdx++;

    // Create the new row with incremented indices
    var options = $("#entry-0-metadata_tag > option").clone();
    $('#formRow').after(`
        <div id="row${rowIdx}" class="row formRow">
            <div class="col-md-3">
                <label for="metadata_tag${rowIdx}">Metadata tag</label><br>
                <select class="form-control" id="entry-${rowIdx}-metadata_tag" name="entry-${rowIdx}-metadata_tag"></select>
            </div>
            <div class="col-md-3">
                <label for="condition${rowIdx}">Condition</label><br>
                <select id="condition${rowIdx}" name="entry-${rowIdx}-condition" class="form-control">
                    <option value="tag_exists">tag exists</option>
                    <option value="tag_not_exist">tag not exists</option>
                    <option disabled style="text-align:center;">────────────────</option>
                    <option value="field_is_empty">field is empty</option>
                    <option value="field_is_not_empty">field is not empty</option>
                    <option disabled style="text-align:center;">────────────────</option>
                    <option value="contains" selected>contains</option>
                    <option value="not_contains">not contains</option>
                    <option disabled style="text-align:center;">────────────────</option>
                    <option value="is_equal">is equal</option>
                    <option value="is_not_equal">is not equal</option>
                    <option disabled style="text-align:center;">────────────────</option>
                    <option value="is_greater">is greater</option>
                    <option value="is_smaller">is smaller</option>
                </select>
            </div>
            <div class="col-md-3">
                <label for="value${rowIdx}">Value</label><br>
                <input type="text" id="value${rowIdx}" name="entry-${rowIdx}-value" class="form-control"/>
            </div>
            <div class="col-md-2">
              <label for="entry-0-weight">Weight</label><br>
              <input class="form-control" id="entry-${rowIdx}-weight" max="100" min="1" name="entry-${rowIdx}-weight" type="number" value="1">
            </div>
            <div class="col-md-1 d-flex align-items-end">
            <button id="removeRow${rowIdx}" type="button" class="btn btn-danger">Remove</button>
            </div>
        </div>
    `);

    $("#entry-"+rowIdx+"-metadata_tag").append(options);

    // Attach click event to the Remove button
    $('#removeRow' + rowIdx).on('click', function () {
        $(this).closest('div.row').remove();
    });
});
  
  

});


function showDetails(button) {
  // Get the hit details from the button's data-hit attribute
  var hit = JSON.parse(button.dataset.hit);

  // Create a table with the details
  var table = '<table class="table wrap-text">';
  for (var key in hit) {
      table += '<tr><th>' + key + '</th><td>' + hit[key] + '</td></tr>';
  }
  table += '</table>';

  // Insert the table into the modal
  document.getElementById('detailsTable').innerHTML = table;

  // Show the modal
  $('#myModal').modal('show');
}


 $(document).ready(function() {
    $('.title').click(function() {
      var row = $(this).closest('tr');
      row.next('.iframeRow').toggle();
    });
  });

  //show Visualization
  function showVisualization(title,iframe_code) {
    var iframe = '<tr class="iframeRow" style="display: none;"><td colspan="3">' + iframe_code + '</td></tr>';
    document.getElementById('detailsTable').innerHTML = iframe;
    document.getElementById('exampleModalLabel').innerHTML = title;

    // Show the modal
    $('#iframeModal').modal('show');
  }
  
  // function configurePanels() {
  //   document.getElementById('detailsTable').innerHTML = "iframe";
  //   document.getElementById('exampleModalLabel').innerHTML = "title";

  //   // Show the modal
  //   $('#dialogContainer').modal('show');
  // }
  function openSidebar(iframes) {
    var checkboxes = '';
    for (var i = 0; i < iframes.length; i++) {
      var iframe = iframes[i];
      checkboxes += '<input type="checkbox" id="check' + i + '" name="' + iframe.title + '">';
      checkboxes += '<label for="check' + i + '">' + iframe.title + '</label><br>';
    }
    
    checkboxes += '<br>';
    checkboxes += '<input type="checkbox" id="selectAll" onclick="toggleSelectAll()">'
    checkboxes += '<label for="selectAll">Select All</label>';
    
    document.getElementById('detailsTable').innerHTML = checkboxes;
    document.getElementById('sidebarTitle').innerHTML = "Panels Configuration";
  
    // Show the sidebar
    document.getElementById('sidebarContainer').style.transform = "translateX(0)";
  }
  
  function closeSidebar() {
    // Hide the sidebar
    document.getElementById('sidebarContainer').style.transform = "translateX(100%)";
  }
  

  document.addEventListener('click', function(event) {
    var sidebarContainer = document.getElementById('sidebarContainer');
    var sidebarOverlay = document.getElementById('sidebarOverlay');
  
    if (!sidebarContainer.contains(event.target) && event.target !== sidebarOverlay && event.target !== document.getElementById('openSidebarButton')) {
      closeSidebar();
    }
  });
  

  function toggleSelectAll() {
    var selectAllCheckbox = document.getElementById('selectAll');
    var checkboxes = document.querySelectorAll('[id^="check"]');
  
    for (var i = 0; i < checkboxes.length; i++) {
      checkboxes[i].checked = selectAllCheckbox.checked;
    }
  }