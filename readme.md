## INSTALLATION

```bash
$ pip install -r requirements.txt
```

## HOW TO RUN

```bash
$ python test.py
```

### Params:

- url: str - URL to crawl
- is_new_sitemap: True | False - Whether is new sitemap or not
- is_all_page: True | False - Whether is all pages or single page

### Edit parameters to settings

```python 
  url = "https://quotes.toscrape.com/" 
  is_new_sitemap = True 
  is_all_page = True
```


See the ./sitemap_generator/settings.py for setting crawler settings