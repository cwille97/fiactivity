# fiactivity
Quick and dirty script to fetch data from Fi and send to Prometheus. A much more elegant solution would be to add an API endpoint to [pytryfi](https://github.com/sbabcock23/pytryfi) and use that. Ideally this solution should properly use their pagination. However, until I have time to learn the basics of GraphQL this script will suffice.

## Disclaimer
**USE AT YOUR OWN RISK** there's always potential that this gets your account suspended since it might not be permitted by the EULA. That being said, it's my opinion that we should be able to have access to our own data and so long as you don't change variables this shouldn't hammer the API. Fetching 100 entries would be equivalent to scrolling the activity timeline for a few minutes. I am not responsible for anything that happens to your access to Fi as a result of using this script.
