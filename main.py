#!/usr/bin/python3
import sys
import os

path = os.getcwd()
base_url = 'http://kissanime.ru/'
url = 'http://kissanime.ru/Anime/Nobunaga-no-Shinobi-Anegawa-Ishiyama-hen'

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

profile = webdriver.FirefoxProfile()
skipper = 'kissanime_skip-3.0-an.fx.xpi'
adblock = 'uBlock0.firefox.xpi'
# profile.add_extension(skipper)
# profile.add_extension(adblock)

driver = webdriver.Firefox(firefox_profile=profile)
driver.get(base_url + 'Login')

time.sleep(6)


input("Login to your account and press enter:\n")


driver.get(url)

html = driver.page_source

import bs4
soup = bs4.BeautifulSoup(html)

table = soup.find("table", class_="listing")
eps = table.find_all('a')

ep_links = []
for ep in eps:
    link = ep.get_attribute_list('href')[0]
    ep_links.insert(0, base_url + link)

for i, link in enumerate(ep_links):
    print("%d: %s" % (i, link))

start = int(input('Start Ep:\n'))

end = int(input('End Ep:\n')) + 1

dl_links = []
filenames = []
for i in range(start, end):

    link = ep_links[i]
    driver.get(link)
    input("Complete captcha and press enter:\n")

    names = driver.title.split('Episode')
    name = names[0].strip().replace(' ', '_')
    ep = names[1].split('-')[0].strip()
    filename = name + '/' + name + '-' + ep + '.mp4'
    filenames.append(filename)

    soup = bs4.BeautifulSoup(driver.page_source)
    dl_link = soup.find('video').get_attribute_list('src')[0]
    dl_links.append(dl_link)
    print(dl_link)
    
if not os.path.exists(name):
    os.mkdir(name)

for dl_link, filename in zip(dl_links, filenames):
    print(dl_link, filename)

import subprocess

def download(args, link, filename=None):
    removal = -1
    for i in range(len(args)):
        if args[i] == '%file':
            if filename:
                args[i] = filename
            else:
                removal = i
        elif args[i] == '%link':
            args[i] = link

    if removal != -1:
        args.pop(removal)

    print ('+ %s' % ( ' '.join(args) ))
    p = subprocess.Popen(args)
    p.wait()


opt = input(
    'Any prefered download method? \nSpecify the exact command to run [wget %link -O %file]:\n')

aria = 'aria2c -x 16 -o %file %link'
wget = 'wget %link -O %file'

if opt.strip() == '':
    args = wget.split()
else:
    args = opt.strip().split()


processes = []
with open('out.sh', 'w') as f:
    for dl_link, filename in zip(dl_links, filenames):
        removal = -1
        for i in range(len(args)):
            if args[i] == '%file':
                if filename:
                    args[i] = '"' + filename + '"'
                else:
                    removal = i
            elif args[i] == '%link':
                args[i] = '"' + dl_link + '"'

        if removal != -1:
            args.pop(removal)

        print('+ %s' % (' '.join(args)))
        f.write(' '.join(args) + ' & \n')
