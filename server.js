const mongo = require("mongodb");
const express = require("express");
const cors = require('cors');
const bodyParser = require('body-parser');
const {ObjectId} = require('mongodb'); //only for node version < 6: var ObjectId = require('mongodb').ObjectId


const app = express();
const port = 8080;
const MongoClient = mongo.MongoClient;

const url = 'mongodb://extreme00.itec.aau.at'; //'mongodb://143.205.122.17';

app.use(cors());  
//app.use('/images', express.static("../dataset/images"));
//app.use('/thumbs', express.static("../dataset/thumbs"));


// bodyparser for sending different http request bodies
app.use(bodyParser.urlencoded({ extended: true }));     // support encoded bodies
app.use(bodyParser.json());                             // support json encoded bodies


MongoClient.connect(url, {useNewUrlParser: true}, (err, client) => {
    if (err) throw err;

    const db = client.db("lsc");

    app.get("/", (req,res) => {
        res.send("It has never been working better, dude!");
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
            case "days":
                filterDays(queryInput, db, res);
                break;
            case "objects":
                filterObjects(req, db, res);
                break;
            case "concepts":
                filterConcepts(req, db, res);
                break;
        }

    });

    app.get("/semanticnames", (req,res) => { //ok
        filterAnything(req, db, res, "$semanticname");
    })
    
    app.get("/timenames", (req,res) => {
        filterAnything(req, db, res, "$timename");
    })

    app.get("/weekdays", (req,res) => { //ok
        filterAnything(req, db, res, "$weekday");
    })

    app.get("/concepts", (req,res) => { //ok
        filterAnything(req, db, res, "$concepts.concept");
    })

    app.get("/places", (req,res) => { //ok
        filterAnything(req, db, res, "$places.place");
    })

    app.get("/songs", (req,res) => { //ok
        filterAnything(req, db, res, "$song");
    })

    app.get("/timezones", (req,res) => { //ok
        filterAnything(req, db, res, "$time_zone");
    })

    app.get("/heartrates", (req,res) => { //ok
        filterAnything(req, db, res, "$heart_rate");
    })

    app.get("/captions", (req,res) => { //ok
        filterAnything(req, db, res, "$mscaption");
    })

    app.get("/years", (req,res) => { //ok
        filterAnything(req, db, res, "$year");
    })

    app.get("/months", (req,res) => { //ok
        filterAnything(req, db, res, "$month");
    })

    app.get("/calendardays", (req,res) => { //ok
        filterAnything(req, db, res, "$day");
    })

    app.get("/dates", (req,res) => { //ok
        filterAnything(req, db, res, "$date");
    })

    app.get("/days", (req,res) => {
        filterDaySummaries(req, db, res);
    })

    app.get("/objects", (req,res) => { //ok
        filterAnything(req, db, res, "$objects.object");
    })

    app.get("/texts", (req,res) => { //ok
        filterAnything(req, db, res, "$texts.text");
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
    //db.collection('concepts').aggregate([{ $sort: {concept: 1} }]).toArray().then((docs) => {
    db.collection('images').aggregate([ {$match: {}}, {$group: {_id: "$concepts.concept", count: {$sum: 1}}}, {$sort: {_id:1}} ], {allowDiskUse:true} ).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " concepts");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterAnything(req, db, res, name) {
    console.log(req.body);
    db.collection('images').aggregate([ {$match: {}}, {$group: {_id: name, count: {$sum: 1}}}, {$sort: {_id:1}} ], {allowDiskUse:true} ).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " " + name);
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterObjects(req, db, res) {
    console.log(req.body);
    //db.collection('objects').aggregate([{ $sort: {object: 1} }]).toArray().then((docs) => {
    db.collection('images').aggregate([ {$match: {}}, {$group: {_id: "$objects.object", count: {$sum: 1}}}, {$sort: {_id:1}} ], {allowDiskUse:true} ).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " objects");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterDaySummaries(req, db, res) {
    console.log(req.body);
    db.collection('days').aggregate([{ $sort: {object: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " days");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterDays(queryInput, db, res) {
    console.log(queryInput);
    db.collection('days').find({$and: [{minute_id: {$gte: queryInput.from}},{minute_id: {$lte: queryInput.to}}]}).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " days");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}



function filterQuery(queryInput, db, res) {
    let query = {};
    let keys = Object.keys(queryInput);

    console.log("***************** NEW QUERY *****************");
    console.log(queryInput);
    console.log("keys:");
    console.log(keys);
    
    let queryArr = [];

    //{filename: {$in: ["20190102_091905_000"] } }

    if (keys.includes("images")) {
        if (Array.isArray(queryInput.images)) {
            let partQuery = {filename: {$in: queryInput.images } }
            console.log("images");
            console.log(partQuery);
            queryArr.push(partQuery);
        } else {
            let partQuery = {filename: {$in: [queryInput.images] } }
            console.log("image");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("concepts")) {
        if (Array.isArray(queryInput.concepts)) {
            let k=0;
            for (k=0; k < queryInput.concepts.length; k++) {
                let c = queryInput.concepts[k];
                let partQuery = {places: { $elemMatch: {place: c.key, score: {$gte: c.score} } } };
                console.log("concept");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
            //query["concepts.concept"] = { $all: queryInput.concepts };
        }
        else {
            let partQuery =  {places: {$elemMatch: {place: queryInput.concepts.key, score: {$gte: queryInput.concepts.score} } } }; //queryInput.concepts;
            console.log("final concept:");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("texts")) {
        if (Array.isArray(queryInput.texts)) {
            let k=0;
            for (k=0; k < queryInput.texts.length; k++) {
                let c = queryInput.texts[k];
                let partQuery = {texts: {$elemMatch: {text: c }} };
                console.log("concept");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
        }
        else {
            let partQuery =  {texts: { $elemMatch: {text: queryInput.texts} } }; //queryInput.concepts;
            console.log("final text:");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("objects")) {
        if (Array.isArray(queryInput.objects)) {
            let k=0;
            for (k=0; k < queryInput.objects.length; k++) {
                let o = queryInput.objects[k];
                let partQuery = {objects: { $elemMatch: {object: o.key, score: {$gte: o.score} }} };
                console.log("object:");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
        }
        else {
            let partQuery = {objects: { $elemMatch: {object: queryInput.objects.key, score: {$gte: queryInput.objects.score} } } };
            console.log("final object:");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("attributes")) {
        if (Array.isArray(queryInput.attributes)) {
            let k=0;
            for (k=0; k < queryInput.attributes.length; k++) {
                let a = queryInput.attributes[k];
                let partQuery = {attributes: a};
                console.log("attribute:");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
        }
        else {
            let partQuery = {attributes: queryInput.attributes};
            console.log("final attribute:");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("date")) {
        let partQuery = {minute_id: {$regex: queryInput.date + ".*"} };
        console.log("date: ");
        console.log(partQuery);
        queryArr.push(partQuery);
    }

    if (keys.includes("timenames")) {
        if (Array.isArray(queryInput.timenames)) {
            let subqueries = [];
            console.log("timenames: ");
            let k=0;
            for (k=0; k < queryInput.timenames.length; k++) {
                let subquery = {timename: queryInput.timenames[k]};
                console.log(subquery);
                subqueries.push(subquery);
            }
            let partQuery = {$or: subqueries};
            queryArr.push(partQuery);
        } else {
            let partQuery = {timename: queryInput.timenames};
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("weekdays")) {
        if (Array.isArray(queryInput.weekdays)) {
            let subqueries = [];
            console.log("weekdays: ");
            let k=0;
            for (k=0; k < queryInput.weekdays.length; k++) {
                let subquery = {weekday: queryInput.weekdays[k]};
                console.log(subquery);
                subqueries.push(subquery);
            }
            let partQuery = {$or: subqueries};
            queryArr.push(partQuery);
        } else {
            let partQuery = {weekday: queryInput.weekdays};
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("latitude") && keys.includes("longitude")) {
        let radius = 30;
        if (keys.includes("radius")) {
            radius = parseInt(queryInput.radius);
        }
        let partQuery = {location:  {$near: { $geometry: { type: "Point", coordinates: [parseFloat(queryInput.longitude), parseFloat(queryInput.latitude)] }, $maxDistance: radius } } }; //within <radius> meters
        console.log("location:");
        console.log(partQuery);
        queryArr.push(partQuery);
    }

    if (keys.includes("locations")) {
        if (Array.isArray(queryInput.locations)) {
            let subqueries = [];
            console.log("semantic locations:");
            let k=0;
            for (k=0; k < queryInput.locations.length; k++) {
                let subquery = {semanticname: {$regex: new RegExp(".*" + queryInput.locations[k] + ".*", "i")}};
                console.log(subquery);
                subqueries.push(subquery);
            }
            let partQuery = {$or: subqueries};
            queryArr.push(partQuery);
        } else {
            let partQuery = {semanticname: {$regex: new RegExp(".*" + queryInput.locations + ".*", "i")}};
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("captions")) {
        if (Array.isArray(queryInput.captions)) {
            let subqueries = [];
            console.log("microsoft captions:");
            let k=0;
            for (k=0; k < queryInput.captions.length; k++) {
                let subquery = {mscaption: {$regex: new RegExp(".*" + queryInput.captions[k] + ".*", "i")}};
                console.log(subquery);
                subqueries.push(subquery);
            }
            let partQuery = {$or: subqueries};
            queryArr.push(partQuery);
        } else {
            let partQuery = {mscaption: {$regex: new RegExp(".*" + queryInput.captions + ".*", "i")}};
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("songs")) {
        if (Array.isArray(queryInput.songs)) {
            let subqueries = [];
            console.log("songs:");
            let k=0;
            for (k=0; k < queryInput.songs.length; k++) {
                let subquery = {song: {$regex: new RegExp(".*" + queryInput.songs[k] + ".*", "i")}};
                console.log(subquery);
                subqueries.push(subquery);
            }
            let partQuery = {$or: subqueries};
            queryArr.push(partQuery);
        } else {
            let partQuery = {song: {$regex: new RegExp(".*" + queryInput.songs + ".*", "i")}};
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    let collection = 'images';
    if (keys.includes("reduced") && (queryInput.reduced == true || queryInput.reduced == 'true')) {
        //collection = 'uniqueimages';
        let partQuery = {reduced: false}
        queryArr.push(partQuery);
    }

    if (queryArr.length > 0) {
        query = {$and: queryArr};
    }

    let limit = 5000;
    if (keys.includes("limit")) {
        limit = parseInt(queryInput.limit);
	console.log("limit set to: " + limit);
    }

    console.log("---------------------------------");
    console.log(query);
    console.log("--------------------------------- (" + limit + ")");

    
    db.collection(collection).find(query).limit(limit).sort({time: 1}).toArray().then((docs) => {
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
