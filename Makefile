all:
	pip install -r requirements.txt
	./manage.py migrate

run:
	./manage.py runserver