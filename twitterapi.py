from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
import pymongo
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from bson import ObjectId
import json
from creds import *
import csv
from datetime import datetime


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'innodb'
app.config['MONGO_URI'] = 'mongodb://ssharshavardhan:1234@ds143738.mlab.com:43738/innodb'
mongo = PyMongo(app)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
        	return str(o)
        return json.JSONEncoder.default(self, o)

def storeData(data, keyword):
	tweets = mongo.db.tweets
        users = mongo.db.users
	datatest = tweets.find_one({'id':data['id']})
	if datatest == None:
		user_keys = ['id','screen_name', 'name', 'location', 'followers_count']
		test = users.find_one({'id':data['user']['id']})
		if test == None:
			save_user = {key: data['user'][key] for key in user_keys}
			save_user["name_lower"] = data['user']['name'].lower()
			save_user["screen_name_lower"] = save_user["screen_name"].lower()
			if data['user']['location']:
				save_user["location_lower"] = data['user']['location'].lower()
			users.insert(save_user)


		data['user'] = data['user']['id']

		datakeys = ['favorite_count', 'id', 'is_quote_status', 'lang', 'retweet_count','user']
		data_save = {key: data[key] for key in datakeys}
		if data['truncated'] and 'full_text' in data:
			data_save['text'] = data['full_text']
		else:
			data_save['text'] = data['text']

		data_save['created_at'] = dt = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
		data_save['text_lower'] = data_save['text'].lower()
		data_save['hashtags'] = [x['text'] for x in data['entities']['hashtags']]
		data_save['hashtags_lower'] = [x['text'].lower() for x in data['entities']['hashtags']]
		data_save['user_mentions'] = [x['screen_name'] for x in data['entities']['user_mentions']]
		data_save['user_mentions_lower'] = [x['screen_name'].lower() for x in data['entities']['user_mentions']]
		data_save['keyword'] = keyword.lower()

		data_save['is_retweet'] = False
		if 'retweeted_status' in data:
			data_save['is_retweet'] = True

		tweets.insert(data_save)

class Listener(StreamListener):

	def __init__(self, time, count, keyword):
		self.highest_tweet = count
		self.time = time
		self.count_of_tweet = 0
		self.starttime = datetime.now()
		self.keyword = keyword

	def on_data(self, data):
		if self.time and (datetime.now()-self.starttime).seconds >= self.time:
			return False

		dtemp = json.loads(data)
		storeData(dtemp, self.keyword)

		self.count_of_tweet+=1
		if self.time and (datetime.now()-self.starttime).seconds >= self.time:
			return False

		if self.highest_tweet and self.count_of_tweet >= self.highest_tweet:
			return False

		return True

	def on_error(self, status):
		print status



@app.route("/stream/<keyword>", methods=['GET','POST'])
def stream(keyword):
	try:
		time = request.args.get('time')
		count = request.args.get('count')

		if time == None or time == "":
			time = 0
		if count == None or count == "":
			count = 0
		if time == 0 and count ==0:
			return jsonify({"code":"1","status":"failed","message":"No Parameters Passed"})

		l = Listener(int(time), int(count), keyword)
		auth = OAuthHandler('tjEkXauBYWewH4F912t77MrjX', 'YXmO9Gns5JU276OVJQgTjftj0eERNRW3lXFR1LMRHY03OAiCyZ')
		auth.set_access_token('796752910071828481-jD8GEXNQrwmK7P2MN6kOUaY8vxbSr0t', 'Fyu8M27vhJGiAltksdI07n8lZk7Y7kVocVpzGKec8hCku')
		stream = Stream(auth, l)

		stream.filter(track=[keyword])

		return jsonify({"code":"0","status":"success","message":"Successful"})
	except:
		return jsonify({"code":"1","status":"failed","message":"Some error occured"})




def filterData(name, text, rt_count, fav_count, start_date, end_date, language, mention, sortPar,
				 hashtag, follow_count, typeTw, location, keyword):
	tweets = mongo.db.tweets
    	users = mongo.db.users


	sort, sortType = "created_at", pymongo.DESCENDING
	sort_Two=None
	sortType2 = None
	if sortPar != None and '-' in sortPar:
		sorttemp, sortTypetemp = sortPar.strip().split("-")
		if sorttemp and sortTypetemp:

			if sorttemp == "sname":
				 sort_Two = "screen_name"
                        elif sorttemp == "name":
				 sort_Two = "user"

                        elif sorttemp == "text":
				 sort = "text"

                        elif sorttemp == "followers":
				 sort = "followers_count"

			elif sorttemp == "fav":
				 sort = "favorite_count"
			elif sorttemp == "ret":
				 sort = "retweet_count"
			else:
				 sort = "created_at"


			if sortTypetemp == "dsc":
				if sort_Two:
					sortType2="dsc"
				else:
					sortType = pymongo.DESCENDING
                        elif sortTypetemp == "asc":
    			        if sort_Two:
    				         sortType2="asc"
    			        else:
    				         sortType = pymongo.ASCENDING
		        else:
			        sort, sortType = "created_at", pymongo.DESCENDING






	filter_dictionary_user = {}
	filter_dictionary = {}

	if keyword != None:
		filter_dictionary["keyword"] = keyword.lower()

	if typeTw != None:
		if typeTw == "retweet":
			filter_dictionary["is_retweet"] = True
		elif typeTw == "quote":
			filter_dictionary["is_quote_status"] = True
		elif typeTw == "original":
			filter_dictionary["is_retweet"] = False
			filter_dictionary["is_quote_status"] = False

	if hashtag != None:
		filter_dictionary['hashtags_lower'] = hashtag.lower()

	if start_date != None and end_date == None and len(start_date)==10:
		try:
			date, month, year = map(int, start_date.strip().split("-"))
			datest = datetime(year,month, date)
			print datest
			filter_dictionary['created_at'] = {'$gte':datest}
		except:
			pass

	if end_date != None and start_date == None and len(end_date)==10:
		try:
			date, month, year = map(int, end_date.strip().split("-"))
			daten = datetime(year,month, date)
			filter_dictionary['created_at'] = {'$lte':daten}
		except:
			pass

	if start_date != None and end_date != None and len(start_date)==10 and len(end_date)==10:
		try:
			date, month, year = map(int, start_date.strip().split("-"))
			datest = datetime(year,month, date)

			date, month, year = map(int, end_date.strip().split("-"))
			daten = datetime(year,month, date)
			filter_dictionary['$and'] = [{'created_at':{'$gte':datest}}, {'created_at':{'$lte':daten}}]
		except:
			pass

	if location != None:
		filter_dictionary_user["location_lower"] = location.lower()

	if follow_count != None:
		follow_count_type = follow_count[:2].lower()
		follow_count = follow_count[2:]
		if follow_count.isdigit():
			if follow_count_type == "gt":
				filter_dictionary_user["followers_count"] = {'$gt':int(follow_count)}
			elif follow_count_type == "lt":
				filter_dictionary_user["followers_count"] = {'$lt':int(follow_count)}
			elif follow_count_type == "eq":
				filter_dictionary_user["followers_count"] = {'$eq':int(follow_count)}
			elif follow_count_type == "le":
				filter_dictionary_user["followers_count"] = {'$lte':int(follow_count)}
			elif follow_count_type == "ge":
				filter_dictionary_user["followers_count"] = {'$gte':int(follow_count)}

	if name != None:
		type_name = name[:2].lower()
		name = name[3:].lower()

		if type_name == "sw":
			filter_dictionary_user["$or"] = [
						{"name_lower" : {'$regex' : "^"+name.lower()}},
						{"screen_name_lower" : {'$regex' : "^"+name.lower()}}
					]

		elif type_name == "ew":
			filter_dictionary_user["$or"] = [
				{"name_lower" : {'$regex' : name.lower()+"$"}},
				{"screen_name_lower" : {'$regex' : name.lower()+"$"}}
			]

		elif type_name == "co":
			filter_dictionary_user["$or"] = [
				{"name_lower" : {'$regex' : name.lower()}},
				{"screen_name_lower" : {'$regex' : name.lower()}}
			]

		elif type_name == "em":
			filter_dictionary_user["$or"] = [
				{"name_lower" : name.lower()},
				{"screen_name_lower" : name.lower()}
			]

	if name != None or follow_count != None or location != None:
		nameids = []
		for i in users.find(filter_dictionary_user):
			nameids.append(i['id'])
		filter_dictionary['user'] = {'$in' : nameids}

	if mention != None:
		type_of_mention = mention[:2].lower()
		mention = mention[3:].lower()
		if type_of_mention == "sw":
			filter_dictionary["user_mentions_lower"] = {'$regex' : "^"+mention.lower()}
		elif type_of_mention == "ew":
			filter_dictionary["user_mentions_lower"] = {'$regex' : mention.lower()+"$"}
		elif type_of_mention == "co":
			filter_dictionary["user_mentions_lower"] = {'$regex' : mention.lower()}
		elif type_of_mention == "em":
			filter_dictionary["user_mentions_lower"] = mention.lower()

	if language != None:
		filter_dictionary["lang"] = language

	if text != None:
		text_type = text[:2].lower()
		text = text[3:].lower()
		if text_type == "sw":
			filter_dictionary["text_lower"] = {'$regex' : "^"+text.lower()}
		elif text_type == "ew":
			filter_dictionary["text_lower"] = {'$regex' : text.lower()+"$"}
		elif text_type == "co":
			filter_dictionary["text_lower"] = {'$regex' : text.lower()}
		elif text_type == "em":
			filter_dictionary["text_lower"] = text.lower()





        if rt_count != None:
		rt_count_type = rt_count[:2].lower()
		rt_count = rt_count[2:]
		print rt_count, rt_count_type
		if rt_count.isdigit():
			if rt_count_type == "gt":
				filter_dictionary["retweet_count"] = {'$gt':int(rt_count)}
			elif rt_count_type == "lt":
				filter_dictionary["retweet_count"] = {'$lt':int(rt_count)}
			elif rt_count_type == "eq":
				filter_dictionary["retweet_count"] = {'$eq':int(rt_count)}
			elif rt_count_type == "le":
				filter_dictionary["retweet_count"] = {'$lte':int(rt_count)}
			elif rt_count_type == "ge":
				filter_dictionary["retweet_count"] = {'$gte':int(rt_count)}

	if fav_count != None:
		favcountType = fav_count[:2].lower()
		fav_count = fav_count[2:]
		if fav_count.isdigit():
			if favcountType == "gt":
				filter_dictionary["favorite_count"] = {'$gt':int(fav_count)}
			elif favcountType == "lt":
				filter_dictionary["favorite_count"] = {'$lt':int(fav_count)}
			elif favcountType == "eq":
				filter_dictionary["favorite_count"] = {'$eq':int(fav_count)}
			elif favcountType == "le":
				filter_dictionary["favorite_count"] = {'$lte':int(fav_count)}
			elif favcountType == "ge":
				filter_dictionary["favorite_count"] = {'$gte':int(fav_count)}

	result = []
	for i in tweets.find(filter_dictionary, {'hashtags_lower':0, 'text_lower':0, 'keyword':0,
		'user_mentions_lower':0}).sort([(sort, sortType)]):

		i['user'] = users.find_one(
				{'id':i['user']},
				{'name':1,'screen_name':1,'followers_count':1, 'location':1, 'id':1}
			)

		result.append(i)

	if sort_Two != None:
		if sort_Two == "user":
			result = sorted(result, key=lambda k: k['user']['name'])
		elif sort_Two == "screen_name":
			result = sorted(result, key=lambda k: k['user']['screen_name'])
		elif sort_Two == "followers_count":
			result = sorted(result, key=lambda k: k['user']['followers_count'])
		if sortType2 == "dsc":
			result = result[::-1]

	return result

@app.route("/search/", methods=['GET','POST'])
def search():
	try:
		name = request.args.get('name')
	        start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
		rt_count = request.args.get('rt_count')
		fav_count = request.args.get('fav_count')
                text = request.args.get('text')
		hashtag = request.args.get('hashtag')

		mention = request.args.get('mention')
	        location = request.args.get('location')
                keyword = request.args.get('keyword')
    	        sortPar = request.args.get('sort')
                language = request.args.get('lang')
		page = request.args.get('page')

		follow_count = request.args.get('followers')
		typeTw = request.args.get('type')

		result = filterData(name, text, rt_count, fav_count, start_date, end_date, language,
			mention, sortPar, hashtag, follow_count, typeTw, location, keyword)

		limit = 10
		if page == None or not page.isdigit() or int(page)<1:
			page = 1
		else:
			page = int(page)
		next_page = page+1
		last_page = False
		if len(result) <=(page*limit):
			last_page = True
			next_page = 1

		count = len(result)
		result = result[((page-1)*limit) : (page*limit)]

		return JSONEncoder().encode({'result': result, 'result_count': count, 'page': page,
									'next_page':next_page, 'last_page':last_page})
	except:
		return jsonify({"code":"1","status":"failed","message":"Some error occured"})

@app.route("/getcsv/", methods=['GET','POST'])
def getcsv():
	# try:
		name = request.args.get('name')
		start_date = request.args.get('start_date')
		hashtag = request.args.get('hashtag')
		follow_count = request.args.get('followers')
		typeTw = request.args.get('type')
		location = request.args.get('location')
		end_date = request.args.get('end_date')
		language = request.args.get('lang')
		mention = request.args.get('mention')
		sortPar = request.args.get('sort')
		text = request.args.get('text')
		rt_count = request.args.get('rt_count')
		fav_count = request.args.get('fav_count')
		keyword = request.args.get('keyword')

		result = filterData(name, text, rt_count, fav_count, start_date, end_date, language,
			mention, sortPar, hashtag, follow_count, typeTw, location, keyword)

		csvfile = "id,created_at,language,user_name,user_screen_name,user_followers,user_location,"\
		"user_id,text,hashtags,mentions,retweet_count,favorite_count,is_retweet,is_quote\n"
		for i in result:
			i['text'] = i['text'].replace("\n", " ")
			csvfile += ",".join([str(i['id']), str(i['created_at']),i['lang'], i['user']['name'],
				i['user']['screen_name'],str(i['user']['followers_count']),str(i['user']['location']) ,
				str(i['user']['id']), i['text'], "-".join(i['hashtags']), "-".join(i['user_mentions']),
				str(i['retweet_count']), str(i['favorite_count']),
				str(i['is_retweet']), str(i['is_quote_status'])]) + "\n"
		response = make_response(csvfile)
		cd = 'attachment; filename=twitterStream.csv'
		response.headers['Content-Disposition'] = cd
		response.mimetype='text/csv'

		return response
if __name__ == '__main__':
	app.run()
