from bs4 import BeautifulSoup
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import pandas as pd

BASE_URL = 'https://www.groundfloor.us' 

class GoundFloor():
    def __init__(self, link):
        self.soup = BeautifulSoup(urlopen(link).read(), "lxml")
    
    def crawl(self):
        cards = self.soup.find_all("div", class_="card")

        loans = []
        count = 0
        for card in cards:
            count += 1
            loan = {}
            loan['name'] = card.find('div', class_="title").get_text()
            loan['type'] = card.find('div', class_='inner-arrow').get_text().strip()
            loan['grade'] = card.find('div', class_="triangle").get_text()

            numbers = card.find_all('div', class_ = 'number')
            loan['rate'] = numbers[0].get_text()
            loan['projected_term'] = numbers[1].get_text()
            loan['loan_to_value'] = numbers[1].get_text()

            loan['details'] = card.find('div', class_='large-link').find('a').attrs['href']
            
            detail_link = BASE_URL + loan['details']
            details = self.crawl_details(detail_link)
            loan.update(details)
            loans.append(loan)
            if count % 10 == 0:
                print("%d of %d loan crawled" % (count, len(cards)))
        
        print("%d of %d loan crawled in total" % (count, len(cards)))
        
        return pd.DataFrame(loans)
    
    def crawl_details(self, detail_link):
        detail_soup = BeautifulSoup(urlopen(detail_link).read(), "lxml")
        
        company = detail_soup.find_all('div', class_='col-xs-11 anchor-link')[0].get_text().strip()
        borrower = detail_soup.find_all('div', class_='col-xs-11 anchor-link')[1].get_text().strip()
        
        loan_amount = detail_soup.find_all('div', class_='black-box')[3].get_text()
        investers = detail_soup.find_all('div', class_='black-box')[4].get_text()
        
        purpose = detail_soup.find_all('div', class_='white-box')[0].get_text().strip()
        loan_position = detail_soup.find_all('div', class_='white-box')[1].get_text()
        total_loan_amount = detail_soup.find_all('div', class_='white-box')[2].get_text()
        loan_status = detail_soup.find_all('div', class_='white-box')[3].get_text().strip()
        
        try:
            start_on = detail_soup.find_all('div', class_='value-in-box col-xs-7')[0].get_text()
            funded_on = detail_soup.find_all('div', class_='value-in-box col-xs-7')[1].get_text()
            repaid_on = detail_soup.find_all('div', class_='value-in-box col-xs-7')[2].get_text()
            matures_on = detail_soup.find_all('div', class_='value-in-box col-xs-7')[3].get_text()
        except IndexError:
            print('dates for {} unavailable:'.format(detail_link))
            start_on = -1
            funded_on = -1
            repaid_on = -1 
            matures_on = -1
            
        address = detail_soup.find(id = 'cucumber-investment').find('a').get_text()
        description = detail_soup.find(id = 'cucumber-investment').find('div', class_ = "col-xs-12").get_text().strip()
        
        return {'company' : company, 
                'borrower' : borrower, 
                'loan_amount' : loan_amount, 
                'investers' : investers, 
                'purpose' : purpose,
                'loan_position' : loan_position, 
                'investers' : investers,
                'purpose' : purpose, 
                'loan_position' : loan_position, 
                'total_loan_amount' : total_loan_amount, 
                'loan_status' : loan_status, 
                'start_on' : start_on, 
                'funded_on' : funded_on, 
                'repaid_on' : repaid_on, 
                'matures_on' : matures_on,
                'address' : address, 
                'description' : description
                }


if __name__ == "__main__":
    funded = GoundFloor('https://www.groundfloor.us/education/funded')
    funded_df = funded.crawl()
