# Rightmove Scraper

A scraper for properties advertised on [rightmove.co.uk](https://rightmove.co.uk).
Results can be saved to either a SQLite database or a JSON file.

## Quickstart

### Docker

To run the scraper, use the following command:

```bash
docker run -e SEARCH_URLS='my-search-url' -v results:/out libklein/rightmove-scraper
```

The container will immediately scrape the given URLs, and then enter cron mode, scraping the URLs at 8 pm daily.

See the [Configuration](#configuration) section for more information on the available settings.

### Pypi

1. (Optional) Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install the required Python modules:

```bash
pip install -r requirements.txt
```

3. Go to [rightmove.co.uk](https://rightmove.co.uk) and configure the search filters to match the properties you're interested in.
4. Copy the URL into the `SEARCH_URLS` array in [settings.py](rightmove_scraper/settings.py). Example:
```python
SEARCH_URLS = [
    'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E87490&minBedrooms=2&maxBedrooms=2&minPrice=1000&maxPrice=1500&propertyTypes=flat&primaryDisplayPropertyType=flats&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='
]
```
5. Set up the database:
```bash
python rightmove_scraper/models.py
```
6. Run the scraper:

```bash
scrapy crawl rightmove
```

Rerunning the scraper will update the database with new properties, i.e., it will not create duplicates. Note that *all* results will be saved to the json file, not just the new ones.

## Configuration

The scraper can be configured by changing the settings in [settings.py](rightmove_scraper/settings.py). Moreover, the following settings can be passed as environment variables:
* `SEARCH_URLS`: A comma separated list of URLs to scrape.
* `DB_PATH`: The path to the SQLite database file. Default: `rightmove.db`.
* `NO_DB`: If set to `1`, the scraper will not save the results to a database. Default: `0`.
* `OUTPUT_JSON_PATH`: If set, the scraper will save the results to a JSON file with the given name. Default: `None`.
* `LOG_FILE_PATH`: The path to the log file. Default: `rightmove.log`.