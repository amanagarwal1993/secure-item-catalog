# Grocery app using Python backend (Flask)

### What the app does:
1. You can sign in securely using Google (oauth 2.0) to create items in any category of groceries (eg bread, fruits etc.)
2. You can edit and delete only items that you yourself have created.
3. You can get JSON data of grocery items and their information by adding 'json' at the end of the url.


### How to run the project
1. Please have Flask, Sqlite3 and Python 2.7 installed.
2. Clone the repo.
3. On the command line, open the project directory.
4. Run *database.py*: 
`python database.py`
5. Run this file to create initial categories of groceries: *populatedb.py*, with this: 
`python populatedb.py`
6. Run the *server.py* file: 
`python server.py`

And then open the following url in your browser: *http://localhost:5000* 

## License
(Feel free to copy, but don't be a jerk :))
[GNU General Public License](http://choosealicense.com/licenses/gpl-3.0/#)
