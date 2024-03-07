const config = require('./local-config.js');
const WebSocket = require('ws');
const cors = require('cors');
const fs = require('fs');

const { v4: uuidv4 } = require('uuid');

const DISTINCTIVE_L2DIST1 = 10.0;
const DISTINCTIVE_L2DIST2 = 15.0;
const CLIPSERVERURL = 'ws://' + config.config_CLIP_SERVER; //'ws://extreme00.itec.aau.at:8002';
console.log(CLIPSERVERURL);
const wss = new WebSocket.Server({ noServer: true });
let clipWebSocket = null;

const mongouri = 'mongodb://' + config.config_MONGODB_SERVER; // Replace with your MongoDB connection string
const MongoClient = require('mongodb').MongoClient;
let mongoclient = null;
connectMongoDB();

// Variables to store the parameter values
let text, concept, object, place, year, month, day, weekday, filename, similarto;
let combineCLIPWithMongo = false, filterCLIPResultsByDate = false, queryMode = 'all';

class QuerySettings {
    constructor(combineCLIPwithMongo = false, combineCLIPwithCLIP = 0) {
        this.combineCLIPwithMongo = combineCLIPwithMongo;
        this.combineCLIPwithCLIP = combineCLIPwithCLIP;
    }
}

let settingsMap = new Map();

//////////////////////////////////////////////////////////////////
// Connection to client
//////////////////////////////////////////////////////////////////
const http = require('http');
const express = require('express');
const { LocalConfig } = require('./local-config');
const app = express();
app.use(cors());  // Enable CORS for all routes
const port = 8080
const server = app.listen(port, () => {
    console.log('WebSocket server is running on port ' + port);
});

//const server = http.createServer(app);
server.on('upgrade', (request, socket, head) => {
    //console.log('connection upgrade');
    wss.handleUpgrade(request, socket, head, (ws) => {
        //console.log('handle connection upgrade');
        wss.emit('connection', ws, request);
    });
});

function isOnlyDateFilter() {
    if (weekday.toString().trim().length > 0 ||
        text.toString().trim().length > 0 ||
        filename.toString().trim().length > 0 ||
        concept.toString().trim().length > 0 ||
        object.toString().trim().length > 0 ||
        place.toString().trim().length > 0 ||
        similarto.toString().trim().length > 0) {
            return false;
        }
    else {
        return true;
    }
}

function extractDateFromFilename(filename) {
    // Extracting the date components from the filename
    const regex = /[0-9]+\/[0-9]+\/([0-9]{4})([0-9]{2})([0-9]{2})\_([0-9]{2})([0-9]{2})([0-9]{2})\_([0-9]+)/;

    const match = regex.exec(filename);

    if (match) {
        const [, year, month, day, hour, minute, second, frame] = match;

        // Convert strings to numbers for the Date constructor
        const numericYear = parseInt(year, 10);
        const numericMonth = parseInt(month, 10) - 1; // Month is 0-based in JavaScript Date object
        const numericDay = parseInt(day, 10);
        const numericHour = parseInt(hour, 10);
        const numericMinute = parseInt(minute, 10);
        const numericSecond = parseInt(second, 10);

        const date = new Date(numericYear, numericMonth, numericDay, numericHour, numericMinute, numericSecond);
        return date;
    } else {
        console.log("No date match found.");
        return null;
    }
}


function getDateComponents(date) {
    // Extracting year, month, and day from the Date object
    const year = date.getFullYear();
    const month = date.getMonth() + 1; // Adding 1 since getMonth() returns zero-based month
    const day = date.getDate();

    return { year, month, day };
}

function areSameDay(date1, date2) {
    const { year: year1, month: month1, day: day1 } = getDateComponents(date1);
    const { year: year2, month: month2, day: day2 } = getDateComponents(date2);

    return year1 === year2 && month1 === month2 && day1 === day2;
}

function generateUniqueClientId() {
    return uuidv4();
}


let clients = new Map(); // This map stores the associations between client IDs and their WebSocket connections
wss.on('connection', (ws) => {
    // WebSocket connection handling logic
    
    let clientId = generateUniqueClientId(); // You would need to implement this function
    clients.set(clientId, ws);
    let clientSettings = new QuerySettings();
    settingsMap.set(clientId, clientSettings);

    console.log('client connected: %s', clientId);

    //check CLIPserver connection
    if (clipWebSocket === null) {
        console.log('clipWebSocket is null, try to re-connect');
        connectToCLIPServer();
    }

    ws.on('message', (message) => {
        console.log('received from client: %s (%s)', message, clientId);
        // Handle the received message as needed

        //check CLIPserver connection
        if (clipWebSocket === null) {
            console.log('clipWebSocket is null');
        } else {

            msg = JSON.parse(message);

            // Append jsonString to the file
            msg.clientId = clientId;
            fs.appendFile('lscqueryserverlog.json', JSON.stringify(msg), function (err) {
                if (err) {
                    console.log('Error writing file', err)
                }
            });

            if (msg.content.type === 'textquery') { // || msg.content.type == 'file-similarityquery'

                nodequery = msg.content.query;

                queryMode = msg.content.queryMode;

                lenBefore = msg.content.query.trim().length;
                clipQuery = parseParameters(msg.content.query)
                combineCLIPWithMongo = false;
                filterCLIPResultsByDate = false;

                //special hack for file-similarity
                /*if (similarto !== '') {
                    msg.query = similarto;
                    msg.pathprefix = '';
                    msg.type = 'file-similarityquery';
                    clipQuery = 'non-empty-string';
                }*/

                if (clipQuery.trim().length > 0) { // only place for clip query
                    // if we have a clip query, we send it to the CLIP server with all parameters, and the clip server also handles the other parameters like text, concept, object, place, etc.
                    // otherwise we only do a search via the database in the else branch
                    msg.content.query = clipQuery
                    msg.content.clientId = clientId

                    if (clipQuery.length !== lenBefore) { //msg.content.query.trim().length || isOnlyDateFilter()) {
                        msg.content.resultsperpage = msg.content.maxresults;
                    }

                    console.log('sending to CLIP server: "%s" len=%d content-len=%d (rpp=%d, max=%d) - %d %d %d', clipQuery, clipQuery.length, msg.content.query.length, msg.content.resultsperpage, msg.content.maxresults, clipQuery.length, msg.content.query.trim().length, lenBefore);

                    let clipQueries = Array();
                    let tmpClipQuery = clipQuery;
                    if (tmpClipQuery.includes('<')) {
                        let idxS = -1;
                        do {
                            idxS = tmpClipQuery.indexOf('<');
                            if (idxS > -1) {
                                clipQueries.push(tmpClipQuery.substring(0,idxS));
                                tmpClipQuery = tmpClipQuery.substring(idxS+1);
                            } else {
                                clipQueries.push(tmpClipQuery); //last one
                            }
                        } while (idxS > -1);
                        console.log('found ' + clipQueries.length + ' temporal queries:');
                        for (let i=0; i < clipQueries.length; i++) {
                            console.log(clipQueries[i]);
                        }
                    }

                    if (isOnlyDateFilter() && queryMode !== 'distinctive' && queryMode !== 'moredistinctive') {
                        //C L I P   Q U E R Y   +   F I L T E R
                        filterCLIPResultsByDate = true;
                    } else {
                        //C L I P   +   D B   Q U E R Y
                        combineCLIPWithMongo = true;
                    }

                    if (clipQueries.length > 0) {
                        console.log("C L I P   Q U E R Y   +   F I L T E R")
                        clientSettings.combineCLIPwithCLIP = clipQueries.length;
                        for (let i=0; i < clipQueries.length; i++) {
                            let tmsg = msg;
                            tmsg.content.resultsperpage = 1234;
                            tmsg.content.query = clipQueries[i];
                            //tmsg.content.resultsperpage = tmsg.content.maxresults;
                            clipWebSocket.send(JSON.stringify(tmsg));
                        }
                        clipQueries = Array();
                    } else {
                        console.log("C L I P   Q U E R Y   +   D B   Q U E R Y")
                        //C L I P   +   D B   Q U E R Y
                        clipWebSocket.send(JSON.stringify(msg));
                    }


                    /*if (isOnlyDateFilter() && queryMode !== 'distinctive' && queryMode !== 'moredistinctive') {
                        //C L I P   Q U E R Y   +   F I L T E R
                        filterCLIPResultsByDate = true;
                        //msg.content.resultsperpage = msg.content.maxresults;
                        clipWebSocket.send(JSON.stringify(msg));
                    } else {
                        //C L I P   +   D B   Q U E R Y
                        combineCLIPWithMongo = true;
                        //msg.content.resultsperpage = msg.content.maxresults;
                        clipWebSocket.send(JSON.stringify(msg));
                    }*/

                    
                } else {
                    //D B   Q U E R Y
                    console.log('querying Node server');
                    queryImages(year, month, day, weekday, text, concept, object, place, filename, clientId).then((queryResults) => {
                        console.log("query* finished");
                        if ("results" in queryResults) {
                            console.log('sending %d results to client', queryResults.results.length);
                            ws.send(JSON.stringify(queryResults));

                            // Append jsonString to the file
                            queryResults.clientId = clientId;
                            fs.appendFile('lscqueryserverlog.json', JSON.stringify(queryResults), function (err) {
                                if (err) {
                                    console.log('Error writing file', err)
                                }
                            });
                        }
                    });
                }
            } else if (msg.content.type === 'metadataquery') {
                queryImage(msg.content.imagepath).then((queryResults) => {
                    console.log("query finished");
                    if (queryResults != undefined && "results" in queryResults) {
                        console.log('sending %d results to client', queryResults.results.length);
                        ws.send(JSON.stringify(queryResults));

                        // Append jsonString to the file
                        queryResults.clientId = clientId;
                        fs.appendFile('lscqueryserverlog.json', JSON.stringify(queryResults), function (err) {
                            if (err) {
                                console.log('Error writing file', err)
                            }
                        });
                    }
                });
            } 
            else if (msg.content.type === 'objects') {
                queryObjects(clientId);
            }
            else if (msg.content.type === 'concepts') {
                queryConcepts(clientId);
            }
            else if (msg.content.type === 'places') {
                queryPlaces(clientId);
            }
            else if (msg.content.type === 'texts') {
                queryTexts(clientId);
            }
        }
    });
    
    ws.on('close', function close() {
        console.log('client disconnected');
        // Close the MongoDB connection when finished
        //mongoclient.close();
    });
});



//////////////////////////////////////////////////////////////////
// Parameter Parsing
//////////////////////////////////////////////////////////////////

function parseParameters(inputString) {
    // Define the regex pattern to match parameters and their values
    const regex = /-([a-zA-Z]+)\s(\S+)/g;

    console.log("inputString: " + inputString)

    text = concept = object = place = year = month = day = weekday = filename = similarto = '';

    // Iterate over matches
    let match;
    while ((match = regex.exec(inputString.trim()))) {
        const [, parameter, value] = match; // Destructure the matched values
        console.log("parameter: " + parameter + " value: " + value)
        // Assign the value to the corresponding variable
        switch (parameter) {
            case 't':
                text = value;
                /*if (value === '"') {
                    const endQuoteIndex = value.indexOf('"', 1); // Find the index of the next double-quote starting from index 1
                    if (endQuoteIndex !== -1) {
                        const extractedString = value.substring(1, endQuoteIndex); // Extract the string between the first pair of double-quotes
                        const remainingString = value.substring(endQuoteIndex + 1); // Get the remaining string after the extracted substring
                    }
                }*/
                break;
            case 'c':
                concept = value;
                break;
            case 'o':
                object = value;
                break;
            case 'p':
                place = value;
                break;
            case 'wd':
                weekday = value;
                break;
            case 'd':
                day = value;
                break;
            case 'm':
                month = value;
                break;
            case 'fn':
                filename = value;
                break;
            case 'sim':
                similarto = value;
                break;
            case 'y':
                year = value;
                break;
        }
    }

    console.log('filters: text=%s concept=%s object=%s place=%s weekday=%s day=%s month=%s year=%s filename=%s', text, concept, object, place, weekday, day, month, year, filename);

    // Extract and remove the matched parameters from the input string
    const updatedString = inputString.replace(regex, '').trim();

    return updatedString.trim();
} 



//////////////////////////////////////////////////////////////////
// Connection to CLIP server
//////////////////////////////////////////////////////////////////
function connectToCLIPServer() {
    try {
        console.log('trying to connect to CLIP...');
        clipWebSocket = new WebSocket(CLIPSERVERURL);
        console.log('after connection trial')
        pendingCLIPResults = Array();

        clipWebSocket.on('open', () => {
            console.log('connected to CLIP server');
        
            // Start sending ping messages at the specified interval
            /*setInterval(() => {
                if (clipWebSocket.readyState === WebSocket.OPEN) {
                    let ping = { "content": {"ping":true} }
                    clipWebSocket.send(JSON.stringify(ping));
                }
            }, pingInterval);
            */
        })
        
        clipWebSocket.on('close', (event) => {
            // Handle connection closed
            clipWebSocket.close();
            clipWebSocket = null;
            console.log('Connection to CLIP closed', event.code, event.reason);
        });
        
        const weekdays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        


        clipWebSocket.on('message', (message) => {
            
            //console.log('received from CLIP server: ' + message);
        
            msg = JSON.parse(message);
            numbefore = msg.results.length;
            clientId = msg.clientId;
            clientWS = clients.get(clientId);
            let clientSettings = settingsMap.get(clientId);

            console.log('received %s results from CLIP server', msg.num);

            if (combineCLIPWithMongo === true) {

                console.log('combined query');
                let combinedResults = [];

                const database = mongoclient.db('lsc'); // Replace with your database name
                const collection = database.collection('images'); // Replace with your collection name
                var { query, projection } = getMongoQuery(year, month, day, weekday, text, concept, object, place, filename); 
                console.log('(1) mongodb query: %s', JSON.stringify(query));
                const sortCriteria = { filepath: 1 }; //-1 for desc
                collection.find(query, projection).sort(sortCriteria).toArray((error, documents) => {
                    if (error) {
                        return;
                    }

                    console.log('got %d results from mongodb', documents.length);
                    let processingInfo = {"type": "info",  "num": 1, "totalresults": 1, "message": documents.length + " results in database, now filtering..."};
                    clientWS.send(JSON.stringify(processingInfo));

                    const dateSet = new Set();

                    for (let i = 0; i < msg.results.length; i++) {
                        const elem = msg.results[i];

                        for (let k = 0; k < documents.length; k++) {
                            if (elem === documents[k].filepath) {
                                if (queryMode === 'first') {
                                    let eyear = elem.substring(0,4);
                                    let emonth = elem.substring(4,6);
                                    let eday = elem.substring(7,9);
                                    let dateStr = eyear + emonth + eday;
                                    if (dateSet.has(dateStr) === false) {
                                        dateSet.add(dateStr);
                                        combinedResults.push(elem);
                                    }
                                } else {
                                    combinedResults.push(elem);
                                }
                                break;
                            } else if (elem < documents[k].filepath) {
                                break;
                            }
                        }
                    }

                    msg.results = combinedResults;
                    msg.totalresults = combinedResults.length;
                    msg.num = combinedResults.length;

                    console.log('forwarding %d combined results to client %s', msg.totalresults, clientId);
                    //console.log(JSON.stringify(msg));
                    clientWS.send(JSON.stringify(msg));

                    // Append jsonString to the file
                    msg.clientId = clientId;
                    fs.appendFile('lscqueryserverlog.json', JSON.stringify(msg), function (err) {
                        if (err) {
                            console.log('Error writing file', err)
                        }
                    });

                });

            }
            else if (clientSettings.combineCLIPwithCLIP > 0) {
                pendingCLIPResults.push(msg);
                console.log("combineCLIPwithCLIP", clientSettings.combineCLIPwithCLIP, pendingCLIPResults.length)
                clientSettings.combineCLIPwithCLIP--;
                if (clientSettings.combineCLIPwithCLIP === 0) {
                    let jointResults = Array();
                    let jointResultsIdx = Array();
                    let jointScores = Array();

                    console.log("combineCLIPwithCLIP === 0", clientSettings.combineCLIPwithCLIP, pendingCLIPResults.length)

                    const target = pendingCLIPResults[pendingCLIPResults.length - 1];
                    const target_results = target.results;
                    const targetIdx = target.resultsidx;
                    const targetScores = target.scores;
                    console.log("target message?", target);


                    // iterate through all results
                    for (let result_id = 0; result_id < target_results.length; result_id++) {
                        const current_result = target_results[result_id];
                        const current_id = targetIdx[result_id];
                        const current_score = targetScores[result_id];
                        console.log("current_result", current_result, current_id, current_score)
                        const current_date = extractDateFromFilename(current_result);
                        console.log('date: ' + current_date);
                        let valid = true;
                        let last_pr_date = current_date;

                        // iterate through all previous results
                        for (let pr_id = pendingCLIPResults.length - 2; pr_id >= 0; pr_id--) {
                            const pr = pendingCLIPResults[pr_id];
                            console.log("check previous meta", pr_id, pr.results.length, pr.resultsidx.length, pr.scores.length);
                            const pr_results = pr.results;
                            const pr_resultsidx = pr.resultsidx;
                            const pr_scores = pr.scores;

                            if (valid === false) {
                                break;
                            }

                            let found = false;

                            // iterate through all result string in the clip result
                            for (let pr_result_id = 0; pr_result_id < pr_results.length; pr_result_id++) {
                                const pr_result = pr_results[pr_result_id];
                                const pr_id = pr_resultsidx[pr_result_id];
                                const pr_score = pr_scores[pr_result_id];
                                const pr_date = extractDateFromFilename(pr_result);

                                // check if we are in the same day
                                if (areSameDay(current_date, pr_date)) {
                                    console.log("compare success", current_date, pr_date, areSameDay(current_date, pr_date))
                                    // check if the previous result is later than the last previous result
                                    if (last_pr_date > pr_date) {
                                        last_pr_date = pr_date;
                                        found = true;
                                        break;
                                    }
                                }
                            }

                            if (found === false) {
                                valid = false;
                                break;
                            }
                        }

                        if (valid) { // add the result to the joint result if we have all valid prev results
                            console.log("valid result: " + current_result);
                            jointResults.push(current_result);
                            jointResultsIdx.push(current_id);
                            jointScores.push(current_score);
                        }
                    }
                    /*for (let r = 1; r < pendingCLIPResults.length - 1; r++) { // iterate through the results
                        console.log("check " + r + " " + pendingCLIPResults.length)
                        let tresPrev = pendingCLIPResults[r-1].results;
                        let tres = pendingCLIPResults[r].results; // string in format 201903/24/20190324_092645_000.jpg
                        let tresIdx = pendingCLIPResults[r].resultsidx; // id of image
                        let tresScores = pendingCLIPResults[r].scores; // score of image

                        for (let i = 0; i < tres.length; i++) { // iterate through each result
                            jointResults.push(tres[i]); // temporary to make it work
                            jointResultsIdx.push(tresIdx[i]); // temporary to make it work
                            jointScores.push(tresScores[i]); // temporary to make it work
                            let date = extractDateFromFilename(tres[i]);
                            console.log('date: ' + date);
                            let vid = getVideoId(tres[i]); // current video
                            let frame = extractFrameNumber(tres[i]); // get all frames in the video

                            for (let j = 0; j < tresPrev.length; j++) { // iterate through the previous result
                                let vidP = getVideoId(tresPrev[j]); //get the previous video
                                let frameP = extractFrameNumber(tresPrev[j]); //get the frames in the previous video

                                if (vid === vidP && frame > frameP) { // if the video is the same and the frame is greater than the previous frame

                                    let videoid = getVideoId(tres[i]); // isn't this the same as vid?
                                    if (clientSettings.videoFiltering === 'first' && videoIds.includes(videoid)) {
                                        countFiltered++;
                                        continue;
                                    }
                                    videoIds.push(videoid);

                                    jointResults.push(tres[i]);
                                    jointResultsIdx.push(tresIdx[i]);
                                    jointScores.push(tresScores[i]);
                                    console.log('found: ' + tres[i] + ': ' + vid + ' ' + frame + " > " + vidP + " " + frameP);
                                    break;
                                    // Not sure if this method just filter two subqueries. If we have
                                    // car < restaurant it should work as expected
                                    // but if we have bed < car < restaurant it's possible that we get results of
                                    // videos where we see a car and then a restaurant, but without a bed before?
                                    // because with that code we only check the previous subquery result, and not all previous results?
                                }

                        }
                    }
                    }*/
                    msg.results = jointResults;
                    msg.resultsidx = jointResultsIdx;
                    msg.scores = jointScores;
                    msg.totalresults = jointResults.length;
                    msg.num = jointResults.length;
                    msg.totalresults =  jointResults.length;
                    console.log('forwarding %d joint results to client %s', msg.totalresults, clientId);
                    pendingCLIPResults = Array();
                    clientWS.send(JSON.stringify(msg));
                }

            }
            else {

                if (filterCLIPResultsByDate === true || queryMode !== 'all') {
            
                    console.log('filter query');
                    let ly = year.toString().trim().length;
                    let lm = month.toString().trim().length;
                    let ld = day.toString().trim().length;
                    let lw = weekday.toString().trim().length;

                    const dateSet = new Set();
                
                    if (ly > 0 || lm > 0 || ld > 0 || lw > 0 || queryMode !== 'all') {
                        for (let i = 0; i < msg.results.length; i++) {
                            const elem = msg.results[i];
                            let eyear = elem.substring(0,4);
                            let emonth = elem.substring(4,6);
                            let eday = elem.substring(7,9);
                
                            if (ly > 0 && eyear !== year) {
                                msg.results.splice(i--, 1);
                            }
                            else if (lm > 0 && emonth !== month) {
                                msg.results.splice(i--, 1);
                            }
                            else if (ld > 0 && eday !== day) {
                                msg.results.splice(i--, 1);
                            }
                            else if (queryMode === 'first') {
                                let dateStr = eyear + emonth + eday;
                                if (dateSet.has(dateStr)) {
                                    msg.results.splice(i--,1);
                                } else {
                                    dateSet.add(dateStr);
                                }
                            }
                            else if (lw > 0) {
                                let dstr = eyear + '-' + emonth + '-' + eday;
                                let edate = new Date(dstr);
                                let wd = edate.getDay();
                                
                                if (weekdays[wd] === weekday) {
                                    msg.results.splice(i--, 1);
                                }
                            }
                        }
                    }
                }

                numafter = msg.results.length;
                if (numafter !== numbefore) {
                    msg.totalresults = msg.results.length;
                    msg.num = msg.results.length;
                }
                console.log('forwarding %d results (current before=%d after=%d) to client %s', msg.totalresults, numbefore, numafter, clientId);
                //console.log(JSON.stringify(msg));
                clientWS.send(JSON.stringify(msg));

                // Append jsonString to the file
                msg.clientId = clientId;
                fs.appendFile('lscqueryserverlog.json', JSON.stringify(msg), function (err) {
                    if (err) {
                        console.log('Error writing file', err)
                    }
                });
            }
            

        })

        clipWebSocket.on('error', (event) => {
            console.log('Connection to CLIP refused');
        });

    } catch(error) {
        console.log("Cannot connect to CLIP server");   
    }
}

connectToCLIPServer();




//////////////////////////////////////////////////////////////////
// MongoDB Queries
//////////////////////////////////////////////////////////////////

function connectMongoDB() {
    mongoclient = new MongoClient(mongouri);

    //connect to mongo
    mongoclient.connect((err) => {
        if (err) {
            console.error('error connecting to mongodb: ', err);
            return;
        }
    });

    mongoclient.on('close', () => {
        console.log('mongodb connection closed');
    });
}

async function queryImages(yearValue, monthValue, dayValue, weekdayValue, textValue, conceptValue, objectValue, placeValue, filenameValue, clientId) {
  try {
    if (!mongoclient.isConnected()) {
        console.log('mongodb not connected!');
        connectMongoDB();
    } else {
        const database = mongoclient.db('lsc'); // Replace with your database name
        const collection = database.collection('images'); // Replace with your collection name

        clientWS = clients.get(clientId);

        const sortCriteria = { minute_id: 1 }; //-1 for desc
        var { query, projection } = getMongoQuery(yearValue, monthValue, dayValue, weekdayValue, textValue, conceptValue, objectValue, placeValue, filenameValue); //-1 for desc

        if (JSON.stringify(query) === "{}") {
            console.log('empty query not allowed');
            let queryResults = { "num": 0, "totalresults": 0, "results": []  };
            clientWS.send(JSON.stringify(queryResults));

            // Append jsonString to the file
            queryResults.clientId = clientId;
            fs.appendFile('lscqueryserverlog.json', JSON.stringify(queryResults), function (err) {
                if (err) {
                    console.log('Error writing file', err)
                }
            });

            return queryResults;
        }

        console.log('mongodb query: %s', JSON.stringify(query));
        const cursor = collection.find(query, projection); //use sort(sortCriteria); //will give an array
        const count = await cursor.count();
        console.log('%d results to client %s', count, clientId);

        let processingInfo = {"type": "info",  "num": 1, "totalresults": 1, "message": count + " results in database, loading from server..."};
        clientWS.send(JSON.stringify(processingInfo));

        let queryResults = { "num": count, "totalresults": count };
        let results = [];

        const dateSet = new Set();

        await cursor.forEach(document => {
            // Access the filename field in each document
            const filename = document.filepath;

            if (queryMode === 'first') {
                let eyear = filename.substring(0,4);
                let emonth = filename.substring(4,6);
                let eday = filename.substring(7,9);
                let dateStr = eyear + emonth + eday;
                if (dateSet.has(dateStr) === false) {
                    results.push(filename);
                    dateSet.add(dateStr);
                } 
            } else {
                results.push(filename);
            }
            //console.log(filename);
        });

        queryResults.results = results;
        return queryResults;
    }
  } /*catch (error) {
    console.log("error with mongodb: " + error);
    await mongoclient.close();
  }*/ finally {
    // Close the MongoDB connection when finished
    //await mongoclient.close();
  }
}



function getMongoQuery(yearValue, monthValue, dayValue, weekdayValue, textValue, conceptValue, objectValue, placeValue, filenameValue) {
    let query = {};

    if (yearValue.toString().trim().length > 0) {
        query.year = parseInt(yearValue);
    }

    if (monthValue.toString().trim().length > 0) {
        query.month = parseInt(monthValue);
    }

    if (dayValue.toString().trim().length > 0) {
        query.day = parseInt(dayValue);
    }

    if (weekdayValue.toString().trim().length > 0) {
        query.weekday = weekdayValue;
    }

    if (textValue.toString().trim().length > 0) {
        if (textValue.includes(',')) {
            let texts = textValue.split(",");
            let text = { $all: texts };
            query['texts.text'] = text;
        } else {
            let text = { $elemMatch: { "text": { $regex: textValue, $options: 'i' } } };
            query.texts = text;
        }
    }

    if (conceptValue.toString().trim().length > 0) {
        if (conceptValue.includes(',')) {
            let concepts = conceptValue.split(",");
            let concept = { $all: concepts };
            query['concepts.concept'] = concept;
        } else {
            conceptValue = '^' + conceptValue + '$';
            let concept = { $elemMatch: { "concept": { $regex: conceptValue, $options: 'i' } } };
            query.concepts = concept;
        }
    }

    if (objectValue.toString().trim().length > 0) {
        if (objectValue.includes(',')) {
            let objects = objectValue.split(",");
            let obj = { $all: objects };
            query['objects.object'] = obj;
        } else {
            objectValue = '^' + objectValue + '$';
            let obj = { $elemMatch: { "object": { $regex: objectValue, $options: 'i' } } };
            query.objects = obj;
        }
    }

    if (placeValue.toString().trim().length > 0) {
        if (placeValue.includes(',')) {
            let places = placeValue.split(",");
            let place = { $all: places };
            query['places.place'] = place;
        } else {
            placeValue = '^' + placeValue + '$';
            let place = { $elemMatch: { "place": { $regex: placeValue, $options: 'i' } } };
            query.places = place;
        }
    }

    if (filenameValue.toString().trim().length > 0) {
        query.filename = { $regex: filenameValue, $options: 'i' };
    }

    if (queryMode === 'distinctive') {
        query.l2dist = { $gt: DISTINCTIVE_L2DIST1 };
    } else if (queryMode == 'moredistinctive') {
        query.l2dist = { $gt: DISTINCTIVE_L2DIST2 };
    }

    console.log(JSON.stringify(query));

    const projection = { filepath: 1 };

    return { query, projection };
}

async function queryImage(url) {
    try {
        if (!mongoclient.isConnected()) {
            console.log('mongodb not connected!');
            connectMongoDB();
        } else {
            const database = mongoclient.db('lsc'); // Replace with your database name
            const collection = database.collection('images'); // Replace with your collection name
        
            let query = { "filepath": url }; 
        
            console.log('mongodb query: %s', JSON.stringify(query));
            const cursor = collection.find(query);
        
            let queryResults = { "type": "metadata", "num": 1, "totalresults": 1 };
            let results = [];
        
            await cursor.forEach(document => {
                // Access the filename field in each document
                results.push(document);
                //console.log(filename);
            });
        
            queryResults.results = results;
            return queryResults;
        }
  
    } catch (error) {
        console.log("error with mongodb: " + error);
        await mongoclient.close();
    } finally {
      // Close the MongoDB connection when finished
      //await mongoclient.close();
    }
}


async function queryObjects(clientId) {
    try {
        if (!mongoclient.isConnected()) {
            console.log('mongodb not connected!');
            connectMongoDB();
        } else {
            const database = mongoclient.db('lsc'); // Replace with your database name
            const collection = database.collection('objects'); // Replace with your collection name
        
            const cursor = collection.find({},{name:1}).sort({name: 1});
            let results = [];
            await cursor.forEach(document => {
                results.push(document);
            });
            
            let response = { "type": "objects", "num": results.length, "results": results };
            clientWS = clients.get(clientId);
            clientWS.send(JSON.stringify(response));
            //console.log('sent back: ' + JSON.stringify(response));
        }
  
    } catch (error) {
        console.log("error with mongodb: " + error);
        await mongoclient.close();
    } finally {
      // Close the MongoDB connection when finished
      //await mongoclient.close();
    }
  }

  async function queryConcepts(clientId) {
    try {
        if (!mongoclient.isConnected()) {
            console.log('mongodb not connected!');
            connectMongoDB();
        } else {
            const database = mongoclient.db('lsc'); // Replace with your database name
            const collection = database.collection('concepts'); // Replace with your collection name
        
            const cursor = collection.find({},{name:1}).sort({name: 1});
            let results = [];
            await cursor.forEach(document => {
                results.push(document);
            });
            
            let response = { "type": "concepts", "num": results.length, "results": results };
            clientWS = clients.get(clientId);
            clientWS.send(JSON.stringify(response));
            //console.log('sent back: ' + JSON.stringify(response));
        }
  
    } catch (error) {
        console.log("error with mongodb: " + error);
        await mongoclient.close();
    } finally {
      // Close the MongoDB connection when finished
      //await mongoclient.close();
    }
  }

  async function queryPlaces(clientId) {
    try {
        if (!mongoclient.isConnected()) {
            console.log('mongodb not connected!');
            connectMongoDB();
        } else {
            const database = mongoclient.db('lsc'); // Replace with your database name
            const collection = database.collection('places'); // Replace with your collection name
        
            const cursor = collection.find({},{name:1}).sort({name: 1});
            let results = [];
            await cursor.forEach(document => {
                results.push(document);
            });
            
            let response = { "type": "places", "num": results.length, "results": results };
            clientWS = clients.get(clientId);
            clientWS.send(JSON.stringify(response));
            //console.log('sent back: ' + JSON.stringify(response));
        }
  
    } catch (error) {
        console.log("error with mongodb: " + error);
        await mongoclient.close();
    } finally {
      // Close the MongoDB connection when finished
      //await mongoclient.close();
    }
  }

  async function queryTexts(clientId) {
    try {
        if (!mongoclient.isConnected()) {
            console.log('mongodb not connected!');
            connectMongoDB();
        } else {
            const database = mongoclient.db('lsc'); // Replace with your database name
            const collection = database.collection('texts'); // Replace with your collection name
        
            const cursor = collection.find({},{name:1}).sort({name: 1});
            let results = [];
            await cursor.forEach(document => {
                results.push(document);
            });
            
            let response = { "type": "texts", "num": results.length, "results": results };
            clientWS = clients.get(clientId);
            clientWS.send(JSON.stringify(response));
            //console.log('sent back: ' + JSON.stringify(response));
        }
  
    } catch (error) {
        console.log("error with mongodb: " + error);
        await mongoclient.close();
    } finally {
      // Close the MongoDB connection when finished
      //await mongoclient.close();
    }
  }

