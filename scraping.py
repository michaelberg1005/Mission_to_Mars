
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path)

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_p = mars_news(browser)

   # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_p,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "hemispheres": hemispheres_enhanced(browser),
      "last_modified": dt.datetime.now()
    }

    browser.quit()

    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
   
    return news_title, news_p

    
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None


    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url
    

def mars_facts():
    try:
        # use read_html to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    #assign colums and set index of DF
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)
    
    #CONVERT INTO html FORMAT, ADD BOOTSTRAP
    return df.to_html()


def hemispheres_enhanced(browser):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url) 

    #initiaite parser
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    #find the 4 descriptions that are for each hemisphere (change to find_all and then do for loop)
    try:
        hemispheres = soup.find("div",class_="description")
    except AttributeError:
        return None
    
    #initiate empty list of dictionary of hemispheres urls and titles
    hemi_urls_titles =[]

    #where a loop would start - get the relative href to set up click for each hemisphere
    for hemisphere in hemispheres:
        try:
            hemi_href = hemisphere.find("a", href=True).get("href")
        except AttributeError:
            return None

        #set up going to a new url where enhanced image is (replaced by the relative location)
        enhanced_url = f'https://astrogeology.usgs.gov{hemi_href}'
        
        #go to enhanced image url
        browser.visit(enhanced_url)
        
        #relative url part 2 - for getting src
        html2 = browser.html
        soup2 = BeautifulSoup (html2,"html.parser")
        
        #get title
        try:
            hemi_title = soup2.find("h2", class_="title").get_text()
        except AttributeError:
            return None
        
        #get relative path for img url
        try:
            hemi_img = soup2.find("img", class_="wide-image").get("src")
        except AttributeError:
            return None
        
        #img url linl
        img_url = f'https://astrogeology.usgs.gov{hemi_img}'
        
        #update dictionary with title and url as key value pair
        hemi_urls_titles.append({"title":hemi_title,"img":img_url})

    return hemi_urls_titles

browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
