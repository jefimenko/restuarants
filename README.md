# restuarants

A scraper for King County's Public Health website that forms a query using python's requests module.
The response is parsed using BeautifulSoup, and currently, relevant information about each business
within a range of dates is extracted and stored in a dictionary, including information about
inspection scores.

Referenced BeautifulSoup documentation extensively for the use of find_all() and attributes available
for BeautifulSoup tag objects.
http://www.crummy.com/software/BeautifulSoup/bs4/doc/
