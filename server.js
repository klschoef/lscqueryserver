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

    app.get("/semanticnames", (req,res) => {
        filterSemanticnames(req, db, res);
    })
    
    app.get("/timenames", (req,res) => {
        filterTimenames(req, db, res);
    })

    app.get("/weekdays", (req,res) => {
        filterWeekdays(req, db, res);
    })

    app.get("/attributes", (req,res) => {
        filterAttributes(req, db, res);
    })

    app.get("/semanticlocations", (req,res) => {
        filterSemanticLocations(req, db, res);
    })

    app.get("/concepts", (req,res) => {
        filterConcepts(req, db, res);
    })

    app.get("/days", (req,res) => {
        filterDaySummaries(req, db, res);
    })

    app.get("/mstags", (req,res) => {
        filterTags(req, db, res);
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

function filterSemanticnames(req, db, res) {
    console.log(req.body);
    db.collection('semanticnames').aggregate([{ $sort: {semanticname: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " semanticnames");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterTimenames(req, db, res) {
    console.log(req.body);
    db.collection('timenames').aggregate([{ $sort: {timename: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " timenames");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterWeekdays(req, db, res) {
    console.log(req.body);
    db.collection('weekdays').aggregate([{ $sort: {weekday: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " weekdays");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterAttributes(req, db, res) {
    console.log(req.body);
    db.collection('attributes').aggregate([{ $sort: {attribute: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " attributes");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterSemanticLocations(req, db, res) {
    console.log(req.body);
    db.collection('attributes').aggregate([{ $sort: {attribute: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " attributes");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}

function filterTags(req, db, res) {
    console.log(req.body);
    db.collection('tags').aggregate([{ $sort: {concept: 1} }]).toArray().then((docs) => {
        console.log(Object.keys(docs).length + " tags");
        res.json(docs);
    }).catch((err) => {
        res.send(err);
        console.log(err);
    });
}


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
    db.collection('days').find({$and: [{day_id: {$gte: queryInput.from}},{day_id: {$lte: queryInput.to}}]}).toArray().then((docs) => {
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

    if (keys.includes("concepts")) {
        //db.images.find( { $and: [{ "concepts": { $elemMatch: {concept: "dorm_room", score: {$gte: 0.4} } } }, { "concepts": { $elemMatch: {concept: "hotel_room", score: {$gte: 0.1} } } }, { "objects": { $elemMatch: {object: "remote"} } } ]  } )
        if (Array.isArray(queryInput.concepts)) {
            let k=0;
            for (k=0; k < queryInput.concepts.length; k++) {
                let c = queryInput.concepts[k];
                let partQuery = {concepts: {$elemMatch: {concept: c.key, score: {$gte: c.score} }} };
                console.log("concept");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
            //query["concepts.concept"] = { $all: queryInput.concepts };
        }
        else {
            let partQuery =  {concepts: { $elemMatch: {concept: queryInput.concepts.key, score: {$gte: queryInput.concepts.score} } } }; //queryInput.concepts;
            console.log("final concept:");
            console.log(partQuery);
            queryArr.push(partQuery);
        }
    }

    if (keys.includes("mstags")) {
        if (Array.isArray(queryInput.mstags)) {
            let k=0;
            for (k=0; k < queryInput.mstags.length; k++) {
                let c = queryInput.mstags[k];
                let partQuery = {msconcepts: {$elemMatch: {concept: c.key, conf: {$gte: c.score} }} };
                console.log("mstag");
                console.log(partQuery);
                queryArr.push(partQuery);
            }
            //query["concepts.concept"] = { $all: queryInput.concepts };
        }
        else {
            let partQuery =  {msconcepts: { $elemMatch: {concept: queryInput.mstags.key, conf: {$gte: queryInput.mstags.score} } } }; //queryInput.concepts;
            console.log("final mstag:");
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
    
    let collection = 'images';
    if (keys.includes("reduced") && (queryInput.reduced == true || queryInput.reduced == 'true')) {
        collection = 'uniqueimages';
    }

    
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
