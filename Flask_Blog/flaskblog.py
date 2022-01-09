#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, render_template, url_for
app = Flask(__name__)


posts = [
    {
        'author' : 'Sam Taylor',
        'title': 'Blog Post 1',
        'content': 'First Post Content',
        'date_posted' : 'January 8th, 2021'
    },
    {
        'author' : 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second Post Content',
        'date_posted' : 'January 9th, 2021'

    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

if __name__ == "__main__":
    app.run(debug = True)




# %%
