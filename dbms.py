import pymongo
from bs4 import BeautifulSoup
import requests

class Youtube:
	'''
	Youtube Database Management System
	'''
	def __init__(self):
		'''
		Establishing connection with MongoDB server
		Connecting Database and collections
		'''
		self.client= pymongo.MongoClient("mongodb://localhost:27017/")
		self.db= self.client['Youtube']
		self.playlist= self.db['Playlist']
		self.videos= self.db['Videos']
		self.history= self.db['History']

	def create_playlist(self, name= "", docs= []):
		'''
		Create new playlist
		'''
		_= self.playlist.insert_one({'name': name, 'list': docs})

	def insert_videos(self, filename= 'new_urls.txt', url_list= []):
		'''
		Inserting new urls and their titles in videos collection
		New Urls are present in new_urls.txt
		'''
		with open(filename, 'r') as f:
			urls= f.readlines()

		with open(filename, 'w') as f:
			f.write('') #Clear file

		if url_list!= []:
			urls.extend(url_list)

		urls_in_db=  self.get_urls()#Return only urls
		new_urls= []
		for i in range(len(urls)):
			url= urls[i]
			url= url.strip('\n ')
			urls[i]= url
			if urls[i] not in urls_in_db:
				new_urls.append(urls[i])

		if len(new_urls)==0:
			return

		print('\nInserting New Videos...')
		obj_list= []
		for url in new_urls:
			try:
				title= self.__get_title(url)
			except Exception as e:
				title= ''
			print(f'Inserted {title}')
			obj= {'url': url, 'title': title, 'count': 0}
			obj_list.append(obj)

		_= self.videos.insert_many(obj_list)

	def delete_videos(self, titles= []):
		'''
		Delete documents from Videos collection
		'''
		for title in titles:
			self.videos.delete_one({'title': title})

	def delete_playlist(self, name= ""):
		'''
		Delete playlist from Playlist collection
		'''
		self.playlist.delete_one({'name': name})

	def get_urls(self):
		'''
		Return a list of urls stored in videos collection
		'''
		urls= [doc['url'] for doc in self.videos.find({}, {'_id': 0, 'url': 1})]
		return urls

	def get_titles(self):
		'''
		Return a list of titles stored in videos collection
		'''
		urls= [doc['title'] for doc in self.videos.find({}, {'_id': 0, 'title': 1})]
		return urls

	def get_docs(self):
		'''
		Return a list of documents stored in videos collection
		'''
		docs= [doc for doc in self.videos.find({}, {'_id': 0})]
		docs= sorted(docs, key= lambda doc: doc['count'], reverse= True)
		return docs

	def get_playlists(self):
		'''
		Return a list of playlists
		'''
		docs= [doc for doc in self.playlist.find({}, {'_id': 0})]
		return docs

	def get_count(self, title= ""):
		'''
		Return count of a particular document
		'''
		return self.videos.find_one({'title': title}, {'_id': 0, 'count': 1})['count']

	def store_urls(self, out_file= 'stored_urls.txt'):
		'''
		Store urls and their titles in a text file
		'''
		docs= self.get_docs()
		vids= [doc['url']+ '  |  '+ doc['title']+'\n' for doc in docs]
		max_length_of_title= max([len(doc['title']) for doc in docs])

		header= ' '*20+ 'Url'+ ' '*20+ '  |  '+ ' '*(max_length_of_title//2 - 3)+ 'Title\n'
		border= '-'*(48+ max_length_of_title)+ '\n'

		with open(out_file, 'w') as f:
			f.write(header)
			f.write(border)
			f.writelines(vids)

	def update_count(self, title= "", count= 0):
		'''
		Update count of videos.
		'''
		self.videos.update_one({'title': title}, { "$set": { "count": count } })

	def update_playlist(self, name= "", titles =[]):
		'''
		Update list of videos in a playlist.
		'''
		self.playlist.update_one({'name': name}, {'$set': {'list': titles}})

	def __get_title(self, url):
		'''
		Get title of youtube videos using BeautifulSoup
		'''
		r= requests.get(url)
		if r.status_code==200:
			pg_src= r.content
			soup= BeautifulSoup(pg_src, 'html5lib')
			# title= str(soup.find('h1').text)
			title= soup.find(class_= 'watch-title').text.strip(' \n')
		else:
			title= ""
		return title

if __name__== '__main__':
	obj= Youtube()
	# print(obj.get_titles())
	# title= input('title:  ')
	# print(obj.get_count(title))
	# docs= obj.get_docs()
	# print(docs)
	# name= input('name: ')
	# title_nums= list(map(int, input('\nEnter title numbers: ').strip().split()))
	# titles= []
	# for title_num in title_nums:
	# 	if title_num>len(docs):
	# 		continue
	# 	url= docs[title_num-1]['url']
	# 	title= docs[title_num-1]['title']
	# 	titles.append({'title': title, 'url': url})
	# obj.create_playlist(name= name, docs= titles)
	# print(obj.get_playlists())
	# print(obj.get_docs())
	# obj.insert_videos()
	# obj.store_urls()
