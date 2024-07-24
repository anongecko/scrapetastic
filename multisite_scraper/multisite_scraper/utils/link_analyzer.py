from urllib.parse import urljoin

def analyze_links(response):
    links = response.css('a::attr(href)').getall()
    absolute_links = [urljoin(response.url, link) for link in links]
    return {
        'total_links': len(links),
        'internal_links': len([link for link in absolute_links if link.startswith(response.url)]),
        'external_links': len([link for link in absolute_links if not link.startswith(response.url)])
    }