
var express = require('express');
var app = express();
var store = require('app-store-scraper');
var PythonShell = require('python-shell');
var v = require('vectorious'),
    Matrix = v.Matrix,
    Vector = v.Vector,
    BLAS = v.BLAS;
var math = require('mathjs');

var allAppFeatures = { };

app.listen(8081);
app.set('json spaces', 2);
var modeEnum = {
	AppDescription: 1,
	AppReviews: 2
};

app.get('/', function(req, res){
    res.send('API runninng on localhost:8081/');
});

app.get('/categories', function(req, res){ 
	res.set('Content-Type', 'application/json');	  
	res.send(store.category)
});

app.get('/apps', function(req, res){
   	store.list({
		category: parseInt(req.query.category),
		num: 100
	  }).then(function(result) {
		res.set('Content-Type', 'application/json');	  
		
		var promises = [];
		for (var i = 0; i < result.length; i++) {
			var promise = store.app({id: parseInt(result[i].id)})
			promises.push(promise);
		}

		Promise.all(promises).then(values => { 
			for (var i = 0; i< values.length; i++) {
				result[i].version = values[i].version;
			}	
			res.send(result)
		});
	});
});

app.get('/app', function(req, res){
	var promises = [];
	for (var i = 0; i< 10; i++) {
		var promise = store.reviews({
			id: req.query.id,
			sort: store.sort.HELPFUL,
			page: i
			});

		promises.push(promise);
	}

	Promise.all(promises).then(values => { 
		res.set('Content-Type', 'application/json');
		values = [].concat.apply([], values)
		var reviews = {
			id: req.query.id,
			review_list: values
		};
		console.log("success");
		res.send(reviews);
	});
 });

app.get('/app/description', function(req, res){
	res.set('Content-Type', 'application/json');
	store.app({id: parseInt(req.query.id)}).then(values => {  
		res.send({ 
			id: req.query.id,
			description: values.description
		});
	});
});

var cachedMessage;
var debugMode = true;

app.get('/features', function(req, res){ 
	console.log(req.url);
	var apps = req.query.ids.split(',')
	var appId = apps[0];

	if (debugMode === true && cachedMessage !== undefined) {
	  	res.set('Content-Type', 'application/json');
		res.send(cachedMessage);
		return;
	}
		
	var appPromises = [];
	for (var i = 0; i < apps.length; i++) {
		appPromises.push(store.app({id: parseInt(apps[i])}));
	}

	Promise.all(appPromises).then(appValues => { 
		mineData(appValues, req, function (allFeatures) { 

			//np.dot(v1, v2) / (LA.norm(v1) * LA.norm(v2))
			var firstFeatures = allFeatures[apps[0]].features;
			var secondFeatures = allFeatures[apps[1]].features;
			for (var firstFeatureIndex in firstFeatures) {
				var v1 = firstFeatures[firstFeatureIndex].cluster_mean;
				for (var secondFeatureIndex in secondFeatures) {
					var v2 = secondFeatures[secondFeatureIndex].cluster_mean;
					var a = new Vector(v1),
		    			b = new Vector(v2);
					
				   	var normalizedA = new Vector(v1);
				   	var normalizedB = new Vector(v2);

					console.log(Vector.dot(a, b) / (math.norm(v1) * math.norm(v2)));
					console.log(firstFeatures[firstFeatureIndex].cluster_name);
					console.log(secondFeatures[secondFeatureIndex].cluster_name);
				}
			}

			cachedMessage = allFeatures;
			res.set('Content-Type', 'application/json');
			res.send(allFeatures);
			});
		});
});


function mineData(appValues, req, callback) {
	console.log("mindeData() begining: " + appValues.length);
	if (appValues.length == 0) {
		console.log("returned");
		callback(allAppFeatures);
		return;
	}

	var app = appValues[0];

	var promises = [];
	
	for (var i = 0; i < 1; i++) {
	var promise = store.reviews({
		id: app.id,
		sort: store.sort.HELPFUL,
		page: i
		});

		promises.push(promise);
	}

	Promise.all(promises).then(values => { 
		values = [].concat.apply([], values)
		console.log("logged reviews: " + values.length)

		var dataToExtract = [{
			appID : app.id,
			name : app.title,
			description : app.description,
			reviews: values,
			appDescThreshold: parseFloat(req.query.desc_threshold),
			featureThreshold: parseFloat(req.query.feature_threshold)
		}];

		var options = {
			mode: 'json',
			pythonPath: '/usr/local/bin/python3'
		};

		var pyshell = new PythonShell('feature-extraction/SAFE.py', options);
		pyshell.send(dataToExtract);

		pyshell.on('message', function (message) {
			console.log("before shifting: " + appValues.length);
			appValues.shift();
			console.log("after shifting: " + appValues.length);
			allAppFeatures[app.id] = message;
		});

		pyshell.end(function (err) {
			if (err){ console.log(err); }
			console.log("finished");
			mineData(appValues, req, callback);
		});
	});
}

app.get("/app/name" , function(req, res) {  
	res.set('Content-Type', 'application/json');
	store.app({id: parseInt(req.query.id)}).then(values => {  
		
		res.send({ 
			id: req.query.id,
			description: values.title
		});
	});
});

console.log('Server running at localhost:8081/');


