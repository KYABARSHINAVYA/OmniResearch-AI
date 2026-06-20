import arxiv


def arxiv_search(query):

    try:

        search = arxiv.Search(
            query=query,
            max_results=3
        )

        papers = []

        for paper in search.results():

            papers.append(

                {
                    "title": paper.title,
                    "summary": paper.summary,
                    "url": paper.entry_id
                }

            )

        return papers

    except Exception:

        return []