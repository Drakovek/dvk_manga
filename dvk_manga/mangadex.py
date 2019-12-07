from re import compile
from dvk_archive.file.dvk import Dvk
from dvk_archive.web.basic_connect import basic_connect
from dvk_archive.processing.html_processing import replace_escapes
from dvk_archive.processing.list_processing import clean_list


def get_title_id(url: str = None) -> str:
    """
    Returns the ID number from a given MangaDex title URL.

    Parameters:
        url (str): MangaDex title URL

    Returns:
        str: MangaDex title ID number
    """
    if url is None or "mangadex.org/title/" not in url:
        return ""
    start = url.index("/title/") + 1
    start = url.index("/", start) + 1
    try:
        end = url.index("/", start)
    except ValueError:
        end = len(url)
    try:
        id = int(url[start:end])
    except ValueError:
        return ""
    return str(id)


def get_title_info(title_num: str = None) -> Dvk:
    """
    Gets information about a MangaDex title and returns as a Dvk object.
    Includes title, artist/author, web_tags, and description.

    Parameters:
        title_num (str): ID Number for a MangaDex title.

    Returns:
        Dvk: Dvk holding MangaDex title information
    """
    dvk = Dvk()
    dvk.set_page_url("https://mangadex.org/title/" + title_num + "/")
    bs = basic_connect(dvk.get_page_url())
    try:
        # GET TITLE
        title = replace_escapes(bs.find("span", {"class": "mx-1"}).get_text())
        dvk.set_title(title)
        # GET ARTISTS
        regex = "/search\\?author=*"
        artists = [bs.find("a", {"href": compile(regex)}).get_text()]
        regex = "/search\\?artist=*"
        artists.append(bs.find("a", {"href": compile(regex)}).get_text())
        dvk.set_artists(artists)
        # GET TAGS
        tags = ["Mangadex:" + title_num]
        bs_list = bs.findAll("a", {"class": "genre"})
        bs_list.extend(bs.findAll("a", {"class": "badge badge-secondary"}))
        for item in bs_list:
            tags.append(replace_escapes(item.get_text()))
        tags = clean_list(tags)
        dvk.set_web_tags(tags)
        # GET DESCRIPTION
        bs_list = bs.findAll("div", {"class": "col-lg-3 col-xl-2 strong"})
        for item in bs_list:
            if item.get_text() == "Description:":
                sibling = item.find_next_sibling("div")
                dvk.set_description(sibling.get_text())
                break
        # GET PAGE
        regex = "/title/" + title_num + "/*"
        bs_list = bs.findAll("a", {"href": compile(regex)})
        if len(bs_list) > 0:
            url = str(bs_list[0]["href"])
            start = url.index("/" + title_num + "/") + 1
            start = url.index("/", start) + 1
            end = url.index("/", start)
            page_url = "https://mangadex.org/title/"
            page_url = page_url + title_num + "/" + url[start:end] + "/"
            dvk.set_page_url(page_url)
    except AttributeError:
        dvk.set_title(None)
    return dvk
