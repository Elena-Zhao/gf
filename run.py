import argparse
import datetime as dt
import groundfloor as gf

def parse_commandline_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--action', metavar='a', type=str, default='crawl')
    return arg_parser.parse_args()


def run():
    args = parse_commandline_args()
    if args.action == 'crawl':
        gf_crawler = gf.GoundFloor('https://www.groundfloor.us/education/funded')
        gf_crawler.crawl()
        today = dt.datetime.today().strftime('%Y%m%d')
        gf_crawler.save('data/funded_' + today + '.csv')
    elif args.action == 'invest':
        gf_crawler = gf.GoundFloor('https://www.groundfloor.us/investments')
        gf_crawler.crawl_funding()
        gf_crawler.read('data/funded_20170102.csv')
        gf_crawler.supply_info()


if __name__ == '__main__':
    run()
