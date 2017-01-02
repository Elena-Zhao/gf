from bs4 import BeautifulSoup
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import pandas as pd
import datetime as dt

from utils import *

BASE_URL = 'https://www.groundfloor.us' 

class GoundFloor():
    def __init__(self, link):
        self.soup = BeautifulSoup(urlopen(link).read(), "lxml")
    
    def crawl(self):
        cards = self.soup.find_all("div", class_="card")

        loans = []
        count_err = 0
        for card in cards:
            loan = {}
            loan['title'] = card.find('div', class_="title").get_text()
#            loan['type'] = card.find('div', class_='inner-arrow').get_text().strip()  # status is given in details
            loan['grade'] = card.find('div', class_="triangle").get_text()

            loan['link'] = card.find('div', class_='large-link').find('a').attrs['href']
            
            details = self.crawl_details(BASE_URL + loan['link'])

            if details['parse_result']:  # we only insert when loan is successfully parsed
                loan.update(details)
                loans.append(loan)
            else:
                count_err += 1

            if len(loans) % 10 == 0:
                print("%d of %d loan crawled" % (len(loans), len(cards)))

        print("%d of %d loan crawled, %d failed" % (len(loans), len(cards), count_err))
        
        self.data = pd.DataFrame(loans)

        return self.data
    

    def crawl_details(self, detail_link):
        detail_soup = BeautifulSoup(urlopen(detail_link).read(), "lxml")
        
        company = detail_soup.find_all('div', class_='col-xs-11 anchor-link')[0].get_text().strip()
        borrower = detail_soup.find_all('div', class_='col-xs-11 anchor-link')[1].get_text().replace(' - principal', '').strip()
        
        rate = float(detail_soup.find_all('div', class_='black-box')[0].get_text().replace('%', '')) / 100
        term = int(detail_soup.find_all('div', class_='black-box')[1].get_text().split()[0])
        loan_to_value = float(detail_soup.find_all('div', class_='black-box')[2].get_text().replace('%', '')) / 100
        amount = parse_currency(detail_soup.find_all('div', class_='black-box')[3].get_text())
        investers = int(detail_soup.find_all('div', class_='black-box')[4].get_text())
        
        purpose = detail_soup.find_all('div', class_='white-box')[0].get_text().strip()
        position = detail_soup.find_all('div', class_='white-box')[1].get_text()
        total_amount = parse_currency(detail_soup.find_all('div', class_='white-box')[2].get_text())
       
        try:
            start_on = parse_date(detail_soup.find_all('div', class_='value-in-box col-xs-7')[0].get_text())
            funded_on = parse_date(detail_soup.find_all('div', class_='value-in-box col-xs-7')[1].get_text())
            repaid_on = parse_date(detail_soup.find_all('div', class_='value-in-box col-xs-7')[2].get_text())
            matures_on = parse_date(detail_soup.find_all('div', class_='value-in-box col-xs-7')[3].get_text())
            parse_result = True
        except IndexError:
            print('dates for %s unavailable' % (detail_link))
            return {'parse_result' : False}
 
        status_info = detail_soup.find_all('div', class_='white-box')[3].get_text().strip().split()
        status = status_info[0]
        if matures_on == 'NA':
            matures_on = start_on + dt.timedelta(30*term)
        if status == 'Funded' and dt.datetime.today() > matures_on:
            status = 'Late'
            
        address = detail_soup.find(id = 'cucumber-investment').find('a').get_text()
        address_array = address.split()
        if len(address_array) > 2:
            zipcode = int(address_array[-1])
            state = address_array[-2]
        else:
            zipcode = 'NA'
            state = address_array[-1]

        description = detail_soup.find(id = 'cucumber-investment').find('div', class_ = "col-xs-12").get_text().strip()
        
        return {'company' : company, 
                'borrower' : borrower, 
                'rate' : rate,
                'term' : term,
                'loan_to_value' : loan_to_value,
                'amount' : amount, 
                'investers' : investers, 
                'purpose' : purpose,
                'position' : position, 
                'investers' : investers,
                'purpose' : purpose, 
                'total_amount' : total_amount, 
                'status' : status, 
                'start_on' : start_on, 
                'funded_on' : funded_on, 
                'repaid_on' : repaid_on, 
                'matures_on' : matures_on,
                'address' : address, 
                'state' : state,
                'zipcode' : zipcode,
                'description' : description,
                'parse_result': parse_result
                }

