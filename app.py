import csv
from flask import Flask
from flask import abort
from flask import render_template
app = Flask(__name__)

# this loads our csv file
def get_csv():
	csv_path = 'csv/standings.csv'
	csv_file = open(csv_path, 'r') # typo rb
	csv_obj = csv.DictReader(csv_file)
	csv_list = list(csv_obj)
	return csv_list


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
    return render_template(template, timestamp=timestamp)

@app.route("/cubs.html")
def cubs():
    template = 'cubs.html'
    timestamp=get_big_timestamp()
    return render_template(template, timestamp=timestamp)

@app.route("/h2h.html")
def h2h():
    template = 'h2h.html'
    timestamp=get_big_timestamp()
    return render_template(template, timestamp=timestamp)

# necessary to establish the app
if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)

