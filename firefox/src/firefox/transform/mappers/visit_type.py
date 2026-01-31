# - 1	TRANSITION_LINK                 The user followed a link and got a new toplevel window.
# -- 2	TRANSITION_TYPED	        The user typed the page's URL in the URL bar or selected it from URL bar autocomplete results, clicked on it from a history query (from the History sidebar, History menu, or history query in the personal toolbar or Places organizer.
# -- 3	TRANSITION_BOOKMARK	        The user followed a bookmark to get to the page.
# -- 4	TRANSITION_EMBED	        Set when some inner content is loaded. This is true of all images on a page, and the contents of the iframe. It is also true of any content in a frame, regardless of whether or not the user clicked something to get there.
# -- 5	TRANSITION_REDIRECT_PERMANENT	The transition was a permanent redirect.
# -- 6	TRANSITION_REDIRECT_TEMPORARY	The transition was a temporary redirect.
# -- 7	TRANSITION_DOWNLOAD	        The transition is a download.
# -- 8    TRANSITION_FRAMED_LINK          The user followed a link and got a visit in a frame.
# -- 9    TRANSITION_RELOAD               The page has been reloaded.
# https://gist.github.com/olejorgenb/9418bef65c65cd1f489557cfc08dde96?utm_source=chatgpt.com
_VISIT_TYPE_MAP = {
    1: "link",
    2: "typed",
    3: "bookmark",
    4: "embed",
    5: "redirectPermanent",
    6: "redirectTemporary",
    7: "download",
    8: "framedLink",
    9: "reload",
}


def transform_visit_type(visit_type: int) -> str:
    return _VISIT_TYPE_MAP[visit_type]
