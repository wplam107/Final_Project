import numpy as np
import pandas as pd
import re
import os
import time
import datetime
import random
import requests
import pickle
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
def scrape_urls_cnn(urls, dates, start, stop, driver):
    '''
    Function to scrape all urls of topic
    '''
    time.sleep(2)
    xpath = '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]/div[{}]/div[2]/div[1]/span[2]'
    a_xpath = '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]/div[{}]/div[2]/h3/a'
    ymd_start = datetime(start[0], start[1], start[2]).date()
    ymd_stop = datetime(stop[0], stop[1], stop[2]).date()
    
    # Scrape urls of each page
    for i in range(10):
        counter = 0
        try:
            ele = driver.find_element_by_xpath(xpath.format(i+1)).text.replace(',', '')
            ts = datetime.strptime(ele, '%b %d %Y').date()
            href = driver.find_element_by_xpath(a_xpath.format(i+1)).get_attribute('href')
            if ts < ymd_start:
                continue
            elif ts < ymd_stop:
                if re.search('(live-news)', href):
                    continue
                else:
                    urls.append(href)
                    dates.append(ts)
        except:
            counter += 1
            if counter < 5:
                continue
            else:
                print('All URLS in date range scraped')
                print(f'Number of article URLs: {len(urls)}\n')
                return urls, dates
    
    # Click to next page if there is one
    try:
        np_xpath= '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[5]/div/div[3]'
        driver.find_element_by_xpath(np_xpath).click()
    except:
        print('No more pages')
        print(f'Number of article URLs: {len(urls)}\n')
        return urls, dates

    return scrape_urls_cnn(urls, dates, start, stop, driver)

# Helper function to clean body of article
def _clean_body(article):
    cleaned = re.sub(r"^.*?\)|(CNN's.*)", "", article)
    return cleaned

def scrape_one_cnn(url, driver, count_sc, count_no):
    '''
    Function to scrape headline and article body
    '''
    driver.get(url)
    time.sleep(3)

    # Click modal button
    try:
        modal_button = driver.find_element_by_class_name('bx-close bx-close-link bx-close-inside')
        modal_button.click()
    except:
        pass

    try:
        headline = driver.find_element_by_class_name('pg-headline').text
        texts = driver.find_elements_by_class_name('zn-body__paragraph')
        article = ' '.join([ text.text for text in texts ])
        article = _clean_body(article)
        count_sc += 1
    except:
        count_no += 1
        headline = 'No headline'
        article = 'No text'
        
    return headline, article, count_sc, count_no  

def scrape_articles_cnn(urls, dates, headlines, bodies, start, stop, driver):
    '''
    Function to scrape all designated articles
    '''
    urls, dates = scrape_urls_cnn(urls, dates, start, stop, driver)
    
    count_sc = 0
    count_no = 0

    for url in urls:
        headline, article, count_sc, count_no = scrape_one_cnn(url, driver, count_sc, count_no)
        bodies.append(article)
        headlines.append(headline)
    
    print(f'Number of Articles Scraped: {count_sc}\n')
    print(f'Number of Articles w/o Text: {count_no}\n')

    return urls, dates, headlines, bodies      

def scrape_cnn(start, stop, ret_csv=False, csv='', ret_df=True):
    '''
    Function to convert data to DataFrame and .csv

    Parameters:
        start : tuple (Y, m, d), inclusive start date for article scraping
        stop : tuple (Y, m, d), exclusive stop date for article scraping
        ret_csv : bool (default False), True returns .csv file
        csv : str (path), path for .csv file if ret_csv=True
        ret_df : bool (default False), True returns DataFrame
    '''
    # Instantiate driver
    driver = webdriver.Chrome()
    driver.get('https://www.cnn.com/search?q=hong%20kong%20protests&size=10&page=1&category=world&type=article')

    urls = []
    dates = []
    headlines = []
    bodies = []
    
    urls, dates, headlines, bodies = scrape_articles_cnn(urls, dates, headlines, bodies, start, stop, driver)
    df = pd.DataFrame()
    df['url'] = urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'CNN'
    df['index'] = range(len(df.index))
    df.set_index('index', inplace=True)

    # Quit driver
    driver.quit()
    
    # Convert to .csv (with tab delimiter)
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    if ret_df == True:
        return df
    return

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
    '''
    Function to scrape 1 SCMP headline, text, body
    '''
    driver.get(url)
    try:
        headline = driver.find_element_by_class_name('info__headline').text
        hl = driver.find_element_by_class_name('info__headline')
        
    except:
        count_no += 1
        headline = 'No headline'
        article = 'No text'
        return headline, article, count_sc, count_no    

    actions = ActionChains(driver)
    time.sleep(5)
    actions.double_click(hl).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).pause(0.5).send_keys(Keys.SPACE).perform()

    # Click modal and full article button
    try:
        modal_button = driver.find_element_by_class_name('bottom-bar-close-button')
        modal_button.click()
    except:
        pass

    try:
        texts = driver.find_elements_by_class_name('generic-article__body')
        article = []
        for text in texts:
            cond1 = re.search('Photo:', text.text)
            cond2 = re.search('CORONAVIRUS UPDATE NEWSLETTER', text.text)
            cond3 = re.search('Privacy Policy', text.text)
            if cond1 or cond2 or cond3:
                pass
            else:
                article.append(text.text)
        article = ' '.join(' '.join(article).split('\n'))
        count_sc += 1
    except:
        count_no += 1
        headline = 'No headline'
        article = 'No text'

    return headline, article, count_sc, count_no

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
        time.sleep(random.uniform(0, 2))
        headline, article, count_sc, count_no = scrape_one_scmp(url, driver, count_sc, count_no)
        bodies.append(article)
        headlines.append(headline)

        if (count_sc + count_no) % 25 == 0 and (count_sc + count_no) != 0:
            driver.quit()
            time.sleep(15)
            driver = webdriver.Chrome()
            driver.maximize_window()
            time.sleep(15)
        if (count_sc + count_no) % 50 == 0 and (count_sc + count_no) != 0:
            time.sleep(random.uniform(8, 12))
            print(f'Current articles scraped: {count_sc + count_no}')
        if (count_sc + count_no) % 250 == 0 and (count_sc + count_no) != 0:
            hl_file = open(f'scmp_hl{count_sc + count_no}.p', 'wb')
            pickle.dump(headlines, hl_file)
            hl_file.close()
            bdies_file = open(f'scmp_bdies{count_sc + count_no}.p', 'wb')
            pickle.dump(bodies, bdies_file)
            bdies_file.close()
            
    # Quit driver
    driver.quit()
    
    print(f'Number of Articles Scraped: {count_sc}\n')
    print(f'Number of Articles w/o Text: {count_no}\n')

    return headlines, bodies

def scrape_scmp(urls, dates, ret_csv=False, csv='', ret_df=True):
    '''
    Function to convert data to DataFrame and .csv

    Parameters:
        start : tuple (Y, m, d), inclusive start date for article scraping
        stop : tuple (Y, m, d), exclusive stop date for article scraping
        scroll : int, number of scrolls through SCMP web search
        ret_csv : bool (default False), True returns .csv file
        csv : str (path), path for .csv file if ret_csv=True
        ret_df : bool (default False), True returns DataFrame
    '''

    headlines = []
    bodies = []
    
    headlines, bodies = scrape_articles_scmp(urls, headlines, bodies)
    df = pd.DataFrame()
    df['url'] = urls
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'SCMP'
    df['index'] = range(len(df.index))
    df.set_index('index', inplace=True)
    
    # Convert to .csv (with tab delimiter)
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    if ret_df == True:
        return df
    return

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

def scrape_one_abc(url, driver, count_sc, count_no):
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2)

    try:
        date = driver.find_element_by_css_selector('time').get_attribute('title')
        date = datetime.strptime(date.split(',')[0], '%a %d %b %Y').date()
    except:
        date = driver.find_element_by_css_selector('time').text
        date = ' '.join(date.split(' ')[1:4])
        try:
            date = datetime.strptime(date, '%d %B %Y').date()
        except:
            date = datetime.strptime(date, '%d %b %Y').date()

    headline = driver.find_element_by_css_selector('h1').text
    eles = driver.find_elements_by_xpath('//*[@id="main_content"]/div[1]/div/div[1]/div/p')
    body = []
    for ele in eles:
        p = ele.text
        cond1 = re.search('Topics:', p)
        cond2 = re.search('Updated', p)
        cond3 = re.search('First posted', p)
        cond4 = re.search('Source:', p)
        if cond1 or cond2 or cond3 or cond4 or p == '':
            continue
        else:
            body.append(p)

    body = ' '.join(body)
    count_sc += 1
    if count_sc % 10 == 0:
        print(f'Articles scraped so far: {count_sc}')
    return date, headline, body, count_sc, count_no

def scrape_all_abc(urls, ret_csv=False, csv='', ret_df=True):
    driver = webdriver.Chrome()
    driver.maximize_window()

    dates = []
    headlines = []
    bodies = []
    urls_sc = []

    count_sc = 0
    count_no = 0

    for url in urls:
        if re.search('interactive', url) or re.search('documentary', url):
            count_no += 1
            print(f'Articles bypassed so far: {count_no}')
            continue
        else:
            date, headline, body, count_sc, count_no = scrape_one_abc(url, driver, count_sc, count_no)
            urls_sc.append(url)
            dates.append(date)
            headlines.append(headline)
            bodies.append(body)
    
    driver.quit()
    print(f'Articles Scraped: {count_sc}')
    print(f'Articles Bypasses: {count_no}')

    df = pd.DataFrame()
    df['url'] = urls_sc
    df['date'] = dates
    df['headline'] = headlines
    df['body'] = bodies
    df['source'] = 'ABC (Australia)'
    df['index'] = range(len(urls_sc))
    df.set_index('index', inplace=True)

    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print(f'File {csv} Created')
    
    if ret_df == True:
        return df
    return
