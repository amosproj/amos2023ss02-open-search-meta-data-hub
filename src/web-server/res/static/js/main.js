function sendAlert(){
    alert("Hello World!");
}

function searchOuter(){
    $.ajax({
        url: "/search/simple?searchString="+$("#searchField").val(),
        
        success: function( result ) {
            //result Parsen -> hits,hits

            var parsedRes = JSON.parse(result);
            var actualHits = parsedRes.hits.hits;
            var counter = 1;
            actualHits.foreach(function() {
                //an Tabelle anhängen
                $("#resBody").append("<tr><td>"+counter+"</td><td>" + THIS.SOURCE +"</td></tr>");
                console.log(this.SourceFile);    
                counter = counter +1;
            }); 
        } 
        
      });
}

$("#searchButton").on("click", function(){
    searchOuter();
});