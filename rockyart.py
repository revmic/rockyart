from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title='Home')

@app.route('/blog')
def blog():
    return render_template("blog.html", title='Blog')

@app.route('/gallery')
def gallery():
    return render_template("gallery.html", title='About')

@app.route('/contact')
def contact():
    return render_template("contact.html", title='Contact')


if __name__ == '__main__':
    app.run()
