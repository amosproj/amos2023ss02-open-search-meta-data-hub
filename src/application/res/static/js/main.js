let myDict;  // Declare dict
let rowIdx;  // Declare rowIdx
$(document).ready(function(){


  $('#entry-0-metadata_tag').select2({
    theme: 'bootstrap',
    width: 'resolve' // need to override the changed width
  });
  

  $("#advancedSearchToggleButton").on("click", function () {
    $("#simpleSearch").hide(); // Hide the simple search section
    $("#advancedSearch").show(); // Show the advanced search section
  });

  // Event handler for the simple search toggle button
  $("#simpleSearchToggleButton").on("click", function () {
    $("#advancedSearch").hide(); // Hide the advanced search section
    $("#simpleSearch").show(); // Show the simple search section
  });

  rowIdx = 0;
  myDict = JSON.parse($("#datatypesDict").val());  // Parse the JSON string back to a JavaScript object

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
                    <option value="tag_not_exists">tag not exists</option>
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
                    <option disabled style="text-align:center;">────────────────</option>
                    <option value="is_greater_or_equal">is greater or equal</option>
                    <option value="is_smaller_or_equal">is smaller or equal</option>
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

  // Set the initial event listener for the metadata tag select field in the first row
  $('#entry-0-metadata_tag').change(function() {
    updateConditionOptions(0, $(this).val());
  });
  
  // Bind the change event for the metadata tag select field of the new row
    $('#entry-' + rowIdx + '-metadata_tag').change(function() {
        updateConditionOptions(rowIdx, $(this).val());
    });

  //execure one Time on page load:
  updateConditionOptions(0, $('#entry-0-metadata_tag').val());

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

// Update the condition select field options based on the selected metadata tag
function updateConditionOptions(rowIdx, metadataTagValue) {
  // Define the condition options for each data type
  var conditionOptions = {
    'text': ['tag_exists', 'tag_not_exists', 'field_is_empty', 'field_is_not_empty', 'contains', 'not_contains'],
    'float': ['tag_exists', 'tag_not_exists', 'field_is_empty', 'field_is_not_empty', 'is_equal', 'is_not_equal', 'is_greater', 'is_smaller'],
    'date': ['tag_exists', 'tag_not_exists', 'field_is_empty', 'field_is_not_empty', 'is_equal', 'is_not_equal', 'is_greater', 'is_smaller'],
  };

  // Get the selected data type from the metadata tag value
  var selectedDataType = myDict[metadataTagValue];

  // Populate the condition select fied with the appropriate options
  var conditionSelect = $("#entry-" + rowIdx + "-condition");

  // Store the current selected option
  var currentOption = conditionSelect.val();

  // Disable all options
  conditionSelect.find('option').each(function() {
    $(this).prop('disabled', true);
  });

  // Enable the options that are available for the selected data type
  conditionOptions[selectedDataType].forEach(function(condition) {
    conditionSelect.find('option[value="' + condition + '"]').prop('disabled', false);

  // If the currently selected option is not disabled, set it back
  if (conditionOptions[selectedDataType].includes(currentOption)) {
    conditionSelect.val(currentOption);
  } else {
    // else select the first non-disabled option
    conditionSelect.val(conditionSelect.find('option:not([disabled]):first').val());
  }

  });
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
  
