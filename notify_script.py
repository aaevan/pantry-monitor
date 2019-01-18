import ast
from datetime import datetime
import os
from notify_run import Notify

log_filename = 'staple_log.txt'

notify = Notify()

staple_labels = ('black beans', 'brown rice', 'flour', 'kosher salt', 'MSG')

#given in g/day amounts. Weekly amounts are divided by 7.
usage_rates = {'black beans':900/7, #2 lb/week
               'brown rice':(680 * 3)/7, #3 cups/week
               'flour':10/7,
               'kosher salt':10/7, 
               'MSG':4/7,}

#given in grams
tare_values = {'black beans':708, #1lb 9 oz for 1/2 gallon mason jar minus lid
               'brown rice':708, #half gallong mason jar
               'flour':708, #half gallong mason jar
               'kosher salt':530, #quart mason jar
               'MSG':200,}#glass pb jar

def parse_log(filename=log_filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as file:
        content = file.readlines()
    parsed_content = []
    for line in content:
        parsed_line = ast.literal_eval(line.strip())
        parsed_content.append(parsed_line)
    return parsed_content

def days_of_stock_remaining(grams_per_day=1600, current_stock=4000, tare_weight=708):
    days_remain = round((current_stock - tare_weight) / grams_per_day, 1)
    return  days_remain

#TODO: parse our %c formatted datetime and see a rate of change?
def diff_time_between_lines(line_a=None, line_b=None, fmt='%c'):
    time_a = line_a['date']
    time_b = line_b['date']
    time_diff = datetime.strptime(time_a, fmt) - datetime.strptime(time_b, fmt)
    return time_diff

def generate_report_text(input_line=None):
    if input_line is None:
        return "No input given!"
    stocks = {}
    for key in input_line:
        print('key is: {}'.format(key))
        if key == 'date':
            continue
        grams_per_day = usage_rates[key]
        current_stock = input_line[key]
        tare_weight = tare_values[key]
        stocks[key] = days_of_stock_remaining(grams_per_day=grams_per_day,
                                              current_stock=current_stock,
                                              tare_weight=tare_weight)
        #print(''.join(["{}: {} days\n".format(key, asdf[key]) for key in asdf]))
        
    print(stocks)
    return stocks

def notify_routine():
    parsed_log = parse_log(log_filename)
    notification_text = generate_report_text(input_line=parsed_log[-1])
    notify.send(notification_text)

def main():
    notify_routine()

if __name__ == '__main__':
    main()
