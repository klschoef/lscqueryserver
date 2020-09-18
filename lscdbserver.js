const mongo = require("mongodb");
const express = require("express");

const app = express();
const port = 8080;
const MongoClient = mongo.MongoClient;

const url = 'mongodb://143.205.122.17';

app.use('/dataset', express.static("images"));

MongoClient.connect(url, {useNewUrlParser: true}, (err, client) => {
    if (err) throw err;

    const db = client.db("lsc");

    app.get("/", (req,res) => {
        res.send("It works, dude!");
    })

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