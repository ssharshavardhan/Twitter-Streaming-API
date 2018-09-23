# Twitter Stream Filter API

This set of APIs has been created to store twitter streaming data and retrieve data based on applied filters. It is a set of 3 APIs-
1. [API to trigger Twitter Stream](#1-api-to-trigger-twitter-stream)
2. [API to filter/search stored tweets](#2-api-to-filtersearch-stored-tweets-search)
3. [API to export filtered data in CSV](#3-api-to-export-filtered-data-in-csv-getcsv)

Technologies used:
  - Python/ Flask framework
  - MongoDB (Hosted on MLab)
  - Twitter Streaming API
  
## Jump To
- [Installation Instructions](#installation-instructions)
- [API 1 - API to trigger Twitter Stream](#1-api-to-trigger-twitter-stream)
- [API 2 - API to filter/search stored tweets](#2-api-to-filtersearch-stored-tweets-search)
- [API 3 - API to export filtered data in CSV](#3-api-to-export-filtered-data-in-csv-getcsv)
  
## Installation Instructions
  1. clone the project
  `git clone https://github.com/ssharshavardhan/twitter-streaming-api.git`
  2. cd to project folder `cd twitter-streaming-api` and create virtual environment
  `virtualenv venv`
  3. activate virtual environment
  `source venv/bin/activate`
  4. install requirements
  `pip install -r requirements.txt`
  5. run the server
  `python twitterapi.py`
   
## 1. API to trigger Twitter Stream (/stream)
This API triggers twitter streaming and stores a curated version of the data returned by Twitter Streaming API. The streaming is done as per the given parameters.

API - `http://127.0.0.1:5000/stream/<keyword>?[parameters]`
(methods supported - GET, POST)

Where `<keyword>` can be any keyword for which streaming needs to be performed and `[parameters]` are as follows -
  
  | Parameter | Action |
  | ------ | ------ |
  | count | the streaming runs till given number of tweets are received |
  | time | the streaming runs for given time (seconds) |
  
  <b>Examples:</b>
  ```
  http://127.0.0.1:5000/stream/India?count=100 (runs till 100 tweets are fetched)
  http://127.0.0.1:5000/stream/India?time=60 (runs for 60 seconds)
  http://127.0.0.1:5000/stream/India?count=100&time=60 (stops streaming whichever comes first i.e. 10 tweets or 10 seconds)
  ```
  ### API Response
  | Parameter | Meaning |
  | ------ | ------ |
  | code | 0 (successful)/ 1(failed) |
  | message | error message if api hit fails |
  | status | success/failed |
  
  <b>Examples:</b>
  
  1. Successful response
  ```
  {
    "code": "0",
    "message": "Successful",
    "status": "success"
  }
  ```
  2. Failed Response
  ```
  {
    "code": "1",
    "message": "No Parameters Passed",
    "status": "failed"
  }
  ```

## 2. API to filter/search stored tweets (/search)
This API fetches the data stored by the [first api](#1-api-to-trigger-twitter-stream) based on the filters and search keywords provided and sorts them as required.

API - `http://127.0.0.1:5000/search/[filters][sort][page]`
(methods supported - GET, POST)

<b>Following are the elements of the api:</b>
### Filters ([filters])
The filters follow format `<filter>=<value>` where `<filter>` can be one or more of filters mentioned below and `<value>` should be in the specified format. 
  
  
Following filters can be applied

  | Filter | Meaning | Value Format (refer table below) | Example |
  | ------ | ----- | ------ | ----- |
  | hashtag | filter tweets by hashtags in tweet (case insensitive) | `<hashtag>` | hashtag=India |
  | keyword | filter tweets by keyword which was used in API 1 for streaming | `<keyword>` | keyword=India |
  | name | filter tweets by name/ screen_name of users (case insensitive) | `<textFilterType>-<filterValue>` | name=co-harsha |
  | location | location of the user posting the tweet | `<location>` | location=India |
  | text | filter tweets by content (case insensitive) | `<textFilterType>-<filterValue>` | text=sw-harsha |
  | type | filter tweets as retweets/quote/original tweets | original/retweet/quote | type=retweet |
  | mention | filter tweets by user mentions(case insensitive) | `<textFilterType>-<filterValue>` | mention=em-harsha |
  | follow_count | number of followers of the user | `<numericFilterType><filterValue>`| follow_count=lt100 |
  | rt_count (mostly 0 in streaming) | retweet count of tweet | `<numericFilterType><filterValue>`| rt_count=gt100 |
  | fav_count (mostly 0 in streaming) | favourite count of tweet | `<numericFilterType><filterValue>`| fav_count=lt100 |
  | language | Language of tweet | language=en |
  | start_date | Tweets posted on or after a specific date | `dd-mm-yyyy` | start_date=11-02-2018 |
  | end_date | Tweets posted on or before a specific date | `dd-mm-yyyy` | end_date=15-02-2018 |
  
  In the format `<textFilterType><filterValue>`, `<filterValue>` can be any string and `<textFilterType>` can be

  | textFilterType | Meaning |
  | ------ | ------ |
  | sw | starts with |
  | ew | ends with |
  | co | contains |
  | em | exact match |
  
  In the format `<numericFilterType><filterValue>`, `<filterValue>` can be any number and `<numericFilterType>` can be

  | numericFilterType | Meaning |
  | ------ | ------ |
  | gt | greater than |
  | lt | less than |
  | eq | equal to |
  | ge | greater than or equal to |
  | le | less than or equal to |
  
### Sort ([sort])
By default, sorting is done by date of tweet in descending order. Other sort types can be given by mentionin the `sort` parameter in the API in the format `<sortField>-<order>`

where  `<order>` can be

  | order | Meaning |
  | ------ | ----- |
  | asc | Ascending order |
  | dsc | descending order |
  
and `<sortField>` can be

  | sortField | Meaning | Example |
  | ------ | ------ | ------ |
  | name | sort by name | sort=name-asc |
  | sname | sort by screen name | sort=sname-dsc |
  | text | sort by tweet text | sort=text-asc |
  | fav | sort by favourites count | sort=fav-asc |
  | ret | sort by retweet count | sort=ret-dsc |
  | followers | sort by follower count of user | sort=followers-asc |
  | date | sort by date | sort=date-asc |
  
### Page ([page])
The API is paginated and returns 10 results in one call. The page number can be specified in the API call as `page=[pageNo]` for example `page=5`. Not speciftying the page number takes to page 1.

<b>Examples</b>
```
http://127.0.0.1:5000/search/?fav_count=gt1000&language=en&start_date=11-02-2018&sort=date-asc
http://127.0.0.1:5000/search/?name=co-India&start_date=11-02-2018&end_date=15-02-2018&sort=text-asc&page=2
http://127.0.0.1:5000/search/?rt_count=gt1000
```

### API Response

  | Parameter | Meaning |
  | ------ | ------ |
  | page | current page number |
  | next_page | next page number (1 if current page is last page) |
  | last_page | Boolean true/false (true if current page is last page else false) |
  | result | list of tweet objects that match the given filters |
  | result_count | total number of matching results |
  

## 3. API to export filtered data in CSV (/getcsv)
This API returns the data in CSV. If opened in browser, it downloads a CSV file containin the data and if hit using another program, it returns the data in CSV format.

API : `http://127.0.0.1:5000/getcsv/[filters][sort]`
(methods supported - GET, POST)

`[filters]` and `[sort]` are the same parameters as defined in the [Second API](#2-api-to-filtersearch-stored-tweets-search) and there is no `[page]` parameter as all the matching data is returned.

<b>Examples</b>
```
http://127.0.0.1:5000/getcsv/?hashtag=India
http://127.0.0.1:5000/getcsv/?fav_count=gt1000&language=en&start_date=11-02-2018&sort=date-asc
```

### API Response
If the request to the API is sent using a browser, it downloads a CSV file containing data based on filters.
If the request is sent by another program/ application like Postman etc., the API returns the data in CSV format.
