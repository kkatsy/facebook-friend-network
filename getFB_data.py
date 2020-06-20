from html.parser import HTMLParser
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from tqdm import tqdm
import pickle
import random


def get_fb_page(url):
    """
    Gather your friends page data
    :param url: string          # url of your friends page
    :return: html_source        # html contents of your friends page
    """
    # start the driver
    time.sleep(random.randint(2, 4))
    driver.get(url)

    # get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # scroll get to end of friends page
    while True:
        time.sleep(random.randint(1, 4))
        # scroll to the bottom of page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait for page to load
        time.sleep(random.randint(2, 4))

        # calculate + compare scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height

    html_source = driver.page_source

    return html_source


def find_friend_from_url(url):
    """
    Gets a friend's username from their url
    :param url: string          # url of friend's page
    :return: friend             # friend's id # or username
    """
    # check if friend has a # for id
    if re.search('com\/profile.php\?id=\d+\&', url) is not None:
        m = re.search('com\/profile.php\?id=(\d+)\&', url)
        friend = m.group(1)
    # else get their distinct username
    else:
        m = re.search('com\/(.*)\?', url)
        friend = m.group(1)

    return friend


def find_name_from_mutual_page(mutual_page):
    """
    Finds a friend's name from html contents of their page
    :param mutual_page: string         # html of mutual friend page
    :return: f_name                    # friend's name
    """
    # search for page title, which will be their name
    if re.search('</script><title id="pageTitle">(.*)</title>', mutual_page) is not None:
        m = re.search('</script><title id="pageTitle">(.*)</title>', mutual_page)
        f_name = m.group(1)
    else:
        f_name = "N/A"

    return f_name


class MyHTMLParser(HTMLParser):
    # list of friend's urls
    urls = []

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        """
        Extracts friend's urls from your page to get usernames

        """
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    if re.search('\?href|&href|hc_loca|\?fref', value) is not None:
                        if re.search('.com/pages', value) is None:
                            self.urls.append(value)


# Get person's facebook info, or can hard code it
username = input("Enter your FB username: ")
password = input("Enter you FB password: ")
name = input("Your full name on FB is: ")

# set up chrome driver for automation
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('http://www.facebook.com/')

# authenticate to facebook account
elem = driver.find_element_by_id("email")
elem.send_keys(username)
elem = driver.find_element_by_id("pass")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)
time.sleep(5)
print("Successfully logged in Facebook!")

SCROLL_PAUSE_TIME = 2

my_url = 'http://www.facebook.com/' + username + '/friends'

# create or open file with urls of all unique friends
UNIQ_FILENAME = 'uniq_urls.pickle'
# if file exists and has preexisting url data
if os.path.isfile(UNIQ_FILENAME):
    with open(UNIQ_FILENAME, 'rb') as f:
        uniq_urls = pickle.load(f)
    print('We loaded {} uniq friends'.format(len(uniq_urls)))
else:
    # scrape your fb page, get urls using parser class
    friends_page = get_fb_page(my_url)
    parser = MyHTMLParser()
    parser.feed(friends_page)
    uniq_urls = set(parser.urls)

    print('We found {} friends, saving it'.format(len(uniq_urls)))

    with open(UNIQ_FILENAME, 'wb') as f:
        pickle.dump(uniq_urls, f)

    # # uncomment if you want to examine html string of your friends page
    # # (in the case that fb changes their api or ui again)
    # with open("page_data.txt", "w") as text_file:
    #     text_file.write(friends_page)
    #     print("Saved friends page html data to file")

friend_graph = {}  # set of friends for graph creation
username_to_name = [(username, name)]  # list to connect usernames to names
GRAPH_FILENAME = 'friend_graph.pickle'
NAMES_FILENAME = 'name_to_id.pickle'

# if existing friend graph file, preload
if os.path.isfile(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'rb') as f:
        friend_graph = pickle.load(f)
    print('Loaded existing graph, found {} keys'.format(len(friend_graph.keys())))

# iterate through unique urls, show progress bar each iteration
count = 0
for url in tqdm(uniq_urls):

    # pause every 100 friends, so as to not overwhelm fb w automation
    count += 1
    if count % 100 == 0:
        print("100 queries completed, pause for a while...")
        time.sleep(180)

    # get username from url, make sure doesn't already exist in friend graph
    friend_username = find_friend_from_url(url)
    if (friend_username in friend_graph.keys()) and (len(friend_graph[friend_username]) > 1):
        continue

    # get html of mutual friends page
    mutual_url = 'https://www.facebook.com/{}/friends_mutual'.format(friend_username)
    mutual_page = get_fb_page(mutual_url)

    # extract friend's name from page, add to reference list
    friend_name = find_name_from_mutual_page(mutual_page)
    username_to_name.append((friend_username, friend_name))

    # add yourself as node
    friend_graph[friend_username] = [username]

    # get urls of mutual friends
    parser = MyHTMLParser()
    parser.urls = []
    parser.feed(mutual_page)
    mutual_urls = set(parser.urls)

    # make sure found urls in uniq_urls
    mutual_friends_urls = []
    for page in mutual_urls:
        if page in uniq_urls:
            mutual_friends_urls.append(page)
    print('Found {} urls'.format(len(mutual_friends_urls)))

    # get usernames of mutual friends
    for mutual_url in mutual_friends_urls:
        mutual_friend = find_friend_from_url(mutual_url)
        friend_graph[friend_username].append(mutual_friend)

    # pickle friend graph + username info in respective files
    with open(GRAPH_FILENAME, 'wb') as f:
        pickle.dump(friend_graph, f)

    with open(NAMES_FILENAME, 'wb') as f:
        pickle.dump(username_to_name, f)

    # pause before continuing to next friend
    time.sleep(random.randint(1, 4))
