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
    for (let i = 0; i < parameterCount; i++) {
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
        'operator': operatorName,
      };
    }
    
    }
  
  $('#advancedSearchButton').click(function() {
    let search_info = advancedSearch();
    console.log(search_info);
  
    $.ajax({
      url: '/your-endpoint-here',
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
  
  

$("#searchButton").on("click", function(){
    searchOuter();
});