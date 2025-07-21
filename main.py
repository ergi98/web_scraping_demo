import bs4
import json
import requests


def scrape_book_thumbnail():
  '''
  Scrape a single image and save it locally
  '''
  book_page_url = 'http://books.toscrape.com'
  result = requests.get(book_page_url)
  soup = bs4.BeautifulSoup(result.text, 'lxml')
  image = soup.select_one('img.thumbnail')
  image_source = image.attrs.get('src')
  image_res = requests.get(f'{book_page_url}/{image_source}')
  content_type = image_res.headers.get('Content-Type')
  if content_type and content_type.startswith('image/'):
    image_type = content_type.split('/')[1]
    if image_type:
      # wb = write as binary
      with open(f'scraped_logo.{image_type}', 'wb') as f:
        f.write(image_res.content)
      

def scrape_books():
  '''
  Scrape all books in a ready to script page
  ''' 
  page_num = 1
  scraped_books = []
  book_page_url = 'http://books.toscrape.com/catalogue'
  rating_dict = { 'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5 }

  # While we can successfully fetch the page contents
  while True:
    print(f'Page Number: {page_num}')
    response = requests.get(f'{book_page_url}/page-{page_num}.html')
    # Exit condition
    if response.status_code != 200:
      break;
    soup = bs4.BeautifulSoup(response.text, 'lxml')

    # Get all books in the current page (products)
    book_elements = soup.select('article.product_pod')
    
    for book_element in book_elements:
      currency = '$'
      price = 0
      title = ''
      rating = 0
      is_in_stock = False
      try:
        # Getting title
        title_element = book_element.select_one('h3 a')
        title = title_element['title']
        # Getting rating
        rating_element = book_element.select_one('p.star-rating')
        for rating_class in rating_element['class']:
          if rating_class in rating_dict.keys():
            rating = rating_dict[rating_class]
            break;
        # Getting price and currency
        price_element = book_element.select_one('p.price_color')
        currency= price_element.text[1:2]
        price = float(price_element.text[2:])
        # Getting stock availability
        in_stock_element = book_element.select_one('p.instock.availability i')
        is_in_stock = in_stock_element.has_attr('class') and 'icon-ok' in in_stock_element['class']
      except Exception as e:
        print(e)
      scraped_books.append({
      "price": price,
      "title": title,
      "rating": rating,
      "currency": currency,
      "is_in_stock": is_in_stock,
    })
    
    page_num += 1
  
  print(f'Scraping finished! Books Found: {len(scraped_books)}')
    
  scraped_books_as_json = json.dumps(scraped_books, indent=2)
  
  with open('scraped_books.json', 'w+') as f:
    f.write(scraped_books_as_json)

   
def scrape_quotes():
  '''
  Scrape all quotes, unique authors and top 10 tags
  '''
  page_num = 1
  scarped_content = {
    "quotes": [],
    "top_10_tags": [],
    "unique_authors": [],
  }
  quote_page_url = "https://quotes.toscrape.com/"
  
  while True:
    print(f'Page Number: {page_num}')
    response = requests.get(f'{quote_page_url}/page/{page_num}')
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    quote_elements = soup.select('div.quote')
  
    # Exit condition
    if response.status_code != 200 or len(quote_elements) == 0:
      break;
    
    # Only on first page populate top_10_tags
    if page_num == 1:
      try:
        top_10_tags_elements = soup.select('div.tags-box > span.tag-item > a.tag')
        for tag_element in top_10_tags_elements:
          scarped_content['top_10_tags'].append(tag_element.text)
      except Exception as e:
        print(e)
    
    try:
      for quote_element in quote_elements:
        quote_data = { "text": '', "author": '', "tags": [] }
        # Getting text
        text_element = quote_element.select_one('span.text')
        quote_data['text'] = text_element.text
        # Getting author
        author_element = quote_element.select_one('small.author')
        quote_data['author']= author_element.text
        if author_element.text not in scarped_content['unique_authors']:  
          scarped_content['unique_authors'].append(author_element.text)
        # Getting tags
        tag_elements = quote_element.select('a.tag')
        for tag_element in tag_elements:
          quote_data['tags'].append(tag_element.text)
        scarped_content['quotes'].append(quote_data)
    except Exception as e:
      print(e)
      
    page_num += 1
    
  # Convert the authors array in a unique set
  scarped_content_as_json = json.dumps(scarped_content, indent=2)
  
  print(f'Scraping finished!\nQuotes Found: {len(scarped_content['quotes'])}\nUnique Authors Found: {len(scarped_content['unique_authors'])}')
  
  with open('scraped_quotes.json', 'w+') as f:
    f.write(scarped_content_as_json)

         
if __name__ == '__main__':
  '''
  Uncomment any function you want to execute when running `python main.py`
  '''
  # scrape_book_thumbnail()
  # scrape_books()
  scrape_quotes()
  pass