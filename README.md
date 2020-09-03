# ModularHistory

https://www.modularhistory.com

![CI](https://github.com/actions/modularhistory/workflows/CI/badge.svg)

---

## Installation

### Prerequisites

OS: MacOS or Ubuntu

(ModularHistory cannot be run on Windows.)

### Clone

Clone ModularHistory to your local machine, as follows:

```shell script
git clone https://github.com/ModularHistory/modularhistory.git
```

### Setup

Enter the cloned project directory and run the setup script, as follows:

```shell script
cd modularhistory
./setup.sh
```
The setup script installs project dependencies.


---

## Contributing

To contribute to ModularHistory's development, follow the steps below.

### Join the project and find/create a card

First, join ModularHistory's PivotalTracker project:

https://www.pivotaltracker.com/projects/2460843

PivotalTracker is used for task management and planning. However, we're transitioning to a GitHub project.  All new tasks and issues should be added to the kanban board on GitHub:

https://github.com/ModularHistory/modularhistory/projects/1

If you would like to contribute regularly to ModularHistory, you can request to be added to the repository members so that you can create branches.  Otherwise, you can fork the project to make changes without joining the repo.


### Fork or branch the repo
If you've been added to the repo members, you can create a branch for your changes.

- ...
- ...
    - ...

- ...
    - ...


### Make your changes

Run the setup script before working on any code changes:

```
./setup.sh
```

Then write your code.

Make migrations.

How to reset migrations: 
https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

Before running migrations, create a db backup:
```
python manage.py dbbackup
```
### Write tests

After adding some code, check coverage to determine what needs to be tested:

```coverage run --source='.' manage.py test && coverage html```

See https://coverage.readthedocs.io/en/coverage-5.2/.

### Review your changes

Lint the code (using [flake8](https://flake8.pycqa.org/en/latest)):
```
flake8
```

---

## Support

Reach out to ModularHistory:

- By email: modularhistory@gmail.com
- On Facebook: [https://www.facebook.com/modularhistory](https://www.facebook.com/modularhistory)
- On Twitter: [https://twitter.com/ModularHistory](https://twitter.com/ModularHistory)

---

## Donations

You can support ModularHistory through [Patreon](https://www.patreon.com/modularhistory).

---

## License

ModularHistory has an [ISC License](https://github.com/ModularHistory/modularhistory/blob/master/LICENSE.txt).
