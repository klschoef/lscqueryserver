const mongo = require("mongodb");
const express = require("express");
const cors = require('cors');
const bodyParser = require('body-parser');
const {ObjectId} = require('mongodb'); //only for node version < 6: var ObjectId = require('mongodb').ObjectId

const app = express();
const port = 8080;
const MongoClient = mongo.MongoClient;

const url = 'mongodb://143.205.122.17';

app.use(cors());  
app.use('/dataset', express.static("../dataset/images"));
app.use('/dataset_thumbs', express.static("../dataset/thumbs"));


// bodyparser for sending different http request bodies
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

        switch (queryInput.type) {
            case "filter":
                filterQuery(queryInput, db, res);
                break;
            case "image":
                filterImage(queryInput, db, res);
                break;
            case "hours":
                filterHours(req, db, res);
                break;
            case "days":
                filterDays(req, db, res);
                break;
            case "objects":
                filterObjects(req, db, res);
                break;
            case "concepts":
                filterConcepts(req, db, res);
                break;
        }

    });

    app.get("/concepts", (req,res) => {
        filterConcepts(req, db, res);
    })

    app.get("/objects", (req,res) => {
        filterObjects(req, db, res);
    })

    app.get("/images", (req,res) => {
        db.collection('images').find({}).limit(5000).toArray().then((docs) => {
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

function filterConcepts(req, db, res) {
    console.log(req.body);
    db.collection('concepts').aggregate([{ $sort: {concept: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " concepts");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterObjects(req, db, res) {
    console.log(req.body);
    db.collection('objects').aggregate([{ $sort: {object: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " objects");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterDays(req, db, res) {
    console.log(req.body);
    db.collection('days').find({}).limit(1000).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " days");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterHours(req, db, res) {
    console.log(req.body);
    db.collection('hours').find({}).limit(1000).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " hours");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterQuery(queryInput, db, res) {
    let query = {};
    let keys = Object.keys(queryInput);
    if (keys.includes("date")) {
        query.minute_id = { $regex: queryInput.date + ".*" };
    }
    if (keys.includes("concepts")) {
        //db.images.find( { $and: [{ "concepts": { $elemMatch: {concept: "dorm_room", score: {$gte: 0.4} } } }, { "concepts": { $elemMatch: {concept: "hotel_room", score: {$gte: 0.1} } } }, { "objects": { $elemMatch: {object: "remote"} } } ]  } )
        if (Array.isArray(queryInput.concepts)) {
            query["concepts.concept"] = { $all: queryInput.concepts };
        }
        else {
            query["concepts.concept"] = queryInput.concepts;
        }
    }
    if (keys.includes("attributes")) {
        if (Array.isArray(queryInput.attributes)) {
            query.attributes = { $all: queryInput.attributes };
        }
        else {
            query.attributes = queryInput.attributes;
        }
    }
    if (keys.includes("objects")) {
        if (Array.isArray(queryInput.objects)) {
            query["objects.object"] = { $all: queryInput.objects };
        }
        else {
            query["objects.object"] = queryInput.objects;
        }
    }
    if (keys.includes("latitude") && keys.includes("longitude")) {
        let coord = [parseFloat(queryInput.longitude, parseFloat(queryInput.latitude))];
        query["location"] = {$near: {$geometry: {type: "Point", coordinates: coord}, $maxDistance: 10000 }};
    }
    console.log(query);
    db.collection('images').find(query).limit(100).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " elements");
        res.json(docs);
    }).catch((err) => {
        res.send({ error: err });
        console.log(err);
    });
}


function filterImage(queryInput, db, res) {
    let query = {};
    let keys = Object.keys(queryInput);

    query = {_id: ObjectId(queryInput._id) }; //ObjectId(queryInput._id)};

    console.log(query);
    db.collection('images').find(query).toArray().then((docs) => {
        let len = Object.keys(docs).length;
        console.log(len + " image");
        if (len == 1) {
            res.json(docs[0]);
        } else {
            res.json(docs);
        }
    }).catch((err) => {
        res.send({ error: err });
        console.log(err);
    });
}
