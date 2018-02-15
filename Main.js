
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
		res.send(result)
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


var debugMode = false;
app.get('/features', function(req, res){ 

	var apps = req.query.ids.split(',')
	console.log(req.url);

	if (apps.length === 1 && apps[0] === '') {
		sendFailure(res, 'One or Two apps should be selected')	
		return;
	}

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
		//empty global variable not to save previously requested data
		allAppFeatures = { };
		mineData(appValues, req, function (allFeatures) { 
			res.set('Content-Type', 'application/json');
			console.log(apps.length);
			if (apps.length === 2) {
				res.send(getTwoAppsFeatures(allFeatures, apps));
			} else if (apps.length === 1) {
				res.send(getOneAppFeatures(allFeatures, apps));
			} else {
				sendFailure(res, 'One or Two apps should be selected')	
			}
		});
	});
});

function getOneAppFeatures(allFeatures, apps) {
	combinedFeatures = { 'data' : { } };
	combinedFeatures.comparison = false;
	combinedFeatures.firstAppName = allFeatures[apps[0]].appName;

	var firstFeatures = allFeatures[apps[0]].features;
	var featuresToReturn = [];

	for (var firstFeatureIndex in firstFeatures) { 
		var mainClusterName = firstFeatures[firstFeatureIndex].cluster_name;

		combinedFeatures.data[mainClusterName] = {
			'firstFeatures': firstFeatures[firstFeatureIndex].cluster_features
		};

		var cluster = {
			'cluster_name' : mainClusterName,
			'features': combinedFeatures.data[mainClusterName].firstFeatures.map(f => f.feature)
		};

		featuresToReturn.push(cluster);
	}

	combinedFeatures['firstSentences'] = allFeatures[apps[0]].sentences;

	return featuresToReturn;
}

function getTwoAppsFeatures(allFeatures, apps) {
	combinedFeatures = { 'data' : { } };
	combinedFeatures.comparison = true;
	combinedFeatures.firstAppName = allFeatures[apps[0]].appName;
	combinedFeatures.secondAppName = allFeatures[apps[1]].appName;

	var firstFeatures = allFeatures[apps[0]].features;
	var secondFeatures = allFeatures[apps[1]].features;

	var featuresToReturn = [];
	
	for (var firstFeatureIndex in firstFeatures) {
		var v1 = firstFeatures[firstFeatureIndex].cluster_mean;
		var similarFeatureFound = false;
		var secondAppFeatures = [];

		for (var secondFeatureIndex in secondFeatures) {
			var v2 = secondFeatures[secondFeatureIndex].cluster_mean;
			var a = new Vector(v1),
    			b = new Vector(v2);
			
		   	var normalizedA = new Vector(v1);
		   	var normalizedB = new Vector(v2);

		   	var result = Vector.dot(a, b) / (math.norm(v1) * math.norm(v2));
		   	if (result > 0.80) {
		   		similarFeatureFound = true;
				secondAppFeatures = secondAppFeatures.concat(secondFeatures[secondFeatureIndex].cluster_features);
			}
		}

		if (similarFeatureFound) {
			console.log("130 - first app features length: " + firstFeatures[firstFeatureIndex].cluster_features.length);
			console.log("130 - second app features length: " + secondAppFeatures.length);

			var mainClusterName = firstFeatures[firstFeatureIndex].cluster_name;

			combinedFeatures.data[mainClusterName] = {
				'firstFeatures': firstFeatures[firstFeatureIndex].cluster_features,
				'secondFeatures': secondAppFeatures
			};

			var ff = combinedFeatures.data[mainClusterName].firstFeatures.map(f => f.feature);
			var sf = combinedFeatures.data[mainClusterName].secondFeatures.map(f => f.feature);
			var cluster = {
				'cluster_name' : mainClusterName,
				'features': ff.concat(sf)
			};

			featuresToReturn.push(cluster);
		}
	}

	combinedFeatures['firstSentences'] = allFeatures[apps[0]].sentences;
	combinedFeatures['secondSentences'] = allFeatures[apps[1]].sentences;

	return featuresToReturn;
}


app.get('/reviews', function(req, res) {
	var promises = [];
	
	for (var i = 0; i < 10; i++) {
		var promise = store.reviews({
			id: req.query.id,
			sort: store.sort.HELPFUL,
			page: i
			});

			promises.push(promise);
	}
	
	Promise.all(promises).then(values => { 
		values = [].concat.apply([], values)
		res.set('Content-Type', 'application/json');
		res.send(values);
	});

});

app.get('/sentiments', function(req, res) {
	console.log(req.url);

	if (combinedFeatures === undefined) {
		sendFailure(res, 'features have not been mined');
		return;
	}		

	var url = "http://localhost:9000/?properties=%7B%22annotators%22:%20%22sentiment%22%7D&pipelineLanguage=en&timeout=30000";
	var features = req.query.features.split(',');

	if (combinedFeatures.comparison) {
		handleTwoAppSentiments(res, features, url);
	} else {
		handleOneAppSentiments(res, features, url);
	}
});

function round(num) {
  num = Math.round(num+'e'+2)
  return Number(num+'e-'+2)
}

function handleTwoAppSentiments(res, features, url) {
	var returnSentiments = { };
    var executedPromiseCount = 0;
    for (var i = 0; i < features.length; i++) {
        returnSentiments[features[i]] = combinedFeatures.data[features[i]];
        returnSentiments[features[i]].firstAppName = combinedFeatures.firstAppName;
        returnSentiments[features[i]].comparison = true;
		returnSentiments[features[i]].secondAppName = combinedFeatures.secondAppName;
		returnSentiments[features[i]].firstAppSentimentAverage = 0;
		returnSentiments[features[i]].secondAppSentimentAverage = 0;

        var firstAppSentimentPromises = [];
        var secondAppSentimentPromises = [];
        var firstAppSentences = [];
        var secondAppSentences = [];

        for (var sentenceKey in combinedFeatures.firstSentences) {
            var sentences = combinedFeatures.firstSentences[sentenceKey];
            for (var j in sentences) {
                //comparing all feature names included in the cluster
                for (var k in combinedFeatures.data[features[i]].firstFeatures) {
	            	for (var extractedFeatureIndex in sentences[j].extracted_features) {
	            		if (combinedFeatures.data[features[i]].firstFeatures[k].feature === sentences[j].extracted_features[extractedFeatureIndex] &&
	            			firstAppSentences.indexOf(sentences[j].sentence_text) == -1) {
	            			firstAppSentimentPromises.push(httpPromisePostAsync(url, sentences[j].sentence_text, i));
	                		firstAppSentences.push(sentences[j].sentence_text);
	            		}
	            	}
            	}
            }
        }

        for (var sentenceKey in combinedFeatures.secondSentences) {
            var sentences = combinedFeatures.secondSentences[sentenceKey];
            for (var j in sentences) {
            	//comparing all feature names included in the cluster
                for (var k in combinedFeatures.data[features[i]].secondFeatures) {
	            	for (var extractedFeatureIndex in sentences[j].extracted_features) {
	            		if (combinedFeatures.data[features[i]].secondFeatures[k].feature === sentences[j].extracted_features[extractedFeatureIndex] &&
	            			secondAppSentences.indexOf(sentences[j].sentence_text) == -1) {
	            			secondAppSentimentPromises.push(httpPromisePostAsync(url, sentences[j].sentence_text, i));
	                		secondAppSentences.push(sentences[j].sentence_text);
	            		}
	            	}
            	}
            }
        }

   		returnSentiments[features[i]].firstAppSentiments = [];
   		returnSentiments[features[i]].secondAppSentiments = [];

	    Promise.all(firstAppSentimentPromises).then(firstAppSentiments => {
	    	if (firstAppSentiments.length > 0) {
	    		console.log('first app sentiments for: \'' + features[firstAppSentiments[0].identifier] + '\' retrieved' );	
	    	}

	    	for (var i = 0; i < firstAppSentiments.length; i++) {
	    		var identifier = firstAppSentiments[i].identifier;
				var sentence = firstAppSentiments[i].sentence;
	    		var sentAverage = 0;

	    		if (returnSentiments[features[identifier]].firstAppSentimentAverage === undefined) {
	    			returnSentiments[features[identifier]].firstAppSentimentAverage = 0;
	    		}

	    		for (var j = 0; j < firstAppSentiments[i].sentences.length - 1; j++) {
	    			sentAverage += parseInt(firstAppSentiments[i].sentences[j].sentimentValue);
	    		}

	    		sentAverage /= (firstAppSentiments[i].sentences.length - 1);
	    		sentAverage = round(sentAverage);
				//if sentiment is NaN assume it as normal
	    		if (sentAverage !== sentAverage) {
	    			sentAverage = 2;	
	    		}

	    		returnSentiments[features[identifier]].firstAppSentiments.push( { 
	    			'sentence': sentence,
	    			'sentiment': sentAverage
	    		});

    			returnSentiments[features[identifier]].firstAppSentimentAverage += sentAverage;
    			
    			if (i === firstAppSentiments.length - 1) { 
					returnSentiments[features[identifier]].firstAppSentimentAverage /= firstAppSentiments.length;
					returnSentiments[features[identifier]].firstAppSentimentAverage = round(returnSentiments[features[identifier]].firstAppSentimentAverage);
				}
	    	}

	    	

    		executedPromiseCount += 1;
    		if (executedPromiseCount / 2 === features.length && executedPromiseCount % 2 === 0) {
    			console.log('finished sentiment analysis');
    			executedPromiseCount = 0;
    			
    			res.set('Content-Type', 'application/json');
				res.send(returnSentiments);
    		}
	    });

	    Promise.all(secondAppSentimentPromises).then(secondAppSentiments => {
	    		if (secondAppSentiments.length > 0) {
	    			console.log('second app sentiments for: ' + features[secondAppSentiments[0].identifier] + ' retrieved' )	
	    		}

		    	for (var i = 0; i < secondAppSentiments.length; i++) {
		    		var identifier = secondAppSentiments[i].identifier;
					var sentence = secondAppSentiments[i].sentence;
		    		var sentAverage = 0;

		    		if (returnSentiments[features[identifier]].secondAppSentimentAverage === undefined) {
	    				returnSentiments[features[identifier]].secondAppSentimentAverage = 0;
	    			}

		    		for (var j = 0; j < secondAppSentiments[i].sentences.length; j++) {
		    			sentAverage += parseInt(secondAppSentiments[i].sentences[j].sentimentValue);
		    		}

		    		sentAverage /= secondAppSentiments[i].sentences.length;
		    		sentAverage = round(sentAverage);

		    		//if sentiment is null assume it as normal
		    		if (sentAverage !== sentAverage) {
		    			sentAverage = 2;	
		    		}
		    		if (!(sentAverage > 0)) {
		    			console.log(sentAverage);
		    		}

		    		returnSentiments[features[identifier]].secondAppSentiments.push( { 
		    			'sentence': sentence,
	    				'sentiment': sentAverage
		    		});

	    			returnSentiments[features[identifier]].secondAppSentimentAverage += sentAverage;	
		    			
		    		if (i === secondAppSentiments.length - 1) {
			    		returnSentiments[features[identifier]].secondAppSentimentAverage /= secondAppSentiments.length;
			    		returnSentiments[features[identifier]].secondAppSentimentAverage = round(returnSentiments[features[identifier]].secondAppSentimentAverage);
			    	}
	    		}


				executedPromiseCount += 1;
	    		if (executedPromiseCount / 2 === features.length && executedPromiseCount % 2 === 0) {
	    			console.log('finished sentiment analysis');
	    			executedPromiseCount = 0;

	    			res.set('Content-Type', 'application/json');
					res.send(returnSentiments);
	    		}
	    });
	}
}

function handleOneAppSentiments(res, features, url) {
	var returnSentiments = { };
    var executedPromiseCount = 0;

    for (var i = 0; i < features.length; i++) {
        returnSentiments[features[i]] = combinedFeatures.data[features[i]];
        returnSentiments[features[i]].comparison = false;
        returnSentiments[features[i]].firstAppName = combinedFeatures.firstAppName;
		returnSentiments[features[i]].firstAppSentimentAverage = 0;

        var firstAppSentimentPromises = [];
        var firstAppSentences = [];

        for (var sentenceKey in combinedFeatures.firstSentences) {
            var sentences = combinedFeatures.firstSentences[sentenceKey];
            for (var j in sentences) {
            	for (var k in combinedFeatures.data[features[i]].firstFeatures) {
	            	for (var extractedFeatureIndex in sentences[j].extracted_features) {
	            		if (combinedFeatures.data[features[i]].firstFeatures[k].feature === sentences[j].extracted_features[extractedFeatureIndex] &&
	            			firstAppSentences.indexOf(sentences[j].sentence_text) == -1) {
	            			firstAppSentimentPromises.push(httpPromisePostAsync(url, sentences[j].sentence_text, i));
	                		firstAppSentences.push(sentences[j].sentence_text);
	            		}
	            	}
            	}
            }
        }

        console.log("found sentences: " + firstAppSentimentPromises.length);

        returnSentiments[features[i]].firstAppSentiments = [];

        Promise.all(firstAppSentimentPromises).then(firstAppSentiments => {
	    	if (firstAppSentiments.length > 0) {
	    		console.log('first app sentiments for: \'' + features[firstAppSentiments[0].identifier] + '\' retrieved' );	
	    	}

	    	for (var i = 0; i < firstAppSentiments.length; i++) {
	    		var identifier = firstAppSentiments[i].identifier;
				var sentence = firstAppSentiments[i].sentence;
	    		var sentAverage = 0;

	    		if (returnSentiments[features[identifier]].firstAppSentimentAverage === undefined) {
	    			returnSentiments[features[identifier]].firstAppSentimentAverage = 0;
	    		}

	    		for (var j = 0; j < firstAppSentiments[i].sentences.length - 1; j++) {
	    			sentAverage += parseInt(firstAppSentiments[i].sentences[j].sentimentValue);
	    		}

	    		sentAverage /= (firstAppSentiments[i].sentences.length - 1);
	    		sentAverage = round(sentAverage);
				//if sentiment is NaN assume it as normal
	    		if (sentAverage !== sentAverage) {
	    			sentAverage = 2;	
	    		}

	    		returnSentiments[features[identifier]].firstAppSentiments.push( { 
	    			'sentence': sentence,
	    			'sentiment': sentAverage
	    		});

    			returnSentiments[features[identifier]].firstAppSentimentAverage += sentAverage;
    			
    			if (i === firstAppSentiments.length - 1) { 
					returnSentiments[features[identifier]].firstAppSentimentAverage /= firstAppSentiments.length;
					returnSentiments[features[identifier]].firstAppSentimentAverage = round(returnSentiments[features[identifier]].firstAppSentimentAverage);
				}
	    	}

	    	

    		executedPromiseCount += 1;
    		if (executedPromiseCount === features.length) {
    			executedPromiseCount = 0;
    			
    			res.set('Content-Type', 'application/json');
				res.send(returnSentiments);
    		}
	    });
	}
}


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
		        	console.log(response);
		        	console.log(error);
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
	        	console.log(response);
	        	console.log(error);
	        	reject(Error(error));
	        }
	    }
	);
}

function sendFailure(res, reason) {
	res.set('Content-Type', 'application/json');
	message.success = false;
	message.reason = reason;
	res.send(message);
}

function mineData(appValues, req, callback) {
	console.log("mineData() begining: " + appValues.length);
	if (appValues.length == 0) {
		console.log("**** returned ****");
		callback(allAppFeatures);
		return;
	}

	var app = appValues[0];

	var promises = [];
	
	for (var i = 0; i < 10; i++) {
	var promise = store.reviews({
		id: app.id,
		sort: store.sort.HELPFUL,
		page: i
		});

		promises.push(promise);
	}

	Promise.all(promises).then(values => { 
		values = [].concat.apply([], values)
		console.log("number of reviews: " + values.length)

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



