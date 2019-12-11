from os import getcwd
from re import compile
from tqdm import tqdm
from time import sleep
from pathlib import Path
from argparse import ArgumentParser
from dvk_archive.file.dvk import Dvk
from dvk_archive.file.dvk_handler import DvkHandler
from dvk_archive.processing.string_processing import get_extension
from dvk_archive.web.basic_connect import basic_connect
from dvk_archive.web.basic_connect import download
from dvk_archive.web.heavy_connect import HeavyConnect
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
            title = base_dvk.get_title() + " | " + link.get_text()
            dvk.set_title(replace_escapes(title))
            dvk.set_page_url("https://mangadex.org" + link["href"] + "/")
            # GET ID
            start = dvk.get_page_url().index("/chapter/") + 1
            start = dvk.get_page_url().index("/", start) + 1
            end = dvk.get_page_url().index("/", start)
            dvk.set_id(dvk.get_page_url()[start:end])
            # GET TIME PUBLISHED
            sibling = sibling.find_next_sibling(
                "div",
                {"class": compile("order-lg-8")})
            dvk.set_time(str(sibling["title"])[0:16])
            # GET TRANSLATION GROUP
            authors = dvk.get_artists()
            sibling = sibling.find_next_sibling(
                "div",
                {"class": compile("chapter-list-group")})
            groups = sibling.findAll("a")
            for group in groups:
                authors.append(group.get_text())
            dvk.set_artists(authors)
            # APPEND
            dvks.append(dvk)
        except (AttributeError, TypeError):
            return []
    if len(bs.findAll("a", {"class": "text-truncate"})) > 0:
        dvks.extend(get_chapters(base_dvk, language, page_num + 1))
    return dvks


def get_dvks(
        directory_str: str = None,
        chapters: list = None,
        save: bool = True) -> list:
    """
    Returns list of Dvk objects for each page in given MangaDex chapters.
    Downloads Dvks if specified.

    Parameters:
        directory_str (str): Directory to read/save from
        chapters (list): List of Dvks with info from MangaDex chapters,
                  as returned by get_chapters
        save (bool): Whether to download images and save Dvk objects

    Returns:
        list: List of Dvk objects for MangaDex pages
    """
    if directory_str is None or chapters is None or len(chapters) == 0:
        return []
    directory = Path(directory_str)
    dvk_handler = DvkHandler()
    dvk_handler.load_dvks([directory_str])
    print("Downloading pages:")
    contains = False
    size = dvk_handler.get_size()
    # FIND CHAPTER TO START WITH
    chapter_num = 0
    while chapter_num < len(chapters):
        c_page_url = chapters[chapter_num].get_page_url()
        for i in range(0, size):
            page_url = dvk_handler.get_dvk_direct(i).get_page_url()
            contains = page_url.startswith(c_page_url)
        if contains:
            break
        chapter_num = chapter_num + 1
    if chapter_num == len(chapters):
        chapter_num = chapter_num - 1
    # GET DVKS
    dvks = []
    connect = HeavyConnect()
    for chp in tqdm(range(chapter_num, -1, -1)):
        page = 1
        c_id = chapters[chp].get_id()
        while True:
            # FIND IMAGE URL
            dvk = Dvk()
            dvk.set_id("MDX" + chapters[chp].get_id() + "-" + str(page))
            dvk.set_title(chapters[chp].get_title() + " | Pg. " + str(page))
            dvk.set_artists(chapters[chp].get_artists())
            dvk.set_time(chapters[chp].get_time())
            dvk.set_web_tags(chapters[chp].get_web_tags())
            dvk.set_description(chapters[chp].get_description())
            dvk.set_page_url(chapters[chp].get_page_url() + str(page))
            dvk.set_file(directory.joinpath(dvk.get_filename() + ".dvk"))
            if not dvk_handler.contains_page_url(dvk.get_page_url()):
                bs = connect.get_page(
                    dvk.get_page_url(), 1,
                    element="//img[@class='noselect nodrag cursor-pointer']")
                if bs is None:
                    break
                # CHECK IF IN RIGHT CHAPTER
                current_id = bs.find(
                    "span", {"class": "chapter-title"})["data-chapter-id"]
                if not current_id == c_id:
                    break
                # GET DIRECT IMAGE URL
                parents = bs.findAll("div", {"data-page": str(page)})
                ims = []
                for parent in parents:
                    ims.append(
                        parent.find(
                            "img",
                            {"class": "noselect nodrag cursor-pointer"}))
                if len(ims) == 0:
                    break
                dvk.set_direct_url(ims[0]["src"])
                extension = get_extension(dvk.get_direct_url())
                dvk.set_media_file(dvk.get_filename() + extension)
                dvks.append(dvk)
                # DOWNLOAD IF SPECIFIED
                if save:
                    dvk.write_dvk()
                    download(dvk.get_direct_url(), dvk.get_media_file())
            page = page + 1
    connect.close_driver()
    return dvks


def download_mangadex(
        url: str = None,
        directory_str: str = None,
        language: str = None):
    """
    Downloads files from MangaDex.org

    Parameters:
        url (str): MangaDex title URL
        directory_str (str): Directory in which to save files
        language (str): Language of files to download
    """
    dir = Path(directory_str)
    if dir.is_dir():
        id = get_title_id(url)
        if id == "":
            print("Invalid MangaDex.org URL")
        else:
            title = get_title_info(id)
            print(title.get_title())
            chapters = get_chapters(title, language)
            get_dvks(str(dir.absolute()), chapters, True)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "url",
        help="MangaDex Title URL",
        type=str)
    parser.add_argument(
        "directory",
        help="Directory in which to preform operations.",
        nargs="?",
        type=str,
        default=str(getcwd()))
    parser.add_argument(
        "-l",
        "--language",
        help="Language of images to download (defaults to \"English\")",
        nargs="?",
        type=str,
        default="English")
    args = parser.parse_args()
    url = str(args.url)
    dir = str(Path(args.directory))
    language = str(args.language)
    download_mangadex(url, dir, language)


if __name__ == "__main__":
    main()
