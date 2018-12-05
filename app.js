var express = require('express');
var app = express();

var fs = require('fs');                 //additional npm functionality incl. mkdir
var https = require('https');
var http = require('http');
var helmet = require('helmet');         //for express security
var constants = require('constants');



var spawn = require("child_process").spawn; // for triggering python scripts etc
//var path = require('path');
var exec = require('child_process').exec;
var bodyParser = require('body-parser');
//app.use(bodyParser.json({limit: '50mb'}));
//app.use(bodyParser.urlencoded({limit: '50mb', extended: true}));
//app.use(express.json({limit: '50mb'}));
//app.use(express.bodyParser({limit: '50mb'})); //increase limit sizey



//for file upload
const fileUpload = require('express-fileupload'); //for uploading files
// default options

app.use(fileUpload());  //for uploading files

app.post('/upload', function(req, res) {
    if (!req.files)
	return res.status(400).send('No files were uploaded.');

    // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
    sampleFile = req.files.sampleFile;

    // Use the mv() method to place the file somewhere on your server
    sampleFile.mv('public/upload/'+sampleFile.name, function(err) {
	if (err)
	    return res.status(500).send(err);

    //python3 home/crscloud/govtools.org/webapps/bill_converter/generate.py https://github.com/antoinemcgrath/govtools.org/archive/master.zip

	scriptexec = ("python3 /home/crscloud/govtools.org/webapps/bill_converter/send_action.py " + sampleFile.name);
	//scriptexecute = scriptexec.toString();
	exec(scriptexec);
    //
	///var spawn = require("child_process").spawn;
	//var process = spawn('python3',["/home/crscloud/govtools.org/public/upload/script.py", '~/govtools.org/public/upload/'+sampleFile.name]);
	///BLOB = "TEST"
	///navigator.msSaveBlob(blob, "filename.csv")
    dest = sampleFile.name.split('.').slice(0, -1).join('.')+".txt"
	resp_url = ("Visit https://govtools.org/upload/"+dest);
    res.header('Content-disposition: attachment; filename=dest');
    //res.header(field, [value])
	res.send((resp_url));
    ///header('Content-type: application/vnd.ms-excel');


	///res.send('File converted!');
    });
});



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



//cat congress.ai/app.js //	port = 8089;  //	port = 8088;
//cat crsreports.com/app.js //	port = 8081; //	port = 8080;
//cat govtools.org/app.js //	port = 8085; //	port = 8084;


var port;
if (process.argv.length >= 2) {
    if (process.argv[2] == 'test') {
	port = 8085;
    } else if (process.argv[2] == 'deploy') {
	port = 8084;
    }
}


if (!port) {
    console.log("Please specify 'test' or 'deploy'");
} else {
    var serv = http.createServer(app).listen(port, function(){
        console.log('GovtTools.org App Online');
        });
    }