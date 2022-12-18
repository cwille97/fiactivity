"""
This script is super hacky and awful but it works until I have time to learn GraphQL basics and learn how to understand the undocumented API.
The intention of this script is to fetch dog walks from the prior day and export to prometheus.
"""
import datetime
import json
import logging
import os
import requests
import sqlite3
import sys

FI_ACTIVITIES_GRAPHQL_QUERY = "query FiFeed($limit: Int, $pagingInstruction: PagingInstruction, $height: Int!, $width: Int!, $scale: Int) {\n  currentUser {\n    __typename\n    fiFeed(limit: $limit, pagingInstruction: $pagingInstruction) {\n      __typename\n      ...FiFeedDetails\n    }\n  }\n}\nfragment FiFeedDetails on FiFeed {\n  __typename\n  feedItems {\n    __typename\n    ...FiFeedItemDetails\n  }\n  pageInfo {\n    __typename\n    ...PageInfoDetails\n  }\n}\nfragment FiFeedItemDetails on FiFeedItem {\n  __typename\n  id\n  timestamp\n  ... on FiFeedActivityItem {\n    __typename\n    activity {\n      __typename\n      ...ActivityDetails\n      ... on Rest {\n        __typename\n        mapUrl(width: $width, height: $height, scale: $scale)\n      }\n      ... on Walk {\n        __typename\n        mapUrl(width: $width, height: $height, scale: $scale)\n      }\n      ... on Play {\n        __typename\n        mapUrl(width: $width, height: $height, scale: $scale)\n      }\n    }\n    pet {\n      __typename\n      ...BasePetInfo\n    }\n  }\n  ... on FiFeedGenericNotificationItem {\n    __typename\n    title\n    body {\n      __typename\n      ...FormatStringDetails\n    }\n    hideTimestamp\n  }\n  ... on FiFeedGoalStreakItem {\n    __typename\n    numDays\n    pet {\n      __typename\n      ...BasePetInfo\n    }\n  }\n  ... on FiFeedRankingUpdateItem {\n    __typename\n    pet {\n      __typename\n      ...BasePetInfo\n      breed {\n        __typename\n        ...BreedDetails\n      }\n    }\n    newBreedRank\n    newOverallRank\n    newOverallRankPercentile\n  }\n  ... on FiFeedPhotoAddedItem {\n    __typename\n    pet {\n      __typename\n      ...BasePetInfo\n    }\n    photo {\n      __typename\n      ...PhotoDetails\n    }\n    user {\n      __typename\n      firstName\n    }\n  }\n  ... on FiFeedLikableWalkItem {\n    __typename\n    followedPet {\n      __typename\n      ...BasePetInfo\n    }\n    walk {\n      __typename\n      ...StrangerWalkDetails\n    }\n  }\n}\nfragment ActivityDetails on Activity {\n  __typename\n  id\n  start\n  end\n  areaName\n  presentUser {\n    __typename\n    ...UserDetails\n  }\n  presentUserString\n  totalSteps\n  obfuscated\n  ... on Walk {\n    __typename\n    isLikable\n    likeCount\n    distance\n    mapPath {\n      __typename\n      ... on MapMatchedPath {\n        __typename\n        path {\n          __typename\n          ...PositionCoordinates\n        }\n      }\n      ... on UnmatchedPath {\n        __typename\n        locations {\n          __typename\n          ...LocationPoint\n        }\n      }\n    }\n  }\n  ... on Rest {\n    __typename\n    position {\n      __typename\n      ...PositionCoordinates\n    }\n    place {\n      __typename\n      ...PlaceDetails\n    }\n  }\n  ... on Play {\n    __typename\n    position {\n      __typename\n      ...PositionCoordinates\n    }\n    place {\n      __typename\n      ...PlaceDetails\n    }\n  }\n}\nfragment UserDetails on User {\n  __typename\n  id\n  email\n  firstName\n  lastName\n  phoneNumber\n  fiNewsNotificationsEnabled\n}\nfragment PositionCoordinates on Position {\n  __typename\n  latitude\n  longitude\n}\nfragment LocationPoint on Location {\n  __typename\n  date\n  errorRadius\n  position {\n    __typename\n    ...PositionCoordinates\n  }\n}\nfragment PlaceDetails on Place {\n  __typename\n  id\n  name\n  address\n  position {\n    __typename\n    ...PositionCoordinates\n  }\n  radius\n  type\n  coordinates {\n    __typename\n    ...PositionCoordinates\n  }\n}\nfragment BasePetInfo on BasePet {\n  __typename\n  id\n  name\n  homeCityState\n  photos {\n    __typename\n    first {\n      __typename\n      image {\n        __typename\n        ...ImageDetails\n      }\n    }\n  }\n  ... on StrangerPet {\n    __typename\n    followStatus\n  }\n  ... on Pet {\n    __typename\n    household {\n      __typename\n      id\n    }\n  }\n}\nfragment ImageDetails on Image {\n  __typename\n  id\n  fullSize\n}\nfragment FormatStringDetails on FormatString {\n  __typename\n  text\n  spans {\n    __typename\n    start\n    length\n    style\n  }\n}\nfragment BreedDetails on Breed {\n  __typename\n  id\n  name\n  popularityScore\n}\nfragment PhotoDetails on Photo {\n  __typename\n  id\n  date\n  image {\n    __typename\n    ...ImageDetails\n  }\n  likeCount\n  liked\n  caption\n  comments {\n    __typename\n    items {\n      __typename\n      ...CommentDetails\n    }\n    totalCount\n  }\n  pet {\n    __typename\n    ...BasePetInfo\n  }\n  poster {\n    __typename\n    ...PhotoPosterDetails\n  }\n}\nfragment CommentDetails on Comment {\n  __typename\n  id\n  comment\n  createdAt\n  strangerPet {\n    __typename\n    id\n    name\n    photos {\n      __typename\n      first {\n        __typename\n        image {\n          __typename\n          fullSize\n        }\n      }\n    }\n  }\n}\nfragment PhotoPosterDetails on PhotoPoster {\n  __typename\n  ... on StrangerUser {\n    __typename\n    ...StrangerUserDetails\n  }\n  ... on ExternalUser {\n    __typename\n    ...ExternalUserDetails\n  }\n}\nfragment StrangerUserDetails on StrangerUser {\n  __typename\n  id\n  firstName\n  profilePicture {\n    __typename\n    ...ImageDetails\n  }\n}\nfragment ExternalUserDetails on ExternalUser {\n  __typename\n  id\n  name\n  profilePicture {\n    __typename\n    ...ImageDetails\n  }\n}\nfragment StrangerWalkDetails on StrangerWalk {\n  __typename\n  id\n  distance\n  stepCount\n  liked\n  likeCount\n}\nfragment PageInfoDetails on PageInfo {\n  __typename\n  startCursor\n  endCursor\n  hasNextPage\n  hasPreviousPage\n}"

ACTIVITIES_TABLE = """
    CREATE TABLE Activities(
        activity_id TEXT PRIMARY KEY,
        activity_type TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        area_name TEXT,
        user_name TEXT,
        user_id TEXT,
        present_user_string TEXT,
        total_steps INTEGER,
        obfuscated BOOLEAN NOT NULL,
        distance REAL,
        pet_name TEXT NOT NULL,
        map_url TEXT,
        map_type TEXT NOT NULL
    );
"""

LOCATIONS_TABLE = """
    CREATE TABLE Locations(
        activity_id VARCHAR NOT NULL,
        timestamp TEXT,
        error_radius REAL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        FOREIGN KEY (activity_id)
            REFERENCES Activites (activity_id)
    );
"""

def export_walks_json(response: dict, time_range: int):
    """Parse response for relevant walk data. time_range is an int representing num days. The response param is expected to be in the format as provided by FI_ACTIVITIES_GRAPHQL_QUERY"""
    walks = []
    for item in response['data']['currentUser']['fiFeed']['feedItems']:
        if item['__typename'] == 'FiFeedActivityItem' and item['activity']['__typename'] == 'Walk' \
            and (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(item['timestamp'][0:-1])) > datetime.timedelta(time_range):
            walk = { # 2022-12-12T01:11:08.249Z
                'id': item['activity']['id'],
                'start': item['activity']['start'],
                'end': item['activity']['end'],
                'areaName': item['activity']['areaName'],
                'presentUser': item['activity']['presentUser'],
                'presentUserString': item['activity']['presentUserString'],
                'totalSteps': item['activity']['totalSteps'],
                'obfuscated': item['activity']['obfuscated'],
                'distance': item['activity']['distance'],
                'mapPath': item['activity']['mapPath'],
                'mapUrl': item['activity']['mapUrl'],
                'petName': item['pet']['name']
            }
            walks.append(walk)
    return walks

def dump_data_to_sqlite(data: dict):
    """Parse data for relevant walks and save to SQLite"""
    con = sqlite3.connect('fiactivity.db')
    cur = con.cursor()
    for item in data['data']['currentUser']['fiFeed']['feedItems']:
        if item['__typename'] == 'FiFeedActivityItem' and item['activity']['__typename'] == 'Walk':
            if activity_exists(item['activity']['id'], cur): # skip this activity if we already have the ID in the DB
                continue
            start_time = item['activity']['start'][0:-1].replace('T', ' '), # format to ISO8601 YYYY-MM-DD HH:MM:SS.SSS
            end_time = item['activity']['end'][0:-1].replace('T', ' ')
            present_user = item['activity'].get('presentUser')
            user_name = None
            user_id = None
            if present_user:
                first_name = present_user.get('firstName')
                last_name = present_user.get('lastName')
                user_name = f'{first_name} {last_name}'
                user_id = present_user.get('id')
            try:
                query_str = f'INSERT INTO Activities VALUES (\"{item["activity"]["id"]}\", \"{item["activity"]["__typename"]}\", \"{start_time}\",' \
                            f'\"{end_time}\", \"{item["activity"].get("areaName")}\", \"{user_name}\", \"{user_id}\", \"{item["activity"]["presentUserString"]}\"' \
                            f', {item["activity"]["totalSteps"]}, {item["activity"]["obfuscated"]}, {item["activity"]["distance"]}, \"{item["pet"]["name"]}\",' \
                            f'\"{item["activity"]["mapUrl"]}\", \"{item["activity"]["mapPath"]["__typename"]}\");'
            except TypeError as e:
                logging.error(f'Encountered a TypeError while attempting to format a SQL query to create a new Activity: {e}. Item was {json.dumps(item)}')
                sys.exit(1)
            try:
                cur.execute(query_str)
            except sqlite3.ProgrammingError as e:
                logging.error(f'Encountered an exception while trying to INSERT a new Activity. Query was {query_str}, exception was {e}')
                sys.exit(1)
            if item['activity']['mapPath']['__typename'] == 'MapMatchedPath':
                for location in item['activity']['mapPath']['path']:

                    try:
                        query_str = f'INSERT INTO Locations (activity_id, latitude, longitude) VALUES (\"{item["activity"]["id"]}\", \"{location["latitude"]}\", \"{location["longitude"]}\");'
                        logging.info(f'INSERTED a new Activity with ID {item["activity"]["id"]}')
                    except TypeError as e:
                        logging.error(f'Encountered a TypeError while attempting to format a SQL query for an MapMatchedPath. Query was {query_str}, exception was {e}')
                        sys.exit(1)
                    try:
                        cur.execute(query_str)
                        logging.info(f'INSERTED a new Activity with ID {item["activity"]["id"]}')
                    except sqlite3.ProgrammingError as e:
                        logging.error(f'Encountered an exception while trying to INSERT a new Location. Query was {query_str}, exception was {e}')
                        sys.exit(1)
            elif item['activity']['mapPath']['__typename'] == 'UnmatchedPath':
                for location in item['activity']['mapPath']['locations']:
                    try:
                        timestamp = location['date'][0:-1].replace('T', ' ')
                        query_str = f'INSERT INTO Locations (activity_id, timestamp, error_radius, latitude, longitude) VALUES (\"{item["activity"]["id"]}\", \"{timestamp}\", \"{location["errorRadius"]}\", \"{location["position"]["latitude"]}\", \"{location["position"]["longitude"]}\");'
                    except TypeError as e:
                        logging.error(f'Encountered a TypeError while attempting to format a SQL query for an UnmatchedPath. Query was {query_str}, exception was {e}')
                        sys.exit(1)
                    except KeyError as e:
                        logging.error(f'Encountered a KeyError while attempting to format a SQL query for an UnmatchedPath. Query was {query_str}, exception was {e}. Item was {item}, location was {location}')
                        sys.exit(1)
                    try:
                        cur.execute(query_str)
                        logging.info(f'INSERTED a new Location belonging to the Activity with ID {item["activity"]["id"]}')
                    except sqlite3.ProgrammingError as e:
                        logging.error(f'Encountered an exception while trying to INSERT a new Location. Query was {query_str}, exception was {e}')
                        sys.exit(1)
            else:
                logging.error(f'Encountered a mapPath that was not of a known type. Full data: {json.dumps(item)}')
                sys.exit(1)
    con.commit()

def activity_exists(activity_id: str, cur: sqlite3.Cursor) -> bool:
    cur.execute(f'SELECT EXISTS(SELECT 1 FROM Activities WHERE activity_id = \"{activity_id}\")')
    return cur.fetchone()

def fetch_activities():
    email = os.environ.get('FI_EMAIL')
    password = os.environ.get('FI_PASSWORD')
    request_template = {
        "operationName": "FiFeed",
        "query": FI_ACTIVITIES_GRAPHQL_QUERY,
        "variables": {
            "height": 300,
            "limit": 100, # this is just a lazy arbitrary limit since nobody is going to walk the dog 100 times in each day
            "pagingInstruction": {
                "cursor": "null",
                "direction":"BACKWARD"
            },
            "scale":4,
            "width":373
        }
    }

    session = requests.Session()
    data = {
        'email': email,
        'password': password
    }
    if email is None or password is None:
        logging.error('Email or password were empty')
        sys.exit(1)
    response = session.post('https://api.tryfi.com/auth/login', data=data)
    try:
        if response.status_code != 200:
            logging.error(f'Encountered non-200 status code while fetching session. Response looked like: {str(response.content)}, request body looked like {data}')
            sys.exit(1)
    except AttributeError as e:
        logging.error('Encountered an attribute error while attempting to decode session response that looked like: ' + str(response.content))
        sys.exit(1)

    try:
        json_content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logging.error('Encountered the following exception while attempting to decode the session response: ' + e)
        sys.exit(1)
    except UnicodeDecodeError as e:
        logging.error('Encountered the following exception while attempting to decode the session response: ' + e)
        sys.exit(1)

    try:
        session_id = json_content['sessionId']
    except KeyError as e:
        logging.error('Encountered the following error while attempting to parse the session ID: ' + e)
        sys.exit(1)

    session.headers = {
        'content-type': 'application/json',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'x-apollo-operation-name': 'FiFeed',
        'apollographql-client-version': '3.0.5-0',
        'x-session-id': session_id
    }


    try:
        data = json.dumps(request_template)
    except TypeError as e:
        logging.error('Encountered the following error while attempting to parse data resopnse: ' + e)
    data_response = session.post('https://api.tryfi.com/graphql', data)
    try:
        if data_response.status_code != 200:
            logging.error('Encountered non-200 status code while fetching data. Response looked like: ' + str(data_response.content))
            sys.exit(1)
    except AttributeError:
        logging.error('Encountered an attribute error while attempting to decode data response that looked like: ' + str(data_response.content))
        sys.exit(1)

    try:
        json_content = data_response.json()
    except requests.exceptions.JSONDecodeError as e:
        logging.error('Encountered an exception while attempting to decode data response to json. Exception looked like %s, data was %s' % e, str(data_response))
        sys.exit(1)
    except UnicodeDecodeError as e:
        logging.error('Encountered an exception while attempting to decode data response to json. Exception looked like %s, data was %s' % e, str(data_response))
        sys.exit(1)
    logging.info(f'Dumping raw data resonse from the API: {json.dumps(json_content)}')
    return json_content

def main():
    json_content = fetch_activities()
    dump_data_to_sqlite(json_content)

if __name__ == '__main__':
    main()

