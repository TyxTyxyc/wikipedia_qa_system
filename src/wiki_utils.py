import wikipedia

wikipedia.set_lang("ru")


def make_wiki_query(q: str) -> str:
    """
    Make a query to Wikipedia to get relevant information about
    any subject. This call returns top-3 search results. If error
    is occured, error text will be in return string.

    Parameters
    ----------
    q : string
        search query to Wikipedia. Should be string

    Returns
    -------
    string
        top-3 result of the query separated by Page OR error description
        if any error has occured
    """
    try:
        page_titles = wikipedia.search(q, results=3)

        summaries = []
        for page_name in page_titles[:3]:
            wiki_page = wikipedia.page(page_name)
            to_append = f"page: {page_name} \n summary: {wiki_page.summary}"
            summaries.append(to_append)

        return "\n\n".join(summaries)
    except Exception as e:
        return f"An error occurred while querying Wikipedia: {str(e)}"


def get_full_wiki_page(page_name: str) -> str:
    """
    Get full Wikipedia page titled as page_name. Return error if no
    page found

    Parameters
    ----------
    page_name : string
        name of the page to get from Wikipedia

    Returns
    -------
    string
        full text of Wikipedia page
    """
    try:
        return wikipedia.page(page_name).content
    except Exception as e:
        return f"An error occurred while querying Wikipedia: {str(e)}"
