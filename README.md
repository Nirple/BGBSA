# BGBSA

Board Game BSA

## Features

### Authentication

Normal authentication used. Easily extendable to use any social auth integration.

### Email

Email is used for password reset. Using smtp2go which has a free tier.


## Contributing

Uses Python 3.11+

Create your virtual environment and activate it
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install requirements with
```bash
pip install -r requirements.txt 
```


### environment variables

Uses environs. Copy the .env_template file to .env and set up the values.
