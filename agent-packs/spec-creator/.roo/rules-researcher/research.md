# Genreal purpose research mode

## Research task instructions

The following instructions define how to do research.
In order to research things corectly we must first search for relvant resources, read those resources, understand the context, rinse and repeat until nough information has been gathered.

The following steps should be used to gather research information.

1. Search the web
2. read the relevant websites found
3. Asses the information gathered
4. If all questions are resolved, complete the research task
4. If neccessary search the web again based on the new context found
6. Continue this process until enough information has been gathered

Each step is layed out in full detail below

### Search

- Select a concept to search
- Write a search query for this concept. The query should be short and concise
- Append the search term to this following url `https://www.bing.com/search?q=`
- Fetch this url from the internet using any of the available tools provided by roo or the terminal
- This url will return html - process the html accordingly

``` Example url processing

var searchQuery = "concept I am researching"
var baseUrl = "https://www.bing.com/search?q="
var searchUrl = String.Concat(baseUrl, searchQuery)
Assert.AreEqual("https://www.bing.com/search?q=concept I am researching", searchUrl)

```

### Read

- Take the search results from the search step and read them
- Each item in the page has a link
- Select the links that seem relevant
- Prefer links that lead to high quality text based web pages such as blogs, news sites, product documentation, wikis etc.
- Read the website of each relevant link
- Fetch these web results using an avaiable tool. Prefer simple fetching for text based sites. Use the browser integration to scrape the content from complex web apps.

### Assess

- Take all the data that was fetched from the various search results
- Asses the information and see if enough data has been found to resolve the users input
- If yes, move on to the respond task
- if not, create a new search term and continue the search, read, assess phases

### Respond

- Only formalize a response once all neccessary context has been found
- Summarize the results in a clear and concide format
- Prefer markdown unless another response format was specified
- Prefer to return results to the calling agent by attempting completion