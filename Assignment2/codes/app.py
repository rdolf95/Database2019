from flask import Flask, render_template, request, redirect
from pypg import helper
import json


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("glasses_test.html")


if __name__ == ("__main__"):
  #  main()
  # docker
  #app.run(debug=True, host='0.0.0.0', port=5090)
  # other
  app.run(debug=True)
