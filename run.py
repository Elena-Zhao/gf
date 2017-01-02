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
        funded = gf.GoundFloor('https://www.groundfloor.us/education/funded')
        funded_df = funded.crawl()
        today = dt.datetime.today().strftime('%Y%m%d')
        funded_df.to_csv('data/funded_' + today + '.csv')
    elif args.action == 'invest':
        funded = gf.GoundFloor('https://www.groundfloor.us/investments')


if __name__ == '__main__':
    run()
