# app-recommendator-api

## instructions

Navigate to the project direcctory with terminal and execute the commands
1. npm install
2. npm install https://github.com/bbbuka/app-store-scraper.git
3. npm start

Then the server will start...

### Methods
#### Retrieve categories
http://localhost:8081/categories
```
{
  "BOOKS": 6018,
  "BUSINESS": 6000,
  "CATALOGS": 6022,
  "EDUCATION": 6017,
  ....
}
```

#### Retrieve apps within category
http://localhost:8081/apps?category=7003
```
[
  {
    "id": "1291851950",
    "appId": "io.voodoo.dune",
    "title": "Dune!",
    "icon": "http://is1.mzstatic.com/image/thumb/Purple118/v4/36/e8/47/36e847e2-a778-d51a-5f14-89f5394590c4/AppIcon-1x_U007emarketing-85-220-7.png/100x100bb-85.png",
    "url": "https://itunes.apple.com/us/app/dune/id1291851950?mt=8&uo=2",
    "price": 0,
    "currency": "USD",
    "free": true,
    "description": "Jump above the line to score, but beware! The higher you get, the harder the landing will be! Don't crash and keep it smooth!",
    "developer": "Voodoo",
    "developerUrl": "https://itunes.apple.com/us/developer/voodoo/id714804730?mt=8&uo=2",
    "developerId": "714804730",
    "genre": "Games",
    "genreId": "6014",
    "released": "2017-10-11T05:56:12-07:00",
    "version": "1.4"
  },
  {
  ...
  }
}
```

#### Retrieve app reviews within the given app
http://localhost:8081/app?appId=com.neonfun.catalog

```
{
  "appId": "com.neonfun.catalog",
  "reveiw_list": [
    {
      "id": "1855969729",
      "date": "2017-10-17T22:22:37.000Z",
      "userName": "DaBoom22",
      "userUrl": "https://itunes.apple.com/us/reviews/id180860804",
      "version": "7.01",
      "score": 5,
      "title": "Still concerned...",
      "text": "Review text",
      "url": "https://itunes.apple.com/us/review?id=656971078&type=Purple%20Software"
    },    
```


#### Retrieve app description within the given app
http://localhost:8081/app/description?id=1291851950
```
{
  "id": "1291851950",
  "description": "Jump above the line to score, but beware! The higher you get, the harder the landing will be! Don't crash and keep it smooth!"
}
```