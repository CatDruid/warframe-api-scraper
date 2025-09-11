from flask import Flask, render_template, redirect, url_for, request
import Apiscraper
import json

app = Flask(__name__)

@app.route("/", methods= ['POST', 'GET'])
def index():
    if request.method == "POST":
        pass
    else:        
        return render_template('index.html')

@app.route('/fetchframes')
def fetch():
    currentBestFrame = Apiscraper.rOICheckAllFrames()
    return render_template('index.html', currentBestFrame=currentBestFrame)

if __name__ == "__main__":
    app.run(debug=True)