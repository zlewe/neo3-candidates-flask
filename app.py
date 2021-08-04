#Flask imports
from flask import Flask, render_template

from util.rpc import get_table

app = Flask(__name__)

#Pandas Page
@app.route('/')
@app.route('/pandas', methods=("POST", "GET"))
def table_view():
    c_list = get_table(show_hash = True)
    return render_template('table.html',
                           PageTitle = "NEO3 Committee/Candidates List",
                           table=[c_list.to_html(classes='data', index = False)], titles= c_list.columns.values)

if __name__ == '__main__':
    app.run(debug = True)