"""
Parse HTML data via Python
"""

def get_text_in_html(url, tags=['h1', 'h2', 'h3', 'p']):
    """
    Get p tags from HTML
    """
    
    import urllib2; import re
    from bs4 import BeautifulSoup
    
    response = urllib2.urlopen(url)
    
    html_doc = response.read()
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    txtData = {
        tag : [re.sub(
            '<[^>]+>', '', str(x)
        ).strip('\n') for x in soup.find_all(tag)] for tag in tags
    }
    
    return txtData


def get_text_in_CssClass(url, classTag, cssCls, texTags=['p']):
    """
    Get text from tags inside a specific object with one tag (classTag) and
    CSS Class (cssCls)
    
    Not recursive: textTags must be direct child of the classTag/cssCls
    """
    
    import urllib2
    import re
    from bs4  import BeautifulSoup
    from glass.pys import obj_to_lst
    
    resp = urllib2.urlopen(url)
    
    html_doc = resp.read()
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    data = soup.find_all(classTag, class_=cssCls)
    
    rslt = {}
    texTags = obj_to_lst(texTags)
    for node in data:
        for t in texTags:
            chld = node.findChildren(t, recursive=False)
            
            l = [re.sub('<[^>]+>', '', str(x)).strip('\n') for x in chld]
            
            if t not in rslt:
                rslt[t] = l
            
            else:
                rslt[t] += l
    
    return rslt
