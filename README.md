# Super Recipe-o-matic 2000

How many times has this happened to you? You want a simple recipe dataset so you can machine learn you a sandwich, but there's nothing good in your internet! Now, you could pay some schmuck $5000 to use their buzzword-tastic service, but why bother when you can scrape the data yourself with the Super Recipe-o-matic 2000.

The Super Recipe-o-matic 2000 scrapes AllRecipes.com to extract recipe data, shifting through all the cruft to produce nice simple json, just the way you like it.

## Here's how it works
First install the Python dependencies.

```sh
$ pip install requests
```

Now, visit AllRecipes.com and get yourself the `Authorization` header from a request to `apps.allrecipes.com`. Take the authorization header – that's the *whole* authorization header – and drop it right into your command prompt:

```
$ python3 main.py --bearer="Bearer P6k/U+2F1ECWIwpm..."
```

The easiest way to get the authorization header is from `http://allrecipes.com/recipes/` which makes an AJAX request to load new page data for infinite scrolling.

Press enter and let the script chug away, generating recipes in `recipes.json`. Yes, it's that simple!


Here are the other flags:

```
$ python3 main.py \
    --bearer ALL_RECIPES_GENERATED_BEARER_AUTH_HEADER \
    -o PATH \ Where should result be written? 
    -i PATH \ Used to load existing data from a file and append to it.
    --start INT \ What page to start loading data from.
    --page_size INT \ What page to start loading data from.
``` 

The optional input file is used to pick up from where an existing task left off. If provided, the output data is appended to the input data. Make sure to use the same `--page_size` though and pass in `--start`.
    
### Wow, that's terrific data! 
The top level object looks like this:

```js
{
  "version": 0,
  "source": "http://allrecipes.com",
  "recipes": [
     ...
  ]
}
```

Each recipe looks like this:

```js
{
  "id": INT Unique recipe identifier,
  "title": STRING Recipe title,
  "description": STRING Recipe description,
  "prep_minutes": INT,
  "cook_minutes": INT,
  "ready_in_minutes": INT,
  "ingredients": [
    STRING Ingredient description,
    ...
  ],
  "directions": [
    STRING Direction,
    ...
  ],
  "footnotes": [
    STRING Extra note,
    ...
  ]
}
```

Clean, simple, and after five to ten thousand recipes, it gets to be quite a rush!

