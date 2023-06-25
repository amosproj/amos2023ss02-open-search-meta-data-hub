$(document).ready(function(){


  $('#entry-0-metadata_tag').select2({
    theme: 'bootstrap',
    width: 'resolve' // need to override the changed width
});

  /* Test Fuse.js
  let selectElement = document.getElementById('your-select-id');
  let optionsArray = Array.from(selectElement.options).map(option => option.value);
  let fuse = new Fuse(optionsArray, {
    shouldSort: true,
    includeScore: true,
    threshold: 0.6, // determines how fuzzy the search should be
    location: 0,
    distance: 100,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: [
      "option"
    ]
  });
  */
  

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
    $("#entry-"+rowIdx+"-metadata_tag").select2({theme: 'bootstrap', width: 'resolve'}); // make it searchable

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
  
