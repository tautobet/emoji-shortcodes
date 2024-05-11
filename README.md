# Streamlit app

Introduce streamlit app

## Install Python, Poetry
  
1. Install Python 3.10.11 or above
```
pyenv install 3.10.11
echo "3.10.11" >> .python-version
```
 
2. Install Poetry
```
pip install poetry
```

3. Configure project
`copy .env-template .env`
then install dependencies
`poetry install`

## Testing
```
poetry shell
python -m pytest
```



## Run

1. Run API server
```
 poetry shell
 python -m babel.app
```

2. Run Streamlit app (stapp.py)
```
poetry shell
python -m streamlit run horus/streamlit_app.py
```
   

