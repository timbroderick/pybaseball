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

# create pages here

@app.route("/")
def index():
    template = 'index.html'
    object_list = get_csv()
    return render_template(template, object_list=object_list)

# necessary to establish the app
if __name__ == '__main__':
    # Fire up the Flask test server
    app.run(debug=True, use_reloader=True)

