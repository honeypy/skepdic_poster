import facebook
import sys
import os
import urllib3

def main(text, img):
    # Fill in the values noted in previous steps here
    cfg = {
    "page_id"      : "223613637798588",  # Step 1
    "access_token" : "CAANYzqudN00BANpQYlGdVz5im8yTSqrz5lowwai51T9tdKvsRw1CidSJwAgrbPYeDqMYFTNxQcdyxte9Xa7yLTVwCsZBwPR1GyWcCztjCtfdZC4P3dJZCmlZA9jcI6ebUeZAZBp7efAdEHpAIFP0FV6GarPPjId2FAiT3yT95CLQXF460atZBrGxuVy20JS1FUZD" # Step 3
    }

    api = get_api(cfg)
    status = api.put_wall_post(text, attachment={'source': img})

def main2(text):
    # Fill in the values noted in previous steps here
    cfg = {
    "page_id"      : "223613637798588",  # Step 1
    "access_token" : "CAANYzqudN00BANpQYlGdVz5im8yTSqrz5lowwai51T9tdKvsRw1CidSJwAgrbPYeDqMYFTNxQcdyxte9Xa7yLTVwCsZBwPR1GyWcCztjCtfdZC4P3dJZCmlZA9jcI6ebUeZAZBp7efAdEHpAIFP0FV6GarPPjId2FAiT3yT95CLQXF460atZBrGxuVy20JS1FUZD" # Step 3
    }

    api = get_api(cfg)
    status = api.put_wall_post(text)


def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    # Get page token to post as the page. You can skip
    # the following if you want to post as yourself.
    resp = graph.get_object('me/accounts')
    page_access_token = None

    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
    graph = facebook.GraphAPI(page_access_token)
    return graph
    # You can also skip the above if you get a page token:
    # http://stackoverflow.com/questions/8231877/facebook-access-token-for-pages
    # and make that long-lived token as in Step 3
