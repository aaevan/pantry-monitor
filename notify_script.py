import ast
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
    return (measured_weight - tare_weight) / grams_per_day

def generate_report_text(input_line=None):
    if input_line is None:
        return "No input given!"

#TODO: parse our %c formatted datetime and see a rate of change?

parsed_log = parse_log(log_filename)
notification_text = "the last line in the log: {}".format(parsed_log[-1])

notify.send(notification_text)

#the script itself will be scheduled as a cron job

#every day at noon
#duplicate the most recent pantry value


