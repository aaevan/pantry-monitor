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
    determines the amount of stock used between each line of the log
    """
    if line_a is None or line_b is None:
        return False
    staple_diffs = {}
    for staple in sorted(line_a):
        if staple == 'date':
            continue
        staple_usage = line_b[staple] - line_a[staple]
        #account for stock being added to the container:
        if staple_usage <= 0:
            staple_usage = 0
        staple_diffs[staple] = staple_usage
    return staple_diffs

def filtered_within_n_days(parsed_log=None, days=14):
    _seconds_in_day = 60 * 60 * 24
    seconds_within_interval = days * _seconds_in_day
    current_time = {'date':datetime.now().strftime('%c')}
    relevant_lines = []
    for line in parsed_log:
        seconds_since_logged = seconds_between_lines(line_dict_a=line, line_dict_b=current_time) 
        if seconds_since_logged < seconds_within_interval:
            relevant_lines.append(line)
    return relevant_lines

def tally_usage_within_interval(parsed_log=None, within_n_days=14):
    #scan through log, discard invalid lines:
    relevant_lines = filtered_within_n_days(parsed_log=parsed_log, days=within_n_days)
    # a list of adjacent pairs of lines, (i.e.: 0,1, 1,2, 2,3, 3,4) 
    # check changes between these pairs:
    line_index_pairs = [(i, i + 1) for i in range(len(relevant_lines) - 1)]
    usage_vals = []
    for index_pair in line_index_pairs:
        line_a = relevant_lines[index_pair[0]]
        line_b = relevant_lines[index_pair[1]]
        staple_use = usage_between_lines(line_a=line_a, line_b=line_b)
        usage_vals.append(staple_use)
    # a zeroed out list of our possible staples:
    totals = {key:0 for key in relevant_lines[0] if key != 'date'}
    for line in usage_vals:
        for key in line:
            totals[key] += line[key]
    return totals

def legible_usage_stats(usage_dict=None, unit='g', title='2 week usage'):
    if usage_dict is None:
        return False
    output_string = ""
    for key in sorted(usage_dict):
        if key == sorted(usage_dict)[0]:
            pass
        elif key == sorted(usage_dict)[-1]:
            output_string += ' and '
        else:
            output_string += ', '
        output_string += '{}{} of {}'.format(round(usage_dict[key]), unit, key)
    output_string += '.'
    output_text = "{}: {}".format(title, output_string)
    print(output_text)
    return output_text

def compare_stock_with_usage(usage_dict=None, stock_dict=None):
    if usage_dict is None or stock_dict is None:
        return False
    use_rates = {key:round(stock_dict[key] / (usage_dict[key] / 14)) for key in usage_dict}
    output_text = legible_usage_stats(usage_dict=use_rates, unit=' days', title='Days of stock remaining')
    return output_text

def notify_routine(log_filename=log_filename):
    parsed_log = parse_log(log_filename)
    current_stock = dict([pair for pair in parsed_log[-1].items() if pair[0] != 'date'])
    #tally usage within lines of date 2 weeks or newer:
    staples_dict = tally_usage_within_interval(parsed_log=parsed_log)
    #filter out the key/value pairs that are zero.
    used_staples = dict([pair for pair in staples_dict.items() if pair[1] != 0])
    #legible_usage_state takes a cleaned list of nonzero values
    notify.send(legible_usage_stats(usage_dict=used_staples))
    notify.send(compare_stock_with_usage(usage_dict=staples_dict, stock_dict=current_stock))

def main():
    notify_routine()

if __name__ == '__main__':
    main()
