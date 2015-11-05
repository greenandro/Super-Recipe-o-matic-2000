"""
Super Recipe-o-matic 2000

Python3 script to scrape recipe data from AllRecipes.com
"""
import argparse
import itertools
import json
import requests
from collections import OrderedDict

API_RECIPES = "https://apps.allrecipes.com/v1/recipe-hubs/1/recipes"
API_RECIPE = "https://apps.allrecipes.com/v1/recipes/{0}"

DATA_VERSION = 0

bearer = None

def get_recipes(page, page_size=20, sort_type='Popular'):
    """Get raw data for a set of recipes."""
    r = requests.get(API_RECIPES,
        params={ 'page': page, 'pagesize': page_size, 'sorttype': sort_type},
        headers={ 'Authorization': bearer })
    if r.status_code != 200:
        print("Request error", r)
        return None
    return r.json()['recipes']

def get_recipe(id):
    """Get raw data for a single recipe."""
    r = requests.get(API_RECIPE.format(id),
        headers={ 'Authorization': bearer })
    if r.status_code != 200:
        print("Request error", r)
        return None
    return r.json()

def process_ingredients(raw_ingredients):
    """Extract important data for raw ingredients list."""
    return [x['displayValue'] for x in raw_ingredients if x['displayType'] == 'Normal']

def process_directions(raw_directions):
    """Extract important data for raw directions list."""
    return [x['displayValue'] for x in raw_directions]

def process_footnotes(raw_footnotes):
    """Extract important data for raw ingredients list."""
    return [x['text'] for x in raw_footnotes]

def process_recipe(raw_data, description=None):
    """Extract important data for raw recipe."""
    return OrderedDict([
        ('id', raw_data['recipeID']),
        ('title', raw_data['title']),
        ('description', description if description is not None else raw_data['description']),
        ('prep_minutes', raw_data['prepMinutes']),
        ('cook_minutes', raw_data['cookMinutes']),
        ('ready_in_minutes', raw_data['readyInMinutes']),
        ('ingredients', process_ingredients(raw_data['ingredients'])),
        ('directions', process_directions(raw_data['directions'])),
        ('footnotes', process_footnotes(raw_data['footnotes']))
    ])
    
def create_recipe_list(raw_data):
    """Get recipe data from list returned by `get_recipes`."""
    for x in raw_data:
        yield process_recipe(
            get_recipe(x['recipeID']),
            description=x['description'])
    
def load_current_recipes(file):
    """Load current recipes from a file"""
    if file is None:
        return []
    with open(file, 'r') as f:
        data = json.load(f)
        if data['version'] != DATA_VERSION:
            print("WARNING - New and current data versions do not match")
        return data['recipes']

def get_current_ids(recipes):
    """Get map of current recipe ids"""
    keys = {}
    for x in recipes:
        keys[x['id']] = 1
    return keys

def load_new_recipes(current_ids, page, page_size):
    r = get_recipes(page, page_size=page_size)
    if r is None:
        return None
    new_recipes = [data for data in r if not data['recipeID'] in current_ids]
    return create_recipe_list(new_recipes)

def write_recipes(recipes, file):
    """Write recipe data to a file."""
    with open(file, 'w') as f:
        return json.dump(OrderedDict([
            ('version', DATA_VERSION),
            ('source', 'http://allrecipes.com'),
            ('recipes', recipes)]), f, indent=4)


def lookup_recipes_loop(current_recipes, outfile, start, page_size):
    """Man script loop"""
    current_ids = get_current_ids(current_recipes)
    for i in itertools.count(start):
        print("Processing page {0} with step {1}".format(i, page_size))
        new = load_new_recipes(current_ids, i, page_size)
        if new is None:
            break
        for x in new:
            current_ids[x['id']] = 1
            current_recipes.append(x)
        print("Wrote output - {0}".format(outfile))
        write_recipes(current_recipes, outfile)

parser = argparse.ArgumentParser()
parser.add_argument("--bearer", dest="bearer", help="Allrecipes auth header value: 'Bearer ...'")
parser.add_argument("-o", "--output", dest="output", default="recipes.json", help="File to write results to.")
parser.add_argument("-i", "--input", dest="input", default=None, help="File to read and append results to.")
parser.add_argument("--start", dest="start", default=1, help="starting page.", type=int)
parser.add_argument("--page_size", dest="page_size", default=20, help="page size to process.", type=int)

args = parser.parse_args()
bearer = args.bearer

current_recipes = load_current_recipes(args.input)
lookup_recipes_loop(current_recipes, args.output, args.start, args.page_size)
