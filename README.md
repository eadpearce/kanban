# kanban

## Tools used

* [Gov uk design system](https://design-system.service.gov.uk/)
* [Django](https://www.djangoproject.com/)
* [Django CKEditor](https://django-ckeditor.readthedocs.io/en/latest/#) (version of ckeditor is now outdated unfortunately)

## Installation

### Requirements

* [Python](https://www.python.org/) 3.12
* [PipEnv](https://pipenv.pypa.io/en/latest/)

### Setup and run

To install python packages:

```
$ pipenv install
```

Run migrations:

```
$ pipenv run ./manage.py migrate
```

Then run the development server:

```
$ pipenv run ./manage.py runserver
```