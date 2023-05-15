


function sendAlert(){
    alert("Hello World!");
}

function searchOuter(){
    $.ajax({
        url: ".../mdh/_search",
        
        success: function( result ) {
          $( "#searchField" ).html( "<strong>" + result + "</strong>" );
        }
      });
}