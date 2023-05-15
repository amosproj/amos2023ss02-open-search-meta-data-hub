var host = "localhost";
var protocol = "http";
var port = 9200;
var auth = "admin:admin"; // For testing only. Don't store credentials in code.
var ca_certs_path = "/full/path/to/root-ca.pem";

// Optional client certificates if you don't want to use HTTP basic authentication.
// var client_cert_path = '/full/path/to/client.pem'
// var client_key_path = '/full/path/to/client-key.pem'

// Create a client with SSL/TLS enabled.
var {Client} = require("@opensearch-project/opensearch");
var fs = require("fs");
var client = new Client({
    node: protocol + "://" + auth + "@" + host + ":" + port,
    // ssl: {
    //     ca: fs.readFileSync(ca_certs_path),
    //     // You can turn off certificate verification (rejectUnauthorized: false) if you're using
    //     // self-signed certificates with a hostname mismatch.
    //     // cert: fs.readFileSync(client_cert_path),
    //     // key: fs.readFileSync(client_key_path)
    // },
});

async function search(index_name, queryParam)
{
    var query = {
        query: {
            match: {
                FileName: {
                    query: queryParam,
                },
            },
        },
    };
    console.log(query);

    var response = await client.search({
        index: index_name,
        body: query,
    });

    i=0;
    while ( i < len(response.body.hits["hits"])){
        $("#resBody").append("<tr><td>"+i+"</td><td>"+ response.body.hits["hits"][i]["_source"]+"</td></tr>");
        i++;
    }
    $("#resTable").show();
    console.log(response.body.hits["hits"][0]["_source"]);

}


function searchOuter(){
    search('amoscore', $("#searchField").val());
}