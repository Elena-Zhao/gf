from bs4 import BeautifulSoup
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import pandas as pd
import datetime as dt
import re

from utils import *

BASE_URL = 'https://www.groundfloor.us' 

class GoundFloor():
    def __init__(self, link):
        self.soup = BeautifulSoup(urlopen(link).read(), 'lxml')
        self.data = None


    def save(self, filename):
        if self.data is not None:
            self.data.to_csv(filename)
        else:
            raise Exception('No data to save!')
    

    def read(self, filename):
        self.data = pd.read_csv(filename, index_col = 0)

    
    def crawl_funding(self):
        items = self.soup.find_all("div", class_="long-text-wrapper")
        loans = []
        print("Crawling investment loans")
        for item in items:
            loan = {}
            loan['title'] = item.find('a').get_text()
            loan['link'] = item.find('a').attrs['href']
            details = self.crawl_funding_details(BASE_URL + loan['link'])
            loan.update(details)
            loans.append(loan)
        
        print("%d of %d loan crawled" % (len(loans), len(items)))

        self.invest_loans = loans


    def crawl_funding_details(self, detail_link):
        detail_soup = BeautifulSoup(urlopen(detail_link).read(), 'lxml')
        divs = detail_soup.find_all('div', class_='col-xs-11 anchor-link')
        company = divs[0].get_text().strip()
        borrower = divs[1].get_text().replace(' - principal', '').strip()
        black_boxes = detail_soup.find_all('div', class_='black-box')
        rate = float(black_boxes[0].get_text().replace('%', '')) / 100
        term = int(black_boxes[1].get_text().split()[0])
        loan_to_value = float(black_boxes[2].get_text().replace('%', '')) / 100
        remaining = black_boxes[3].get_text().split('/')
        remaining_amount = parse_currency(remaining[0])
        remaining_days = int(remaining[1].split()[0])
        investers = int(black_boxes[4].get_text())
        
        white_boxes = detail_soup.find_all('div', class_='white-box')
        purpose = white_boxes[0].get_text().strip()
        position = white_boxes[1].get_text()
        total_amount = parse_currency(white_boxes[2].get_text())
        
        address = detail_soup.find(id = 'cucumber-investment').find('a').get_text()
        address_array = address.split()
        if len(address_array) > 2:
            zipcode = int(address_array[-1])
            state = address_array[-2]
        else:
            zipcode = 'NA'
            state = address_array[-1]


        date_of_formation = parse_date(detail_soup.find('div', class_='col-xs-4 date-of-formation').get_text().strip().split('\n')[-1])
        for div in detail_soup.find_all('div', class_='col-xs-6'):
            if div.find(text=re.compile('Completed Projects Per Year')):
                complete_all = int(div.find_all('div')[-1].get_text().strip())
            elif div.find(text=re.compile('Completed Projects')):
                num_complete = int(div.find_all('div')[-1].get_text().strip())
            elif div.find(text=re.compile('On Time')):
                repayment = div.find_all('div')[-1].get_text().strip()

        return {'company' : company, 
                'borrower' : borrower, 
                'rate' : rate,
                'term' : term,
                'loan_to_value' : loan_to_value,
                'remaining_amount' : remaining_amount, 
                'remaining_days' : remaining_days,
                'purpose' : purpose,
                'position' : position, 
                'investers' : investers,
                'total_amount' : total_amount,
                'zipcode' : zipcode,
                'state' : state,
                'num_complete' : num_complete,
                'complete_all' : complete_all,
                'repayment' : repayment
                }
 

    def crawl(self):
        cards = self.soup.find_all("div", class_="card")

        loans = []
        count_err = 0
        print("Crawling loans")
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
        detail_soup = BeautifulSoup(urlopen(detail_link).read(), 'lxml')
        divs = detail_soup.find_all('div', class_='col-xs-11 anchor-link')
        company = divs[0].get_text().strip()
        borrower = divs[1].get_text().replace(' - principal', '').strip()
        black_boxes = detail_soup.find_all('div', class_='black-box')
        rate = float(black_boxes[0].get_text().replace('%', '')) / 100
        term = int(black_boxes[1].get_text().split()[0])
        loan_to_value = float(black_boxes[2].get_text().replace('%', '')) / 100
        amount = parse_currency(black_boxes[3].get_text())
        investers = int(black_boxes[4].get_text())
        
        white_boxes = detail_soup.find_all('div', class_='white-box')
        purpose = white_boxes[0].get_text().strip()
        position = white_boxes[1].get_text()
        total_amount = parse_currency(white_boxes[2].get_text())

        try:
            value_boxes = detail_soup.find_all('div', class_='value-in-box col-xs-7')
            start_on = parse_date(value_boxes[0].get_text())
            funded_on = parse_date(value_boxes[1].get_text())
            repaid_on = parse_date(value_boxes[2].get_text())
            matures_on = parse_date(value_boxes[3].get_text())
            parse_result = True
        except IndexError:
            print('dates for %s unavailable' % (detail_link))
            return {'parse_result' : False}
 
        status_info = white_boxes[3].get_text().strip().split()
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
                'purpose' : purpose,
                'position' : position, 
                'investers' : investers,
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


    def supply_info(self):
        for loan in self.invest_loans:
            borrower_past = self.data[self.data.borrower == loan['borrower']]
            loan_borrower_past = {'Funded':0, 'Repaid':0, 'Late':0}
            loan_borrower_past.update(borrower_past.groupby(['status']).size().to_dict())
            loan['borrower(f:r:l)'] = "%2d :%2d :%2d" % (loan_borrower_past['Funded'], loan_borrower_past['Repaid'], loan_borrower_past['Late'])


            location_past = self.data[self.data.state == loan['state']]
            loan_location_past = {'Funded':0, 'Repaid':0, 'Late':0}
            loan_location_past.update(location_past.groupby(['status']).size().to_dict())
            loan['location(f:r:l)'] = "%2d :%2d :%2d" % (loan_location_past['Funded'], loan_location_past['Repaid'], loan_location_past['Late'])

        invest_data = pd.DataFrame(self.invest_loans)

        pd.set_option('display.max_columns', 10)
        pd.set_option('display.width', 140)
        print(invest_data[['title', 'borrower', 'state', 'borrower(f:r:l)', 'location(f:r:l)', 'num_complete', 'complete_all', 'repayment']])

        invest_data.to_csv('invest.csv')
