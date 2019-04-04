from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import random

from dbms import Youtube

# Chrome Driver
chromeoptions=webdriver.ChromeOptions()
chromeoptions.add_argument("start-maximized")
chromeoptions.add_argument("--disable-notifications")
driver= webdriver.Chrome(chrome_options=chromeoptions)

autoplay= True   #Default Youtube Autoplay is on
dark_theme= False #Dark Theme OFF
SHUFFLE= True   #Shuffle playlist
last_played= []   #Last Played videos

# Database Management
ytube= Youtube()
ytube.insert_videos()
docs= ytube.get_docs()


def print_title(docs= []):
	'''
	Print titles
	'''
	print('\nTitles:\n-------\n')
	for i in range(0, len(docs)):
		print(f'{i+1}. {docs[i]["title"]}')
	print()

def print_playlist_title(playlists= []):
	'''
	Print Playlists
	'''
	print('\nPlaylists:\n----------\n')
	for i in range(0, len(playlists)):
		print(f'{i+1}. {playlists[i]["name"]}')
	print()

def show_playlist(playlists= [], p_num= 0):
	'''
	Show Videos of a playlists
	'''
	print('\nPlaylist Content: ')
	for doc in playlists[p_num]['list']:
		print(doc['title'])
	print()

def toggle_autoplay_to_off():
	'''
	Turn off default youtube autoplay button
	'''
	try:
		element= driver.find_element_by_id('improved-toggle')
		if element.get_attribute('aria-pressed')=='true':
			print('Default Youtube Autoplay is turned off')
			element.click()
	except Exception as e:
			return True
	return False

def toggle_dark_theme_on():
	'''
	Turn dark theme ON if OFF
	'''
	try:
		topbar= driver.find_elements_by_tag_name('ytd-topbar-menu-button-renderer')[2]
		topbar.click()

		label= driver.find_element_by_id('label').text
		if label=='Dark theme: On':
			return True

		sec_icon= driver.find_element_by_id('secondary-icon')
		sec_icon.click()

		time.sleep(1)
		toggleButton= driver.find_elements_by_id('toggleButton')[2]
		toggleButton.click()

		topbar.click()
		print("Dark Theme On")
		return True

	except Exception as e:
		return False


def play_video(url= "", title= ""):
	'''
	Play Video on Chrome
	'''
	global autoplay, dark_theme, last_played

	driver.get(url)
	print(f'Playing {title}')

	start_time= time.time()
	player_status= driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

	while(player_status!= 0):
		cur_time= time.time()
		time_elapsed= cur_time- start_time
		player_status= driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

		if autoplay and time_elapsed>=5 :
			autoplay= toggle_autoplay_to_off()

		if (not dark_theme) and time_elapsed>= 8:
			dark_theme= toggle_dark_theme_on()
		time.sleep(1)
	last_played.append({'url': url, 'title': title})

def menu():
	'''
	Show menu
	'''
	print('\nMenu:\n-----')
	print('1. Play Videos')
	print('2. Play Playlist')
	print('3. Create Playlist')
	print('4. Update Playlist')
	print('5. Delete Videos')
	print('6. Delete Playlist')
	print('7. Store Contents in a text file')
	print('8. Exit')

def enter_choice():
	'''
	Enter choice
	'''
	global ytube, docs, playlists

	menu()
	choice= int(input('\nEnter choice: '))

	if choice==1:
		# Play videos
		print_title(docs)
		title_nums= list(map(int, input('\nEnter title numbers: ').strip().split()))
		for title_num in title_nums:
			if title_num>len(docs):
				continue
			url= docs[title_num-1]['url']
			title= docs[title_num-1]['title']
			count= ytube.get_count(title= title)
			play_video(url, title)
			ytube.update_count(title, count+1)

	elif choice==2:
		# Play Playlist
		playlists= ytube.get_playlists()
		print_playlist_title(playlists)
		playlist_num= int(input('Enter playlist number: '))
		if playlist_num<= len(playlists):
			show_playlist(playlists, playlist_num-1)
			playlist_docs= playlists[playlist_num-1]['list']
			if SHUFFLE:
				print('Shuffle is ON.')
				random.shuffle(playlist_docs)
			for doc in playlist_docs:
				url= doc['url']
				title= doc['title']
				count= ytube.get_count(title= title)
				play_video(url, title)
				ytube.update_count(title, count+1)

	elif choice==3:
		# Create Playlist
		print_title(docs)
		name= input('Enter name of playlist: ')
		title_nums= list(map(int, input('\nEnter title numbers: ').strip().split()))
		titles= []
		for title_num in title_nums:
			if title_num>len(docs):
				continue
			url= docs[title_num-1]['url']
			title= docs[title_num-1]['title']
			titles.append({'title': title, 'url': url})
		ytube.create_playlist(name= name, docs= titles)

	elif choice==4:
		# Update Playlist
		pass
	elif choice==5:
		#Delete videos
		print_title(docs)
		title_nums= list(map(int, input('\nEnter title numbers to delete: ').strip().split()))
		titles= []
		for title_num in title_nums:
			if title_num>len(docs):
				continue
			title= docs[title_num-1]['title']
			titles.append(title)
		ytube.delete_videos(titles= titles)

	elif choice==6:
		#Delete playlist
		playlists= ytube.get_playlists()
		print_playlist_title(playlists)
		playlist_num= int(input('Enter playlist number: '))
		if playlist_num<= len(playlists):
			name= playlists[playlist_num-1]['name']
			ytube.delete_playlist(name= name)

	elif choice==7:
		# Store Contents in a text file
		ytube.store_urls()

	else:
		# Exit
		driver.close()
		return
	enter_choice()

if __name__== "__main__":
	try:
		enter_choice()
	except Exception as e:
		print(e)
		driver.close()
	finally:
		ytube.update_playlist(name= 'Last Played', titles= last_played)
		print('Last Played')
		print_title(last_played)
