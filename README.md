# instagram-scraper

Allows users to search Instagram's posts using hashtags.

## Anaconda Setup

1. Create the environment

```
conda create --name instagram_scraper python=3.11
conda activate instagram_scraper
```

2. Install packages

```
conda install requests
conda install beautifulsoup4
conda install pymongo
conda install selenium=4.9.0
```

## Run the tool

```
cd instagram-scraper
python instagram_srcaper.py
```

You will be prompted to enter the [keyword] in the terminal, this is the hashtag to be searched. Please note that the '#' symbol is not needed.


## Using Jupyter Notebook

```
conda install -c anaconda jupyter
jupyter notebook
```


## Credits

This project based on [Scrapstagram](https://github.com/xTEddie/Scrapstagram.gi). 
