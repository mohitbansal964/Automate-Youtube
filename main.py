from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

from dbms import Youtube


autoplay= True   #Default Youtube Autoplay is on
dark_theme= False #Dark Theme OFF


def print_title(docs= []):
	'''
	Print titles
	'''
	print('\nTitles:\n-------\n')
	for i in range(0, len(docs)):
		print(f'{i+1}. {docs[i]["title"]}')
	print()

def menu():
	'''
	Show menu
	'''
	print('\nMenu:\n-----\n')
	print('1. Play Videos')
	print('2. Show Playlists')
	print('3. Play Playlist')
	print('4. Create Playlist')
	print('5. Update Playlist')
	print('4. Exit')


def toggle_autoplay_to_off(driver):
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

def toggle_dark_theme_on(driver):
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


def play_video(driver, url= "", title= ""):
	'''
	Play Video on Chrome
	'''
	global autoplay, dark_theme

	driver.get(url)
	print(f'Playing {title}')

	start_time= time.time()
	player_status= driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
	
	while(player_status!= 0):
		cur_time= time.time()
		time_elapsed= cur_time- start_time
		player_status= driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

		if autoplay and time_elapsed>=5 :
			autoplay= toggle_autoplay_to_off(driver)

		if (not dark_theme) and time_elapsed>= 6:
			dark_theme= toggle_dark_theme_on(driver)
		time.sleep(1)

def enter_choice(driver):
	choice= int(input('Enter choice: '))
	if choice==1:
		title_nums= list(map(int, input('\nEnter title numbers: ').strip().split()))
		for title_num in title_nums:
			if title_num>len(docs):
				continue
			play_video(driver, docs[title_num-1]['url'], docs[title_num-1]['title'])
	elif choice==2:
		pass
	elif choice==3:
		pass
	else:
		return
	menu()
	enter_choice(driver)

if __name__== "__main__":
	ytube= Youtube()
	ytube.insert_videos()

	docs= ytube.get_docs()
	print_title(docs)

	chromeoptions=webdriver.ChromeOptions()
	chromeoptions.add_argument("start-maximized")
	chromeoptions.add_argument("--disable-notifications")
	
	driver= webdriver.Chrome(chrome_options=chromeoptions)

	menu()
	enter_choice(driver)
	
	driver.close()
