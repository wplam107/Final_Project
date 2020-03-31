import numpy as np
import pandas as pd
import re
import os
import time
import datetime
import random
import requests
from os import system
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CNN FUNCTIONS

def scrape_urls_cnn(urls, dates, start, stop, driver):
    '''
    Function to scrape all urls of topic
    '''
    time.sleep(5)
    xpath = '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]/div[{}]/div[2]/div[1]/span[2]'
    a_xpath = '/html/body/div[5]/div[2]/div/div[2]/div[2]/div/div[3]/div[{}]/div[2]/h3/a'
    ymd_start = datetime(start[0], start[1], start[2]).date()
    ymd_stop = datetime(stop[0], stop[1], stop[2]).date()
    
    # Scrape urls of each page
    for i in range(10):
        try:
            ele = driver.find_element_by_xpath(xpath.format(i+1)).text.replace(',', '')
            ts = datetime.strptime(ele, '%b %d %Y').date()
            href = driver.find_element_by_xpath(a_xpath.format(i+1)).get_attribute('href')
            if ts < ymd_start:
                print('All URLS in date range scraped')
                print(f'Number of article URLs: {len(urls)}\n')
                return urls, dates
            elif ts < ymd_stop:
                if re.search('(live-news)', href) or re.search('(style)', href):
                    continue
                else:
                    urls.append(href)
                    dates.append(ts)
        except:
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

def scrape_one_cnn(url, driver):
    '''
    Function to scrape headline, byline, and article body
    '''
    try:
        driver.get(url)
        time.sleep(2)
        headline = driver.find_element_by_class_name('pg-headline').text
        texts = driver.find_elements_by_class_name('zn-body__paragraph')
        article = ' '.join([ text.text for text in texts ])
        article = _clean_body(article)
        byline = driver.find_element_by_class_name('metadata__byline__author').text
    except:
        headline = 'No headline'
        byline = 'No byline'
        article = 'No text'
        
    return headline, byline, article     

def scrape_articles_cnn(urls, dates, headlines, bylines, bodies, start, stop, driver):
    '''
    Function to scrape all designated articles
    '''
    urls, dates = scrape_urls_cnn(urls, dates, start, stop, driver)
    
    for url in urls:
        headline, byline, article = scrape_one_cnn(url, driver)
        bodies.append(article)
        headlines.append(headline)
        bylines.append(byline)
        
    return urls, dates, headlines, bylines, bodies      

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
    driver.get('https://www.cnn.com/search?q=Hong%20Kong%20Protest&size=10&type=article')

    urls = []
    dates = []
    headlines = []
    bylines = []
    bodies = []
    
    urls, dates, headlines, bylines, bodies = scrape_articles_cnn(urls, dates, headlines, bylines, bodies, start, stop, driver)
    df = pd.DataFrame()
    df['url'] = urls
    df['date'] = dates
    df['headline'] = headlines
    df['byline'] = bylines
    df['body'] = bodies
    df['source'] = 'CNN'
    df['index'] = range(len(df.index))
    df.set_index('index', inplace=True)

    # Quit driver
    driver.quit()
    
    # Convert to .csv (with tab delimiter)
    if ret_csv == True:
        df.to_csv(csv, sep='\t')
        print('CSV Created')
    
    if ret_df == True:
        return df
        
    return