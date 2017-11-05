var express = require('express');
var app = express();
var store = require('app-store-scraper');
var PythonShell = require('python-shell');

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
		for (i = 0; i < result.length; i++) {
			var promise = store.app({id: parseInt(result[i].id)})
			promises.push(promise);
		}

		Promise.all(promises).then(values => { 
			for (i = 0; i< values.length; i++) {
				result[i].version = values[i].version;
			}	
			res.send(result)
		});
	});
});

app.get('/app', function(req, res){
	var promises = [];

	for (i = 0; i< 10; i++) {
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
			reveiw_list: values
		};
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

app.get('/features', function(req, res){ 

	if (req.query.mode == modeEnum.AppDescription) {
		store.app({id: parseInt(req.query.id)}).then(values => {  
					
			var dataToExtract = [{
				appID : req.query.id,
				data: values.description,
				mode: modeEnum.AppDescription
			}];

			var options = {
			    mode: 'json',
			    pythonPath: '/usr/local/bin/python3'
			};

			var pyshell = new PythonShell('feature-extraction/SAFE.py', options);
			pyshell.send(dataToExtract);

			pyshell.on('message', function (message) {
			    res.set('Content-Type', 'application/json');
	  		    res.send({ 
					id: req.query.id,
					features: message
				});
			});

			pyshell.end(function (err) {
			    if (err){ throw err; };
			    console.log('finished');
			});
		});
	} else if (req.query.mode == modeEnum.AppReviews) {
		var promises = [];
		
			for (i = 0; i< 10; i++) {
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

				var dataToExtract = [{
					appID : req.query.id,
					data: values,
					mode: modeEnum.AppReviews
				}];
	
				var options = {
					mode: 'json',
					pythonPath: '/usr/local/bin/python3'
				};

				var pyshell = new PythonShell('feature-extraction/SAFE.py', options);
				pyshell.send(dataToExtract);
	
				pyshell.on('message', function (message) {
					res.set('Content-Type', 'application/json');
					  res.send({ 
						id: req.query.id,
						features: message
					});
				});
	
				pyshell.end(function (err) {
					if (err){ throw err; };
					console.log('finished');
				});
				
			});
	}
});

console.log('Server running at localhost:8081/');


