from flask import Flask, render_template, request
import sybpydb

app = Flask(__name__)

# Configuration for Sybase connection
app.config['SYBASE_SERVER'] = 'your_sybase_server'
app.config['SYBASE_USER'] = 'your_username'
app.config['SYBASE_PASSWORD'] = 'your_password'

# Helper function to connect to Sybase
def connect_to_sybase():
    conn = sybpydb.connect(
        server=app.config['SYBASE_SERVER'],
        user=app.config['SYBASE_USER'],
        password=app.config['SYBASE_PASSWORD']
    )
    return conn

# Route to render the main UI
@app.route('/')
def index():
    # Fetch server CPU, memory (implement these functions)
    server_info = {
        'cpu_usage': get_cpu_usage(),
        'memory_usage': get_memory_usage()
    }
    return render_template('index.html', server_info=server_info)

# Route to fetch and display database info
@app.route('/database_info', methods=['POST'])
def database_info():
    selected_server = request.form['server']
    selected_database = request.form['database']
    
    # Connect to Sybase
    conn = connect_to_sybase()
    cursor = conn.cursor()

    # Execute stored procedures
    cursor.execute(f"use {selected_database}")
    
    cursor.callproc("sp_tables_count")
    table_count = cursor.fetchone()[0]

    cursor.callproc("sp_views_count")
    view_count = cursor.fetchone()[0]

    cursor.callproc("sp_procedures_count")
    procedure_count = cursor.fetchone()[0]
    
    conn.close()

    return render_template('database_info.html', 
                           table_count=table_count, 
                           view_count=view_count, 
                           procedure_count=procedure_count,
                           database=selected_database)

if __name__ == '__main__':
    app.run(debug=True)







# blocking chnages 

from flask import Flask, render_template, request, jsonify
import sybpydb
import random

app = Flask(__name__)

# Configuration for Sybase connection
app.config['SYBASE_SERVER'] = 'your_sybase_server'
app.config['SYBASE_USER'] = 'your_username'
app.config['SYBASE_PASSWORD'] = 'your_password'

# Helper function to connect to Sybase
def connect_to_sybase():
    conn = sybpydb.connect(
        server=app.config['SYBASE_SERVER'],
        user=app.config['SYBASE_USER'],
        password=app.config['SYBASE_PASSWORD']
    )
    return conn

# Dummy functions for CPU and memory usage
# Replace these with actual implementations
def get_cpu_usage():
    return random.randint(0, 100)

def get_memory_usage():
    return random.randint(0, 100)

# Route to render the main UI
@app.route('/')
def index():
    server_info = {
        'cpu_usage': get_cpu_usage(),
        'memory_usage': get_memory_usage()
    }
    return render_template('index.html', server_info=server_info)

# Route to fetch and display database info
@app.route('/database_info', methods=['POST'])
def database_info():
    selected_server = request.form['server']
    selected_database = request.form['database']
    
    conn = connect_to_sybase()
    cursor = conn.cursor()

    cursor.execute(f"use {selected_database}")
    
    cursor.callproc("sp_tables_count")
    table_count = cursor.fetchone()[0]

    cursor.callproc("sp_views_count")
    view_count = cursor.fetchone()[0]

    cursor.callproc("sp_procedures_count")
    procedure_count = cursor.fetchone()[0]
    
    conn.close()

    return render_template('database_info.html', 
                           table_count=table_count, 
                           view_count=view_count, 
                           procedure_count=procedure_count,
                           database=selected_database)

# Route to check for blocking processes
@app.route('/check_blocking', methods=['POST'])
def check_blocking():
    conn = connect_to_sybase()
    cursor = conn.cursor()

    cursor.execute("SELECT spid, blocked FROM sysprocesses WHERE blocked > 0")
    blocking_processes = cursor.fetchall()
    
    conn.close()

    if blocking_processes:
        return jsonify(blocking_processes=blocking_processes)
    else:
        return jsonify(message="No blocking found on server.")

if __name__ == '__main__':
    app.run(debug=True)



