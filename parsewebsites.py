import urllib.request
from bs4 import BeautifulSoup

# Function that will scrape a webpage of the Washington Post
def getWashPostText(url, token):
    # This function takes the url of an article in the washington post and then returns the article minus all of the crud html, javascript etc.
    # Assumption: All articles in the WashPo are enclosed in <article></article> tags
    try:
        # Downloading the webpage
        page = urllib.request.urlopen(url).read().decode('utf8')
    except:
        return (None,None)
    
    # Use BeautifulSoup to remove all the div and tags that are present
    soup = BeautifulSoup(page)
    if soup is None:
        return(None, None)
    
    # Removing the hmtl divs/tags and get on string with text
    text = ''
    # By taking a token. This is a token in which between all the text of the article is kept
    # This is specific to the structure of the webpage that is parsed
    if soup.find_all(token) is not None:
        # Finding all the text between that token and mushes it together
        text = ''.join(map(lambda p: p.text, soup.find_all(token)))
        # Second soup because the structure of the WashingtonPost page is such that the article is enclosed within article tags
        # and there are paragraphs within the article which are enclosed in p tags.
        soup2 = BeautifulSoup(text)
        if soup2.find_all('p') is not None:
            # Takes all the p-tags within that text and mushes it all together
            # text should be one string with the text of the articles without any tags like article or p
            text = ''.join(map(lambda p: p.text, soup2.find_all('p')))
    # Return the text of the article and the title of the article as a tuple
    return text, soup.title.text

# Function that will scrape the NYT
def getNYTText(url, token):
    # Alternative way to get the contents of a URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    page = str(soup)
    title = soup.find('title').text

    # In the NYT, the article is contained within the tags story-body-text class
    mydivs = soup.findAll('p', {'class':'story-body-text story-content'})
    # Find all the all the text that is between p tags and smush it together to get one string
    text = ''.join(map(lambda p: p.text, mydivs))
    return text, title

# Function that takes in the URL of an entire section of a newspapers and parses all of the URLs linked off that section
# It returns all the corresponding articles of all the URLs of that section as a dictionary
# The function will use getWashPostText() and getNYTText()
def scrapeSource(url, magicFrag = '2020', scraperFunction = getNYTText, token = 'None'):
    # The scraperFunction is a website specific function in order to scrape that specific webpage
    # magicFrag: allows us to check URLs for dates

    # Setting up a soup for the section page to find all the links that are in that section page
    urlBodies = {}
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response)

    # We will only consider URLs with a date line, i.e.
    # We need to check whether the URL contains a date
    # To do so, we will use the magicFrag argument
    numErrors = 0
    # find_all returns an object of ResultSet which offers index based access to the result of found occurrences
    for a in soup.findAll('a'):
        try:
            # Links are always of the form <a href = 'link-url'> link-text </a>
            url = a['href']
            if( (url not in urlBodies) and ((magicFrag is not None and magicFrag in url) or magicFrag is None)):
                # Employing the website specific scraper function to download the article
                body = scraperFunction(url, token)

                if body and len(body > 0 ):
                    # Each text body is saved in a dictionary with the URL as the key
                    urlBodies[url] = body
        # Except block so that we can keep track of parsing errors
        except:
            numErrors += 1
        
        # Returns are dictionary with key: url and corresponding article title and value: text
        return urlBodies
