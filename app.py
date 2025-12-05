from flask import Flask, render_template
from data_loader import DataLoader

app = Flask(__name__)
loader = DataLoader()

# --- IMPORTANT: LOAD DATA ON STARTUP ---
print("Initializing Data Loader...")
loader.load_data()
print("Data Ready.")

@app.route('/')
def dashboard():
    # Check status
    db_status = loader.check_files()
    
    # Get Visuals (Now using the correct function name)
    graphs = loader.get_visuals()
    
    return render_template('dashboard.html', 
                           status=db_status, 
                           graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True)