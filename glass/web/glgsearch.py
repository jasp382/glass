"""
Search for things in Web
"""

def glg_search(keyword, __site=None, NPAGES=1):
    """
    Google Search by keyword
    """
    
    import pandas
    from google import google
    
    Q = keyword if not __site else "site:{} {}".format(__site, keyword)
    
    results = google.search(Q, NPAGES)
    
    return pandas.DataFrame([[
        i.name, i.link, i.description
    ] for i in results], columns=["name", "url", "description"])

