var express = require('express');
var app = express();

var fs = require('fs');                 //additional npm functionality incl. mkdir
var https = require('https');
var http = require('http');
var helmet = require('helmet');         //for express security
var constants = require('constants');
var bodyParser = require('body-parser');


var path = require('path');

//Search Match Updated to Include SERVE 1 Line 90
//ITEM PAGE SERVE UPDATED Line 120
//INFOR page serve1 updated line 150



function uniq(a) {
        var seen = {};
        return a.filter(function(item) {
                return seen.hasOwnProperty(item) ? false : (seen[item] = true);
        });
}

app.use(helmet());
//app.use(bodyParser.urlencoded({ extended: false }))

//app.use(bodyParser.json())
app.set('views', __dirname + '/views');
app.engine('html', require('ejs').renderFile);
app.use(express.static(__dirname + '/public'));

app.set('view engine', 'html');

app.get('/', function(req, res) {
        res.render('index.html')
});
app.get('/result', function(req, res) {
        res.render('result.html');
});
app.get('/item', function(req, res) {
        res.render('result.html');
});
app.get('/about', function(req, res){
        res.render('about.html');
})




//ITEM PAGE SERVE UPDATED Line 120
//logic for item page
//Is based on ORDERCODE

///break off onto a nesssw resource get file renders layouts page formating from additional file



// Code for report infor page serve1 updated line 150
// Code fos report info page

var port;

if (process.argv.length >= 2) {
    if (process.argv[2] == 'test') {
	port = 8081;
    } else if (process.argv[2] == 'deploy') {
	port = 8080;
    }
}

if (!port) {
    console.log("Please specify 'test' or 'deploy'");
} else {
    }, function(err,thedb){
	if(err) console.log(err);
	console.log("connected!");
    });

    var serv = http.createServer(app).listen(port, function(){
	console.log('CRSReports App Online');
    });
}
