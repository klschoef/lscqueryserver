const mongo = require("mongodb");
const express = require("express");
const cors = require('cors');
const bodyParser = require('body-parser');

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
        }

    });

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
        if (Array.isArray(queryInput.concepts)) {
            query["concepts.concept"] = { $all: queryInput.concepts } };
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
            query["objects.object"] = { $all: queryInput.objects } };
        }
        else {
            query["objects.object"] = queryInput.objects;
        }
    }
    if (keys.includes("latitude") && keys.includes("longitude")) {
        query.location = { $near: { $geometry: { type: "Point", coordinates: [queryInput.longitude, queryInput.latitude] }, $maxDistance: 10000 } };
    }
    console.log(query);
    db.collection('images').find(query).limit(5000).toArray().then((docs) => {
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

    query._id = {_id: ObjectId(queryInput._id)};

    console.log(query);
    db.collection('images').find(query).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " image");
        res.json(docs);
    }).catch((err) => {
        res.send({ error: err });
        console.log(err);
    });
}
