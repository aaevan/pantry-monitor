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
def seconds_between_lines(line_dict_a=None, line_dict_b=None, fmt='%c'):
    time_a = datetime.strptime(line_dict_a['date'], fmt)
    time_b = datetime.strptime(line_dict_b['date'], fmt)
    time_diff = (time_b - time_a).total_seconds()
    return time_diff

def usage_between_lines(line_a=None, line_b=None):
    """
    determines the amount of stock used between each
    """
    if line_a is None or line_b is None:
        return False
    staple_diffs = {}
    for staple in sorted(line_a):
        if staple == 'date':
            continue
        staple_usage = line_b[staple] - line_a[staple]
        staple_diffs[staple] = staple_usage
    return staple_diffs

#full report:
#At your current average rate of <USAGE_RATE>g per day, <NUM_DAYS> days of <STAPLE> remain.

#I want a report to be sent AFTER each time I update any particular stock 
#AND I want another report to be sent once a day at noon.

def filtered_within_n_days(parsed_log=None, days=14):
    _seconds_in_day = 60 * 60 * 24
    within_interval = days * _seconds_in_day
    current_time = datetime.now()
    relevant_lines = []
    for line in parsed_log:
        seconds_since_logged = seconds_between_lines(line_dict_a=line, line_dict_b=current_time) 
        if seconds_sinced_logged < seconds_in_interval:
            relevant_lines.append(line)
    return relevant_lines

def tally_usage_within_interval(parsed_log=None, within_n_days=14):
    #scan through log, discard invalid lines:
    relevant_lines = filtered_within_n_days(parsed_log=parsed_log, days=within_n_days)
    line_index_pairs = [(i, i + 1) for i in range(len(relevant_lines) - 1)]
    usage_vals = []
    for index_pair in line_index_pairs:
        line_a = relevant_lines[index_pair[0]]
        line_b = relevant_lines[index_pair[1]]
        staple_use = usage_between_lines(line_a=line_a, line_b=line_b)
        usage_vals.append(staple_use)
    totals = {key:0 for key in relevant_lines[0] if key != 'date'}
    for line in usage_vals:
        for key in line:
            totals[key] += line[key]
    return totals

def generate_report_text(parsed_log=None):
    if parsed_log is None:
        return "No input given!"
    #stocks = {}
    #for key in input_line:
    #   print('key is: {}'.format(key))
    #   if key == 'date':
    #       continue
    #   grams_per_day = usage_rates[key]
    #   current_stock = input_line[key]
    #   tare_weight = tare_values[key]
        #stocks[key] = days_of_stock_remaining(grams_per_day=grams_per_day,
                                              #current_stock=current_stock,
                                              #tare_weight=tare_weight)
        #print(''.join(["{}: {} days\n".format(key, asdf[key]) for key in asdf]))
    stocks = tally_usage_within_interval(parsed_log=parsed_log)
        
    print(stocks)
    return stocks

def notify_routine():
    parsed_log = parse_log(log_filename)
    notification_text = generate_report_text(parsed_log=parsed_log)
    notify.send(notification_text)

def main():
    notify_routine()

if __name__ == '__main__':
    main()
