# Splitwise

# Local development
* Make sure `docker` & `docker-compose` are installed.
* Create `.env` file using `.env.example` file.
* Run the command `./run update`, to run build and run the server in background
* Run the command `./run migrate`, to run db migrations.

# Adding Migrations

* Create migrations:  `./run makemigrations`

# Check Logs
* `./run logs --tail=100 -f`


# Running pre-commit hooks
1. To install pre-commit run `brew install pre-commit` on your mac terminal. (https://pre-commit.com/#install)
2. To run pre-commit automatically on running git commit run `pre-commit install` on your mac terminal.
3. To run specific hook like flake8 run `pre-commit run --hook-stage manual flake8`. (flake8 is not automatically run)
