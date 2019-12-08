from re import compile
from time import sleep
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
    print("Finding Chapters...")
    bs = basic_connect(dvk.get_page_url())
    sleep(1)
    try:
        # GET TITLE
        title = replace_escapes(bs.find("span", {"class": "mx-1"}).get_text())
        dvk.set_title(title)
        # GET ARTISTS
        regex = "/search\\?author="
        artists = [bs.find("a", {"href": compile(regex)}).get_text()]
        regex = "/search\\?artist="
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
        regex = "/title/" + title_num + "/"
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
        dvk.set_page_url(None)
    return dvk


def get_chapters(
        base_dvk: Dvk = None,
        language: str = "English",
        page_num: int = 1) -> list:
    """
    Returns list of Dvks holding MangaDex chapter information.
    Information includes title, and time published.

    Parameters:
        base_dvk (Dvk): Dvk with MangaDex title information
        language (str): Language of chapters to download
        page_num (int): Page of chapter links to search through

    Returns:
        list: List of Dvks holding MangaDex chapter information
    """
    print("Page: " + str(page_num) + "...")
    dvks = []
    if base_dvk is None or base_dvk.page_url is None:
        return dvks
    bs = basic_connect(base_dvk.get_page_url() + "chapters/" + str(page_num))
    sleep(1)
    try:
        bs_list = bs.findAll("span", {"title": language})
    except AttributeError:
        return dvks
    for item in bs_list:
        # SET ALREADY DETERMINED INFORMATION
        dvk = Dvk()
        dvk.set_artists(base_dvk.get_artists())
        dvk.set_web_tags(base_dvk.get_web_tags())
        dvk.set_description(base_dvk.get_description())
        try:
            # GET TITLE AND PAGE_URL
            sibling = item.find_parent().find_previous_sibling(
                "div", {"class": compile("pr-1")})
            link = sibling.find("a", {"class": "text-truncate"})
            dvk.set_title(base_dvk.get_title() + " | " + link.get_text())
            dvk.set_page_url("https://mangadex.org" + link["href"])
            # GET TIME PUBLISHED
            sibling = sibling.find_next_sibling(
                "div",
                {"class": compile("order-lg-8")})
            dvk.set_time(str(sibling["title"])[0:16])
            # APPEND
            dvks.append(dvk)
        except (AttributeError, TypeError):
            return []
    if len(bs.findAll("a", {"class": "text-truncate"})) > 0:
        dvks.extend(get_chapters(base_dvk, language, page_num + 1))
    return dvks
