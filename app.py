from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/queryItem', methods=['POST'])
def query_item():
    given_item = request.args.get('value1')
    print(given_item)
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
