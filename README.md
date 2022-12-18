# fiactivity
Quick and dirty script to fetch data from Fi and send to Prometheus. A much more elegant solution would be to add an API endpoint to [pytryfi](https://github.com/sbabcock23/pytryfi) and use that. Ideally this solution should properly use their pagination. However, until I have time to learn the basics of GraphQL this script will suffice.

## Disclaimer
**USE AT YOUR OWN RISK** there's always potential that this gets your account suspended since it might not be permitted by the EULA. That being said, it's my opinion that we should be able to have access to our own data and so long as you don't change variables this shouldn't hammer the API. Fetching 100 entries would be equivalent to scrolling the activity timeline for a few minutes. I am not responsible for anything that happens to your access to Fi as a result of using this script. Also since their API is subject to change at any time, this could break unexpectedly.

## DB Schema
Before running this app for the first time, you'll need to create a SQLite DB with a file name of fiactivity.db and populate it with the tables in the schema. Probably the easiest way to do this is to use a Python shell and import `sqlite3` and open the non-existent DB file (it will be created automatically) and run the `CREATE TABLE` commands at the top of the Python file. Don't forget to commit your SQL queries and then the DB should be ready.
![fischema drawio](https://user-images.githubusercontent.com/24487628/208002347-e3216dc7-fbf2-483c-a5d8-1ca9e6982e1c.svg)

## Data Structure
The Activities data has an interesting structure. I was only interested in Walks and not resting periods so I filtered on that. It seems like there's two types of walks: `MapMatchedPath` and `UnmatchedPath`. I'm pretty sure the latter is when the collar is on a walk without an accompanying smartphone and is relying on its own GPS and cellular chip to ping data. When an owner's smartphone is present, the collar instead talks to the app and the app will use the smartphone's GPS and data to get more precise and frequent location information. The two types have slightly different data because `UnmatchedPath` needs to include information about margins of error.

### MapMatchedPath
This data format looks like the following JSON
```
{
mapPath:
  __typename: "MapMatchedPath"
  path: [
    {
      __typename: "position",
      latitude: 25.000,
      longitude: 25.000
    }
    .
    .
    .
  ]
```

### UnmatchedPath
```
{
mapPath:
  __typename: "UnmatchedPath"
  path: [
    {
      __typename: "Location"
      date: "2022-12-12T01:01:55.737Z",
      errorRadius: 18.99999,
      position: {
        __typename: "Position",
        latitude: 25.000,
        longitude: 25.000
      }
    }
    .
    .
    .
   ]
```
### Data Sample
This is a sample of the JSON structure as a result of my parsing after receiving the data from the GraphQL API
<img width="471" alt="Screenshot 2022-12-15 at 8 56 43 PM" src="https://user-images.githubusercontent.com/24487628/208004323-627fd6c8-4ab3-4a0e-9d2f-552ed21d2090.png">
