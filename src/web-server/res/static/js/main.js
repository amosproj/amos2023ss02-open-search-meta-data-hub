
function sendAlert(){
    alert("Hello World!");
}

function searchOuter(){
    $.ajax({
        url: "/search/simple?searchString="+$("#searchField").val(),
        
        success: function( result ) {
            //result Parsen -> hits,hits

            //var parsedRes = JSON.parse(result);
            //console.log(parsedRes);
            var actualHits = result.hits.hits;
            console.log(actualHits);
            var counter = 1;
            $("#resBody").html("");
            actualHits.forEach(function(hit) {
                //an Tabelle anhängen
                $("#resBody").append("<tr><td>"+counter+"</td><td>" + hit._source.FileName +"</td><td>" + hit._source.FileInodeChangeDate +"</td></tr>");
                //console.log(this.SourceFile);    
                counter = counter +1;
            }); 
            $("#resTable").show();
        } 
        
      });
}

function advancedSearch() {
    let search_info = {};
    let parameterCount = parseInt($('#countParams').val());
    console.log(parameterCount);
    for (let i = 0; i <= parameterCount; i++) {
      let parameterName = $('#parameterName' + i).val();
      let operator = $('#operators' + i).val();
      let searchValue = $('#searchValue' + i).val();
  
      let operatorName;
      switch (operator) {
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
  
      search_info[parameterName] = {
        'search_content': searchValue,
        'operator': operatorName
      };
    }
    return search_info;
    }
  
  $('#advancedSearchButton').click(function() {
    let search_info = advancedSearch();
    console.log(search_info);
  
    $.ajax({
      url: '/search/advanced',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(search_info),
      success: function(result) {
        var actualHits = result.hits.hits;
        console.log(actualHits);
        var counter = 1;
        $("#resBody").html("");
        actualHits.forEach(function(hit) {
          $("#resBody").append("<tr><td>"+counter+"</td><td>" + hit._source.FileName +"</td><td>" + hit._source.FileInodeChangeDate +"</td></tr>");
          counter = counter + 1;
        }); 
        $("#resTable").show();
      },
      error: function(error) {
        console.error(error);
      }
    });
  });
  
  $('#advancedSearchToggleButton').click(function() {
    $("#simpleSearch").hide();
    $("#advancedSearch").show();
  });
  $('#simpleSearchToggleButton').click(function() {
    $("#advancedSearch").hide();
    $("#simpleSearch").show();
  });

$("#searchButton").on("click", function(){
    searchOuter();
});

$('#addParameterButton').click(function() {
  var parameterCount = parseInt($('#countParams').val()) + 1;
  $('#countParams').val(parameterCount);
  
  var newParameter = '<div class="input-group mb-3">';
  newParameter += '<input type="text" class="form-control form-input" placeholder="Parameter Name" id="parameterName' + parameterCount + '">';
  newParameter += '<select class="form-control" id="operators' + parameterCount + '">';
  newParameter += '<option>=</option><option>></option><option>>=</option><option><</option><option><=</option><option><></option>';
  newParameter += '</select>';
  newParameter += '<input type="text" class="form-control form-input" placeholder="Search Value" id="searchValue' + parameterCount + '">';
  newParameter += '</div>';
  $('#searchParameters').append(newParameter);
});
