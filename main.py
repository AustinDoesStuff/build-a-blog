#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.ext import db

templateDir = os.path.join(os.path.dirname(__file__), 'templates')
jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(templateDir), autoescape = True)

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def getBlogPosts(otherQuery):
    blog = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created DESC ' + otherQuery)
    return blog

class Helper(webapp2.RequestHandler):
    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def renderStr(self, template, **params):
        t = jinjaEnv.get_template(template)
        return t.render(**params)

    def render(self, template, **kw):
        self.write(self.renderStr(template, **kw))

class Frontpage(Helper):
    def get(self):
        blogs = getBlogPosts('LIMIT 5')
        self.render('front.html', BlogPost = blogs)

class Blogs(Helper):
    def get(self):
        blogs = getBlogPosts('')
        self.render('blogs.html', BlogPost = blogs)

class AddBlog(Helper):
    def get(self):
        #Make a form that allows someone to add a blog
        self.render('blogpost.html',title='',body='', error = '')

    def post(self):
        title = self.request.get('title')
        body = self.request.get('body')

        if title and body:
            newPost = BlogPost(title = title, body = body)
            newPost.put()
            self.redirect('/')

        else:
            self.render('blogpost.html',body=body, title=title, error = 'Try putting more words in places')

class BlogDetail(Helper):
    def get(self, blogId):
        blog = BlogPost.get_by_id(int(blogId))
        if not blog:
            self.renderError(404)
        else:
            self.render('newpost.html', blog = blog)

        # self.render('newpost.html')

app = webapp2.WSGIApplication([
    ('/', Frontpage),
    ('/blogs', Blogs),
    ('/add', AddBlog),
    webapp2.Route(r'/blogs/<blogId:\d+>', BlogDetail)
], debug=True)
