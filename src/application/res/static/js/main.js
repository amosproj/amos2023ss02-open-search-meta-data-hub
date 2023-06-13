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
    $('#formRow').after(`
        <div id="row${rowIdx}" class="row">
            <div class="col-md-3">
                <label for="metadata_tag${rowIdx}">Metadata tag</label><br>
                <input type="text" id="metadata_tag${rowIdx}" name="entry-${rowIdx}-metadata_tag" class="form-control"/>
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
            <div class="col-md-3">
                <button id="removeRow${rowIdx}" type="button" class="btn btn-danger">Remove</button>
            </div>
        </div>
    `);

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