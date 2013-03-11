from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from models import Student, Choice
from dnd_ldap import lookup

students = Blueprint ('students', __name__, template_folder='templates')

class ListView(MethodView):
	def get(self):
		students = Student.objects.all()
		return render_template('students/list.html',students=students)

class DetailView(MethodView):
	form = model_form(Choice, exclude=['created-at','email'])

	def get_context(self, slug):
		print slug
		print 'through'
		student = Student.objects.get_or_404(slug=slug)
		print student.name
		form = self.form(request.form)

		context = {
			"student": student,
			"form": form
		}
		return context

	def get(self,slug):
		context = self.get_context(slug)
		return render_template('students/detail.html', **context)

	def post(self, slug):
		context = self.get_context(slug)
		print 'over here dude'

		form = context.get('form')

		print 'entering form'
		if form.validate():
			choice_new = Choice()
			form.populate_obj(Choice)
			print 'populated'
			lookup(choice_new.name)
			student = context.get('student')
			student.choices.append(choice_new)
			print student.choices
			student.save()
			print 'saving student'
			return redirect(url_for('students.detail', slug=slug))

		return render_template('students/detail.html',**context)

students.add_url_rule('/',view_func=ListView.as_view('list'))
students.add_url_rule('/<slug>/',view_func=DetailView.as_view('detail'))
