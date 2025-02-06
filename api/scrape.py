from scraping import auto

def handler(request, response):
    auto()
    return response.json({"status": "Scraping completed"})