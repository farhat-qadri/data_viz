from flask import Flask, render_template
from data_loader import DataLoader

app = Flask(__name__)
loader = DataLoader()

@app.route('/')
def dashboard():
    # Check if files exist (just for status indicator)
    db_status = loader.check_files()
    
    # Get the placeholder graphs (so the JS doesn't crash)
    graphs = loader.get_placeholders()
    
    return render_template('dashboard.html', 
                           status=db_status, 
                           graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True)