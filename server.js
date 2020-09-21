const mongo = require("mongodb");
const express = require("express");

const app = express();
const port = 8080;
const MongoClient = mongo.MongoClient;

const url = 'mongodb://143.205.122.17';


app.use('/dataset', express.static("dataset"));
app.use('/dataset_thumbs', express.static("dataset_thumbs"));


// bodyparser for sending different http request bodies
let bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));     // support encoded bodies
app.use(bodyParser.json());                             // support json encoded bodies


MongoClient.connect(url, {useNewUrlParser: true}, (err, client) => {
    if (err) throw err;

    const db = client.db("lsc");

    app.get("/", (req,res) => {
        res.send("It works, dude!");
    })

    // body parameters
    app.post("/query", (req, res) => {
        console.log(req.body);

        let queryInput = req.body;

        let query = {};
        let keys = Object.keys(queryInput);

        if (keys.includes("date")) {
            query.minute_id = {$regex: queryInput.date + ".*"};
        }

        if (keys.includes("concepts")) {
            if (Array.isArray(queryInput.concepts)) {
                query.concepts = {$all: queryInput.concepts};
            } else {
                query.concepts = queryInput.concepts;
            }
        }

        if (keys.includes("attributes")) {
            if (Array.isArray(queryInput.attributes)) {
                query.attributes = {$all: queryInput.attributes};
            } else {
                query.attributes = queryInput.attributes;
            }
        }
        
        if (keys.includes("objects")) {
            if (Array.isArray(queryInput.objects)) {
                query.objects = {$all: queryInput.objects};
            } else {
                query.objects = queryInput.objects;
            }
        }

        if (keys.includes("latitude") && keys.includes("longitude")) {
            query.location = {$near: {$geometry: {type: "Point", coordinates: [queryInput.longitude, queryInput.latitude]}, $maxDistance: 10000} }
        }

        console.log(query);

        db.collection('images').find(query).limit(100).toArray().then((docs) => {
            res.json(docs);
        }).catch((err) => {
            res.send(err);
            console.log(err);
        });

    });

    app.get("/images", (req,res) => {
        db.collection('images').find({}).limit(100).toArray().then((docs) => {
            res.json(docs);
        }).catch((err) => {
            res.send(err);
            console.log(err);
        });
    })

    app.get("/hours", (req,res) => {
        db.collection('hours').find({}).limit(100).toArray().then((docs) => {
            res.json(docs);
        }).catch((err) => {
            res.send(err);
            console.log(err);
        });
    })

    app.get("/days", (req,res) => {
        db.collection('days').find({}).limit(100).toArray().then((docs) => {
            res.json(docs);
        }).catch((err) => {
            res.send(err);
            console.log(err);
        });
    })

    app.listen(port, () => {
        console.log("LSC database server listenting at " + url + ":" + port);
    })
    
    /*db.collection('images').find({}).toArray().then((docs) => {
        console.log(docs);
    }).catch((err) => {
        console.log(err);
    }).finally(() => {
        client.close();
    });*/
});