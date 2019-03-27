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

		print('\nInserting New Videos...\n')
		obj_list= []
		for url in new_urls:
			title= self.__get_title(url)
			obj= {'url': url, 'title': title}
			obj_list.append(obj)

		_= self.videos.insert_many(obj_list)

	def delete_videos(self, titles= []):
		'''
		Delete documents from Videos collection
		'''
		for title in titles:
			self.videos.delete_one({'title': title})

	def create_playlist(self, name= "", titles= []):
		'''
		Create new playlist
		'''
		_= self.playlist.insert_one({'name': name, 'list': titles})

	def get_urls(self):
		'''
		Return a list of urls stored in videos collection
		'''
		urls= [doc['url'] for doc in self.videos.find({}, {'_id': 0, 'url': 1})]
		return urls

	def get_docs(self):
		'''
		Return a list of documents stored in videos collection
		'''
		docs= [doc for doc in self.videos.find({}, {'_id': 0})]
		return docs
		
	def store_urls(self, out_file= 'stored_urls.txt'):
		'''
		Store urls and their titles in a text file
		'''
		docs= [doc for doc in self.videos.find({}, {'_id': 0})]
		vids= [doc['url']+ '  |  '+ doc['title'] for doc in docs]
		max_length_of_title= max([len(doc['title']) for doc in docs])

		header= ' '*20+ 'Url'+ ' '*20+ '  |  '+ ' '*(max_length_of_title//2 - 3)+ 'Title\n'
		border= '-'*(48+ max_length_of_title)+ '\n'

		with open(out_file, 'w') as f:
			f.write(header)
			f.write(border)
			f.writelines(vids)

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
	# obj.insert_videos()
	# obj.store_urls()