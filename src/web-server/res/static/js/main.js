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

$("#searchButton").on("click", function(){
    searchOuter();
});