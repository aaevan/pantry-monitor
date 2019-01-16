from notify_run import Notify
notify = Notify()

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
               'MSG':4,}#jelly jar

def days_of_stock_remaining(grams_per_day=1600, current_stock=4000, tare_weight=708):
    return (measured_weight - tare_weight) / grams_per_day



notification_text = "

notify.send("Sent from that script you just wrote!")



#the script itself will be scheduled as a cron job

#slurp in the log file

#every day at noon
#duplicate the most recent pantry value

#okay, we're trying to figure out what the rate of change of the staples.

#give an estimate in gpio control of rate of change of each staple

#for each line in the log file, 

