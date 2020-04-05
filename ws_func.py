import numpy as np
import pandas as pd
import re
import os
import time
import datetime
import random
import requests
import pickle
import urllib
from bs4 import BeautifulSoup
from os import system
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# CNN FUNCTIONS
def urls_scrape_page_cnn(urls, page, driver):
    driver.get(page)
    time.sleep(5)
    xpath = '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]/div[{}]/div[2]/h3/a'
    counter = 0
    for i in range(1, 11):
        href = driver.find_element_by_xpath(xpath.format(i)).get_attribute('href')
        if re.search('live-news', href):
            continue
        else:
            counter += 1
            urls.append(href)
    print(f'Added {counter} URLs')
    return urls

def urls_scrape_all_cnn(driver):
    urls = []
    search_site = ['https://www.cnn.com/search?size=10&q=%22hong%20kong%20protests%22&type=article']
    s_pages = 'https://www.cnn.com/search?size=10&q=%22hong%20kong%20protests%22&page={}&from={}0&type=article'
    pages = search_site + [ s_pages.format(i, i-1) for i in range(2, 17) ]
    for page in pages:
        urls = urls_scrape_page_cnn(urls, page, driver)
    return urls

# Helper function to clean body of article
def _clean_body(article):
    cleaned = re.sub(r"^.*?\)|(CNN's.*)", "", article)
    return cleaned

def scrape_one_cnn(url, counter, driver):
    driver.get(url)
    body = []
    time.sleep(3)

    # Click modal button
    try:
        modal_button = driver.find_element_by_class_name('bx-close bx-close-link bx-close-inside')
        modal_button.click()
    except:
        pass
    
    try:
        date = driver.find_element_by_class_name('update-time').text
    except:
        date = ''
    try:
        headline = driver.find_element_by_class_name('pg-headline').text
    except:
        headline = ''
    try:
        texts = driver.find_elements_by_class_name('zn-body__paragraph')
        for text in texts:
            if re.search('CNN\'s', text.text):
                continue
            else:
                body.append(text.text)
        counter += 1
    except:
        body.append('')
    
    body = ' '.join(body)
        
    return url, date, headline, body, counter

def scrape_cnn(urls, driver, ret_csv=False, csv=''):
    new_urls = []
    dates = []
    headlines = []
    bodies = []
    
    counter = 0
    
    for url in urls:
        time.sleep(1)
        url, date, headline, body, counter = scrape_one_cnn(url, counter, driver)
        new_urls.append(url)
        dates.append(date)
        headlines.append(headline)
        bodies.append(body)
        if counter % 10 == 0:
            print(f'Articles scraped so far: {counter}')
            time.sleep(2)
    
    df = pd.DataFrame()
    df['url'] = new_urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'CNN'
    
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    return df

# SCMP functions

def _super_scroll(scroll, driver):
    '''
    Function to scroll down page, approximately 30 new articles per scroll
    '''
    # driver = webdriver.Chrome()
    # driver.get('https://www.scmp.com/topics/hong-kong-protests')

    i = 0
    while i < scroll:
        try:
            actions = ActionChains(driver)
            more_content = driver.find_element_by_class_name('topic-content__load-more-anchor')
            actions.move_to_element(more_content).double_click(more_content).pause(1).send_keys(Keys.SPACE).perform()
            i += 1
            time.sleep(random.uniform(2, 5))
            if i % 10 == 0:    
                print(f'Scrolls: {i}')
        except:
            modal_button = driver.find_element_by_class_name('bottom-bar-close-button')
            modal_button.click()

            actions = ActionChains(driver)
            more_content = driver.find_element_by_class_name('topic-content__load-more-anchor')
            actions.move_to_element(more_content).double_click(more_content).pause(1).send_keys(Keys.SPACE).perform()
            i += 1
            time.sleep(random.uniform(2, 5))
            if i % 10 == 0:    
                print(f'Scrolls: {i}')

    # Find total articles
    time.sleep(8)
    total = len(driver.find_elements_by_xpath('//*[@id="topic-detail"]/div[1]/div/div[5]/div[2]/*'))
    print(f'Total articles: {total}\n')
    time.sleep(1)
    return total

def scrape_urls_scmp(scroll):
    '''
    Function to scrape URLs and dates

    Parameters:
        scroll : int, number of scrolls through SCMP web search
    '''
    # Instantiate driver
    driver = webdriver.Chrome()
    driver.get('https://www.scmp.com/topics/hong-kong-protests')
    

    # Scroll through pages
    total = _super_scroll(scroll, driver)

    urls = []
    dates = []

    counter = 0
    xpath = '//*[@id="topic-detail"]/div[1]/div/div[5]/div[2]/div[{}]/div[1]/div[2]/div[1]/div/span'
    a_xpath = '//*[@id="topic-detail"]/div[1]/div/div[5]/div[2]/div[{}]/div[1]/div[1]/div/div/div[2]/a'

    for i in range(total):
        try:
            ele = driver.find_element_by_xpath(xpath.format(i+1)).text
            ts = datetime.strptime(ele, '%d %b %Y - %H:%M%p').date()
            href = driver.find_element_by_xpath(a_xpath.format(i+1)).get_attribute('href')
            if re.search('news', href):
                urls.append(href)
                dates.append(ts)
                counter += 1
                if counter % 50 == 0:
                    print(f'URLs scraped so far: {counter}')
        except:
            continue
    
    # driver.quit()
    print('\n')
    print(f'Number of URLs Scraped: {len(urls)}')
    print(f'Number of Dates Scraped: {len(dates)}')
    return urls, dates

def scrape_one_scmp(url, driver, count_sc, count_no):
    driver.get(url)
    if re.search('/video/', url) or re.search('/infographics/', url) or re.search('united-states-canada', url):
        time.sleep(8)
        headline = ''
        body = ''
        count_no += 1
        return headline, body, count_sc, count_no
    
    try:
        head = driver.find_element_by_class_name('info__headline')
        if head == None:
            head = driver.find_elements_by_css_selector('h1')
        headline = head.text
    except:
        headline = ''  

    actions = ActionChains(driver)
    time.sleep(5)
    actions.double_click(head).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).perform()

    # Click modal and full article button
    try:
        modal_button = driver.find_element_by_class_name('bottom-bar-close-button')
        modal_button.click()
    except:
        pass
    try:
        text_body = driver.find_element_by_class_name('details__body')
        texts = text_body.find_elements_by_class_name('generic-article__body')
        if texts == None:
            texts = text_body.find_elements_by_css_selector('p')
    except:
        body = ''
        count_no += 1
        return headline, body, count_sc, count_no

    body = []
    for text in texts:
        cond1 = re.search('Photo:', text.text)
        cond2 = re.search('CORONAVIRUS UPDATE NEWSLETTER', text.text)
        cond3 = re.search('Privacy Policy', text.text)
        cond4 = re.search('Advertisement', text.text)
        if cond1 or cond2 or cond3 or cond4:
            continue
        else:
            body.append(text.text)
    body = ' '.join(body)
    if body == '':
        count_no += 1
    else:
        count_sc += 1
        
    return headline, body, count_sc, count_no

def scrape_articles_scmp(urls, headlines, bodies):
    '''
    Function to scrape all designated articles
    '''
    # Instantiate driver
    driver = webdriver.Chrome()
    driver.maximize_window()

    count_sc = 0
    count_no = 0

    for url in urls:
        time.sleep(random.uniform(1, 3))
        headline, body, count_sc, count_no = scrape_one_scmp(url, driver, count_sc, count_no)
        bodies.append(body)
        headlines.append(headline)

        if (count_sc + count_no) % 20 == 0 and (count_sc + count_no) != 0:
            print(f'Current articles scraped: {count_sc + count_no}')
            driver.quit()
            time.sleep(20)
            driver = webdriver.Chrome()
            driver.maximize_window()
            time.sleep(20)

        if (count_sc + count_no) % 40 == 0 and (count_sc + count_no) != 0:
            time.sleep(10)
            
    # Quit driver
    driver.quit()
    
    print(f'Number of Articles Scraped: {count_sc}\n')
    print(f'Number of Articles w/o Text: {count_no}\n')

    return headlines, bodies

def scrape_scmp(urls, dates, ret_csv=False, csv=''):
    headlines = []
    bodies = []
    
    headlines, bodies = scrape_articles_scmp(urls, headlines, bodies)
    df = pd.DataFrame()
    df['url'] = urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'SCMP'
    
    # Convert to .csv (with tab delimiter)
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    return df

# ABC (Australia) Functions

def url_scrap_page_abc(urls, page, driver):
    a_xpath = '//*[@id="#content"]/section[2]/div/div[3]/div[2]/ul/li[{}]/div/article/div/div[1]/div/a'
    driver.get(page)
    time.sleep(random.uniform(2, 4))
    for i in range(0, 10):
        url = driver.find_element_by_xpath(a_xpath.format(i+1)).get_attribute('href')
        if re.search('news', url):
            urls.append(url)
    return urls

def url_scrape_all_abc(driver):
    page_range = range(1, 15)
    href = 'https://search-beta.abc.net.au/#/?query=%22hong%20kong%20protests%22&page={}&configure%5BgetRankingInfo%5D=true&configure%5BclickAnalytics%5D=true&configure%5BuserToken%5D=anonymous-02f5b4b2-06b4-4402-9b15-3cc4fc5dbb64&configure%5Banalytics%5D=true&sortBy=ABC_production_all_latest&refinementList%5Bsite.title%5D%5B0%5D=ABC%20News'
    pages = [ href.format(i) for i in page_range ]
    urls = []
    for page in pages:
        urls = url_scrap_page_abc(urls, page, driver)
    print(f'Total Articles: {len(urls)}')
    return urls

def bs_scrape_body_abc(url):
    print(url)
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    article = soup.find('div', class_='article section')
    if article == None:
        article = soup.find('article')
    if article == None:
        article = soup.find('div', class_='comp-rich-text article-text clearfix')
    ps = article.find_all('p')
    date = article.find('span', class_='timestamp')
    if date == None:
        date = article.find('time')['datetime']
    else:
        date = date.get_text()
        try:
            date = re.findall(r'([a-zA-Z]+\s\d+\,\s\d+)', date)[0]
        except:
            date = re.findall(r'([a-zA-Z]+\s\d+\s\d+)', date)[0]
    headline = article.find('h1').string
    body = []
    for p in ps:
        text = p.get_text()
        cond1 = re.search('Updated', text)
        cond2 = re.search('Topics:', text)
        cond3 = re.search('First posted', text)
        cond4 = re.search('Posted', text)
        cond5 = re.search('Source:', text)
        if cond1 or cond2 or cond3 or cond4 or cond5:
            continue
        else:
            body.append(text)
    body = ' '.join(body)
    return url, headline, date, body

def bs_scrape_abc(urls, ret_csv=False, csv=''):
    new_urls = []
    headlines = []
    dates = []
    bodies = []
    source = 'ABC (Australia)'
    
    counter = 0
    
    for url in urls:
        cond1 = re.search('interactive', url)
        cond2 = re.search('documentary', url)
        cond3 = re.search('the-world', url)
        cond4 = re.search('newschannel', url)
        cond5 = re.search('science', url)
        if cond1 or cond2 or cond3 or cond4 or cond5:
            continue
        else:
            time.sleep(random.uniform(1, 2))
            url, headline, date, body = bs_scrape_body_abc(url)
            new_urls.append(url)
            headlines.append(headline)
            dates.append(date)
            bodies.append(body)
            counter += 1
            if counter % 10 == 0:
                print(f'Scraped so far: {counter}')
    
    df = pd.DataFrame()
    df['url'] = new_urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = source
    
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    return df

# CCTV Functions

def url_scrape_page_cctv(urls, page, counter):
    link = urllib.request.urlopen(page)
    soup = BeautifulSoup(link, 'html.parser')
    heads = soup.find_all('h1')
    for head in heads:
        href = head.find('a').get('href')
        urls.append(href)
        counter += 1
    return urls, counter

def url_scrape_all_cctv():
    urls = []
    cctv_search = 'http://so.cntv.cn/language/english/index.php?qtext=hong+kong+protest&type=1&sort=SCORE&page={}&vtime=-1&datepid=5&history=yes'
    pages = [ cctv_search.format(i) for i in range(1, 32) ]
    counter = 0
    for page in pages:
        urls, counter = url_scrape_page_cctv(urls, page, counter)
        if counter % 10 == 0:
            print(f'URLs scraped: {counter}')
    print(f'Total URLs scraped: {counter}')
    return urls

def scrape_body_cctv(url):
    body = []
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    page_body = soup.body
    headline = page_body.h3.get_text()
    headline = page_body.find('h3').get_text()
    date = page_body.find('h3').find_next_sibling('p').find_next_sibling('p').get_text()[:10]
    text_body = page_body.find(class_='text')
    ps = text_body.find_all('p')
    for p in ps:
        if re.search('Photo', p.get_text()):
            continue
        else:
            body.append(p.get_text())
    body = ' '.join(body)
    return url, date, headline, body

def scrape_cctv(urls, ret_csv=False, csv=''):
    new_urls = []
    dates = []
    headlines = []
    bodies = []
    
    counter = 0
    
    for url in urls:
        time.sleep(1)
        url, date, headline, body = scrape_body_cctv(url)
        new_urls.append(url)
        dates.append(date)
        headlines.append(headline)
        bodies.append(body)
        counter += 1
        if counter % 25 == 0:
            print(f'Articles scraped: {counter}')
    
    df = pd.DataFrame()
    df['url'] = new_urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'CCTV'
    
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    return df

# Reuters functions

# Function to clickdown for more articles till no more
def clickdown_reuters(driver):
    more_button = driver.find_element_by_xpath('//*[@id="content"]/section[2]/div/div[1]/div[4]/div/div[4]/div[1]')
    counter = 80
    while counter > 0:
        time.sleep(0.5)
        try:
            more_button.click()
            counter += 1
        except:
            break

def url_scrape_reuters(driver):
    eles = driver.find_elements_by_css_selector('h3')
    urls = [ ele.find_element_by_css_selector('a').get_attribute('href') for ele in eles ]   
    return urls

def scrape_one_reu(url):
    page = urllib.request.urlopen(url)
    time.sleep(1.5)
    soup = BeautifulSoup(page, 'html.parser')
    headline = soup.find('h1').get_text()
    date = soup.find('div', class_='ArticleHeader_date').get_text()
    text_body = soup.find('div', class_='StandardArticleBody_body')
    texts = text_body.find_all('p')
    body = []
    for text in texts:
        cond1 = re.search('Writing by', text.get_text())
        cond2 = re.search('Editing by', text.get_text())
        cond3 = re.search('Reporting by', text.get_text())
        if cond1 or cond2 or cond3:
            continue
        else:
            body.append(text.get_text())
    body = ' '.join(body)
    return url, date, headline, body

def scrape_reuters(urls, ret_csv=False, csv=''):
    new_urls = []
    dates = []
    headlines = []
    bodies = []
    
    counter = 0
    
    for url in urls:
        time.sleep(random.uniform(0.5, 1.5))
        url, date, headline, body = scrape_one_reu(url)
        new_urls.append(url)
        dates.append(date)
        headlines.append(headline)
        bodies.append(body)
        counter += 1
        if counter % 25 == 0:
            print(f'Articles scraped: {counter}')
    
    df = pd.DataFrame()
    df['url'] = new_urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'Reuters'
    print(f'Total Articles Scraped: {counter}')
    
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    return df