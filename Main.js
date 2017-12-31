
var express = require('express');
var app = express();
var store = require('app-store-scraper');
var request = require('request');
var PythonShell = require('python-shell');
var v = require('vectorious'),
    Matrix = v.Matrix,
    Vector = v.Vector,
    BLAS = v.BLAS;
var math = require('mathjs');

var allAppFeatures = { };
var message = {'success': false, 'reason': ''};
var combinedFeatures;

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


var debugMode = true;
app.get('/features', function(req, res){ 

	var apps = req.query.ids.split(',')
	var appId = apps[0];

	if (debugMode === true && combinedFeatures !== undefined) {
	  	res.set('Content-Type', 'application/json');
		res.send(combinedFeatures);
		return;
	}
		
	var appPromises = [];
	for (var i = 0; i < apps.length; i++) {
		appPromises.push(store.app({id: parseInt(apps[i])}));
	}

	Promise.all(appPromises).then(appValues => { 
		mineData(appValues, req, function (allFeatures) { 

			combinedFeatures = { 'data' : {} };
			var firstFeatures = allFeatures[apps[0]].features;
			var secondFeatures = allFeatures[apps[1]].features;

			var featureNamesToReturn = [];
			
			for (var firstFeatureIndex in firstFeatures) {
				var v1 = firstFeatures[firstFeatureIndex].cluster_mean;
				var similarFeatureFound = false;
				var similarityObject = {};

				for (var secondFeatureIndex in secondFeatures) {
					var v2 = secondFeatures[secondFeatureIndex].cluster_mean;
					var a = new Vector(v1),
		    			b = new Vector(v2);
					
				   	var normalizedA = new Vector(v1);
				   	var normalizedB = new Vector(v2);

				   	var result = Vector.dot(a, b) / (math.norm(v1) * math.norm(v2));
				   	if (result > 0.80) {
				   		similarFeatureFound = true;
						similarityObject[result] = secondFeatures[secondFeatureIndex].cluster_features;
					}
				}

				if (similarFeatureFound) {
					var mainClusterName = firstFeatures[firstFeatureIndex].cluster_name;
					featureNamesToReturn.push(mainClusterName);

					var secondAppFeatures = similarityObject[Math.max.apply(null, Object.keys(similarityObject))];
					
					combinedFeatures.data[mainClusterName] = {
						'firstFeatures': firstFeatures[firstFeatureIndex].cluster_features,
						'secondFeatures': secondAppFeatures
					};
				}
			}

			combinedFeatures['firstSentences'] = allFeatures[apps[0]].sentences;
			combinedFeatures['secondSentences'] = allFeatures[apps[1]].sentences;
			
			res.set('Content-Type', 'application/json');
			res.send(combinedFeatures);
			
			});
		});
});

app.get('/sentiments', function(req, res) {
	if (combinedFeatures === undefined) {
		sendFailure(res, 'features have not been mined');
		return;
	}		

	var url = "http://localhost:9000/?properties=%7B%22annotators%22:%20%22sentiment%22%7D&pipelineLanguage=en&timeout=30000";
	var features = req.query.features.split(',');

    var returnSentiments = {};
    var executedPromiseCount = 0;
    for (var i = 0; i < features.length; i++) {
        returnSentiments[features[i]] = combinedFeatures.data[features[i]];

        var firstAppSentimentPromises = [];
        var secondAppSentimentPromises = [];

        for (var sentenceKey in combinedFeatures.firstSentences) {
            var sentences = combinedFeatures.firstSentences[sentenceKey];
            for (var j in sentences) {
                //comparing all feature names included in the cluster
                for (var k in combinedFeatures.data[features[i]].firstFeatures) {
                	if (sentences[j].sentence_text.indexOf(combinedFeatures.data[features[i]].firstFeatures[k].feature) !== -1) {
                		firstAppSentimentPromises.push(httpPromisePostAsync(url, sentences[j].sentence_text, i));
                	}
                }
            }
        }

        for (var sentenceKey in combinedFeatures.secondSentences) {
            var sentences = combinedFeatures.secondSentences[sentenceKey];
            for (var j in sentences) {
            	//comparing all feature names included in the cluster
                for (var k in combinedFeatures.data[features[i]].secondFeatures) {
                	if (sentences[j].sentence_text.indexOf(combinedFeatures.data[features[i]].secondFeatures[k].feature) !== -1) {
                		secondAppSentimentPromises.push(httpPromisePostAsync(url, sentences[j].sentence_text, i));
                	}
                }
            }
        }

   		returnSentiments[features[i]].firstAppSentiments = [];
   		returnSentiments[features[i]].secondAppSentiments = [];

	    Promise.all(firstAppSentimentPromises).then(firstAppSentiments => {
	    	executedPromiseCount += 1;
	    	for (var i = 0; i < firstAppSentiments.length; i++) {
	    		var identifier = firstAppSentiments[i].identifier;
				var sentence = firstAppSentiments[i].sentence;
	    		var sentAverage = 0;
	    		for (var j = 0; j < firstAppSentiments[i].sentences.length; j++) {
	    			sentAverage += parseInt(firstAppSentiments[i].sentences[j].sentimentValue);
	    		}
	    		sentAverage /= firstAppSentiments[i].sentences.length;

	    		returnSentiments[features[identifier]].firstAppSentiments.push( { 
	    			'sentence': sentence,
	    			'sentiment': sentAverage
	    		});

	    		if (executedPromiseCount/2 === features.length) {
	    			res.set('Content-Type', 'application/json');	
					res.send(returnSentiments);
	    		}
	    	}
	    });

	    Promise.all(secondAppSentimentPromises).then(secondAppSentiments => {
	    		executedPromiseCount += 1;
		    	for (var i = 0; i < secondAppSentiments.length; i++) {
		    		var identifier = secondAppSentiments[i].identifier;
					var sentence = secondAppSentiments[i].sentence;
		    		var sentAverage = 0;

		    		for (var j = 0; j < secondAppSentiments[i].sentences.length; j++) {
		    			sentAverage += parseInt(secondAppSentiments[i].sentences[j].sentimentValue);
		    		}
		    		sentAverage /= secondAppSentiments[i].sentences.length;

		    		returnSentiments[features[identifier]].secondAppSentiments.push( { 
		    			'sentence': sentence,
		    			'sentiment': sentAverage
		    		});
	    		}

	    		if (executedPromiseCount/2 === features.length) {
	    			res.set('Content-Type', 'application/json');	
					res.send(returnSentiments);
	    		}
	    });
	}
});


function httpPromisePostAsync(theUrl, requestBody, identifier) {
	return new Promise(function(resolve, reject) { 
		request.timeout = 30000;
		request.post(theUrl, { json: JSON.stringify(requestBody) },
		    function (error, response, body) {
		        if (!error && response.statusCode == 200) {
		        	body.sentence = requestBody;
		        	body.identifier = identifier;
		            resolve(body);
		        } else {
		        	reject(Error(error));
		        }
		    }
		);
	});
}

function httpPostAsync(theUrl, requestBody, callback) {
	request.timeout = 30000;
	request.post(theUrl, { json: JSON.stringify(requestBody) },
	    function (error, response, body) {
	        if (!error && response.statusCode == 200) {
	        	var r = response;
	        	r.sentence = requestBody;
	            callback(r);
	        } else {
	        	reject(Error(error));
	        }
	    }
	);
}

function sendFailure(res, reason) {
	res.set('Content-Type', 'application/json');
	message.success = false;
	message.reason = reason;
	res.send();
}

function mineData(appValues, req, callback) {
	console.log("mindeData() begining: " + appValues.length);
	if (appValues.length == 0) {
		console.log("returned");
		callback(allAppFeatures);
		return;
	}

	var app = appValues[0];

	var promises = [];
	
	for (var i = 0; i < 6; i++) {
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

function getCombitation(arrays, combine = [], finalList = []) {
    if (!arrays.length) {
        finalList.push(combine);
    } else {
        arrays[0].forEach(now => {
            let nextArrs = arrays.slice(1);
            let copy = combine.slice();
            copy.push(now);
            getCombitation(nextArrs, copy, finalList);
        });
    }
    return finalList;
}



