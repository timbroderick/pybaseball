import csv
from flask import Flask
from flask import abort
from flask import render_template
app = Flask(__name__)

# this loads csv for index file
def get_csv():
	csv_path = 'csv/standings.csv'
	csv_file = open(csv_path, 'r') # typo rb
	csv_obj = csv.DictReader(csv_file)
	csv_list = list(csv_obj)
	return csv_list

# this loads csv for Sox next last file
def soxagg():
    soxagg_path = 'csv/soxagg.csv'
    soxagg_file = open(soxagg_path, 'r') # typo rb
    soxagg_obj = csv.DictReader(soxagg_file)
    soxagg_list = list(soxagg_obj)
    return soxagg_list

# this loads csv for Sox game aggregate file
def soxnl():
    soxnextlast_path = 'csv/soxnextlast.csv'
    soxnextlast_file = open(soxnextlast_path, 'r') # typo rb
    soxnextlast_obj = csv.DictReader(soxnextlast_file)
    soxnextlast_list = list(soxnextlast_obj)
    return soxnextlast_list

# this loads csv for Sox pitch aggregate file
def soxpitch():
    soxpitch_path = 'csv/soxpitch.csv'
    soxpitch_file = open(soxpitch_path, 'r') # typo rb
    soxpitch_obj = csv.DictReader(soxpitch_file)
    soxpitch_list = list(soxpitch_obj)
    return soxpitch_list

# this loads csv for Sox hit aggregate file
def soxhit():
    soxhit_path = 'csv/soxhit.csv'
    soxhit_file = open(soxhit_path, 'r') # typo rb
    soxhit_obj = csv.DictReader(soxhit_file)
    soxhit_list = list(soxhit_obj)
    return soxhit_list

# this loads csv for cubs next last file
def cubsagg():
    cubsagg_path = 'csv/cubsagg.csv'
    cubsagg_file = open(cubsagg_path, 'r') # typo rb
    cubsagg_obj = csv.DictReader(cubsagg_file)
    cubsagg_list = list(cubsagg_obj)
    return cubsagg_list

# this loads csv for cubs game aggregate file
def cubsnl():
    cubsnextlast_path = 'csv/cubsnextlast.csv'
    cubsnextlast_file = open(cubsnextlast_path, 'r') # typo rb
    cubsnextlast_obj = csv.DictReader(cubsnextlast_file)
    cubsnextlast_list = list(cubsnextlast_obj)
    return cubsnextlast_list

# this loads csv for cubs game aggregate file
def cubshit():
    cubshit_path = 'csv/cubshit.csv'
    cubshit_file = open(cubshit_path, 'r') # typo rb
    cubshit_obj = csv.DictReader(cubshit_file)
    cubshit_list = list(cubshit_obj)
    return cubshit_list

# this loads csv for Cubs pitch aggregate file
def cubspitch():
    cubspitch_path = 'csv/cubspitch.csv'
    cubspitch_file = open(cubspitch_path, 'r') # typo rb
    cubspitch_obj = csv.DictReader(cubspitch_file)
    cubspitch_list = list(cubspitch_obj)
    return cubspitch_list

# trying mike stucka's date
def get_big_timestamp(date_object=None):
    import datetime
    if not date_object:
        date_object = datetime.datetime.now()
    stamp = ""
    # comment out below if you don't want "Wednesday" or similar in your string
    stamp += datetime.datetime.strftime(date_object, "%A, ")
    if date_object.month == 9:
        stamp += "Sept. " +  datetime.datetime.strftime(date_object, "%d, %Y").lstrip("0")
    elif date_object.month < 3 or date_object.month > 7:
        stamp += datetime.datetime.strftime(date_object, "%b. ") + datetime.datetime.strftime(date_object, "%d").lstrip("0")
    else:
        stamp += datetime.datetime.strftime(date_object, "%B ") + datetime.datetime.strftime(date_object, "%d").lstrip("0")
    # uncomment out below if you want the year
    # stamp += datetime.datetime.strftime(date_object, ", %Y")
    stamp += ", at "
    stamp += datetime.datetime.strftime(date_object, "%I:%M %p").lstrip("0").replace("AM", "a.m.").replace("PM", "p.m.")
    return(stamp)

# create pages here

@app.route("/")
@app.route("/index.html")
def index():
    template = 'index.html'
    timestamp=get_big_timestamp()
    object_list = get_csv()
    return render_template(template, timestamp=timestamp, object_list=object_list)

@app.route("/sox.html")
def sox():
    template = 'sox.html'
    timestamp=get_big_timestamp()
    soxagg_list = soxagg()
    soxnl_list = soxnl()
    soxhit_list = soxhit()
    soxpitch_list = soxpitch()
    return render_template(template, timestamp=timestamp, agg=soxagg_list, nl=soxnl_list, hit=soxhit_list, pitch=soxpitch_list)
	# For end of season, doesn't include the next/last file
	#return render_template(template, timestamp=timestamp, agg=soxagg_list, hit=soxhit_list, pitch=soxpitch_list)

@app.route("/cubs.html")
def cubs():
    template = 'cubs.html'
    timestamp=get_big_timestamp()
    cubsagg_list = cubsagg()
    cubsnl_list = cubsnl()
    cubshit_list = cubshit()
    cubspitch_list = cubspitch()
    return render_template(template, timestamp=timestamp, agg=cubsagg_list, nl=cubsnl_list, hit=cubshit_list, pitch=cubspitch_list)
	# For end of season, doesn't include the next/last file
    #return render_template(template, timestamp=timestamp, agg=cubsagg_list, hit=cubshit_list, pitch=cubspitch_list)

@app.route("/h2h.html")
def h2h():
    template = 'h2h.html'
    timestamp=get_big_timestamp()
    return render_template(template, timestamp=timestamp)

# necessary to establish the app
if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)
