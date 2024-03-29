# Hangman

Simple hangman guessing game using VueJS and FastAPI.

## Installing

### User interface

The user interface can be installed using `npm`. Inside the `front` directory run:
```commandline
npm install
```
### Application server

Dependencies are defined in `pyproject.toml` and `requirements.txt`.
The application server can be installed in a virtual environment. For example using Poetry and inside the `app` directory:
```commandline
poetry install
```

## Starting

### Environment
Create a `.env` file at the root of the cloned repository. See `.env.example` for an example.
The `ALGORITHM` and `SECRET_KEY` keys are used to sign JWT tokens.
Change the value of `SECRET_KEY` to a randomly generated key using for example:
```commandline
openssl rand -hex 32
```
`ORIGINS` and `VITE_API_URL` keys define respectively the URLs where the user interface and the API are accessible.

### User interface

Start the vite development server using:
```commandline
npm run dev
```

### Application server
Activate the virtual environment where the server is installed. For example using Poetry and inside the `app` directory:
```commandline
poetry shell
```
Then start the uvicorn server (development):
```commandline
uvicorn app.main:api --reload
```

### To do
- Package python backend
- Complete dockerization of both frontend and backend
- Local Redis
- User registration on client side
- User data save on server side
- User interface improvements
- Highscore, feedback and settings pages
