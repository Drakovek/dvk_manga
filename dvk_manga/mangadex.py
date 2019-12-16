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


def get_id_from_tag(tag: str = None) -> str:
    """
    Returns the ID number from a given MangaDex tag.

    Parameters:
        t (str): MangaDex title tag

    Returns:
        str: MangaDex title ID number
    """
    if tag is None or not tag.lower().startswith("mangadex:"):
        return ""
    return tag[len("MangaDex:"):]


def get_downloaded_titles(dvk_handler: DvkHandler = None) -> list:
    """
    Returns a list of DVKs gathered from MangaDex.org for the purpose of
    downloading new entries to partially downloaded MangaDex titles.

    Parameters:
        dvk_handler (DvkHandler): DvkHandler for loading DVK files

    Returns:
        list: List of DVKs for downloaded MangaDex titles
    """
    if dvk_handler is None:
        return []
    ids = []
    dvks = []
    size = dvk_handler.get_size()
    dvk_handler.sort_dvks("a")
    print("Finding Titles:")
    for i in tqdm(range(0, size)):
        url = dvk_handler.get_dvk_sorted(i).get_page_url().lower()
        if "mangadex.org" in url:
            tags = dvk_handler.get_dvk_sorted(i).get_web_tags()
            for tag in tags:
                lower_tag = tag.lower()
                if lower_tag.startswith("mangadex:"):
                    if lower_tag not in ids:
                        ids.append(lower_tag)
                        dvks.append(dvk_handler.get_dvk_sorted(i))
    return dvks


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


def get_start_chapter(
        dvk_handler: DvkHandler = None,
        chapters: list = None,
        check_all: bool = False) -> int:
    """
    Returns index of the chapter to start downloading from.
    Ignores chapters already downloaded in full.

    Parameters:
        dvk_handler (DvkHandler): DvkHandler for seeing which files
                                  are already downloaded.
        chapters (list): List of Dvks with info from MangaDex chapters,
                         as returned by get_chapters
        check_all (bool): Whether to check all chapters,
                          not just newest chapters

    Returns:
        int:Index of chapter to start downloading
    """
    if chapters is None:
        return 0
    if check_all or dvk_handler is None:
        return len(chapters) - 1
    contains = False
    size = dvk_handler.get_size()
    # FIND CHAPTER TO START WITH
    start_chapter = 0
    while start_chapter < len(chapters):
        c_page_url = chapters[start_chapter].get_page_url()
        for i in range(0, size):
            page_url = dvk_handler.get_dvk_direct(i).get_page_url()
            if page_url.startswith(c_page_url):
                contains = True
                break
        if contains:
            break
        start_chapter = start_chapter + 1
    if start_chapter == len(chapters):
        start_chapter = len(chapters) - 1
    return start_chapter


def get_dvks(
        dvk_handler: DvkHandler = None,
        chapters: list = None,
        save: bool = True,
        check_all: bool = False) -> list:
    """
    Returns list of Dvk objects for each page in given MangaDex chapters.
    Downloads Dvks if specified.

    Parameters:
        dvk_handler (DvkHandler): DvkHandler for seeing which files
                                  are already downloaded.
        chapters (list): List of Dvks with info from MangaDex chapters,
                  as returned by get_chapters
        save (bool): Whether to download images and save Dvk objects
        check_all (bool): Whether to check all chapters,
                          not just newest chapters

    Returns:
        list: List of Dvk objects for MangaDex pages
    """
    if (dvk_handler is None
            or len(dvk_handler.get_paths()) < 1
            or chapters is None
            or len(chapters) == 0):
        return []
    directory = dvk_handler.get_paths()[0]
    print("Downloading pages:")
    start_chapter = get_start_chapter(dvk_handler, chapters, check_all)
    # GET DVKS
    dvks = []
    connect = HeavyConnect()
    for chp in tqdm(range(start_chapter, -1, -1)):
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
                    dvk.write_media()
            page = page + 1
    connect.close_driver()
    return dvks


def download_mangadex(
        url: str = None,
        directory_str: str = None,
        language: str = None,
        check_all: bool = False):
    """
    Downloads files from MangaDex.org

    Parameters:
        url (str): MangaDex title URL
        directory_str (str): Directory in which to save files
        language (str): Language of files to download
        check_all (bool): Whether to check all chapters,
                          not just newest chapters
    """
    dir = Path(directory_str)
    if dir.is_dir():
        dvk_handler = DvkHandler()
        dvk_handler.load_dvks([str(dir.absolute())])
        ids = []
        dirs = []
        if url == "":
            dvks = get_downloaded_titles(dvk_handler)
            for dvk in dvks:
                for tag in dvk.get_web_tags():
                    if tag.lower().startswith("mangadex:"):
                        ids.append(get_id_from_tag(tag))
                        dirs.append(dvk.get_file().parent)
                        break
        else:
            ids = [get_title_id(url)]
            dirs = [dir]
        for i in range(0, len(ids)):
            if ids[i] == "":
                print("Invalid MangaDex.org URL")
            else:
                title = get_title_info(ids[i])
                print(title.get_title())
                chapters = get_chapters(title, language)
                get_dvks(
                    dvk_handler,
                    chapters,
                    True,
                    check_all)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "url",
        help="MangaDex Title URL",
        nargs="?",
        type=str,
        default="")
    parser.add_argument(
        "-d",
        "--directory",
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
    parser.add_argument(
        "-c",
        "--check_all",
        help="Checks for images in all chapters, even if already downloaded.",
        action="store_true")
    args = parser.parse_args()
    url = str(args.url)
    dir = str(Path(args.directory))
    language = str(args.language)
    check_all = bool(args.check_all)
    download_mangadex(url, dir, language, check_all)


if __name__ == "__main__":
    main()
