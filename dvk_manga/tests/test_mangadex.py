from pathlib import Path
from shutil import rmtree
from traceback import print_exc
from dvk_archive.file.dvk import Dvk
from dvk_archive.file.dvk_handler import DvkHandler
from dvk_manga.mangadex import get_title_id
from dvk_manga.mangadex import get_id_from_tag
from dvk_manga.mangadex import get_downloaded_titles
from dvk_manga.mangadex import get_title_info
from dvk_manga.mangadex import get_chapters
from dvk_manga.mangadex import get_start_chapter
from dvk_manga.mangadex import get_dvks


class TestMangadex():
    """
    Unit tests for the mangadex.py module.
    """

    def test_all(self):
        """
        Tests all functions of the mangadex.py module.
        """
        try:
            self.test_get_title_id()
            self.test_get_id_from_tag()
            self.test_get_downloaded_titles()
            self.test_get_title_info()
            self.test_get_chapters()
            self.test_get_start_chapter()
            self.test_get_dvks()
            print("\033[32mAll dvk_manga tests passed.\033[0m")
        except AssertionError:
            print("\033[31mCheck failed:\033[0m")
            print_exc()

    def test_get_title_id(self):
        """
        Tests the get_title_id function.
        """
        assert get_title_id() == ""
        assert get_title_id("www.differentsite.com") == ""
        assert get_title_id("www.mangadex.cc/nope/27153/") == ""
        assert get_title_id("www.mangadex.cc/title/invalid/") == ""
        assert get_title_id("mangadex.cc/title/27152") == "27152"
        i = "www.mangadex.cc/title/27153/jojo-s-bizarre-adventure"
        assert get_title_id(i) == "27153"

    def test_get_id_from_tag(self):
        """
        Tests the get_id_from_tag function
        """
        assert get_id_from_tag() == ""
        assert get_id_from_tag("Bleh") == ""
        assert get_id_from_tag("MangaDex:") == ""
        assert get_id_from_tag("MangaDex:137") == "137"
        assert get_id_from_tag("Mangadex:2345") == "2345"
        assert get_id_from_tag("mangadex:bleh") == "bleh"

    def test_get_downloaded_titles(self):
        try:
            test_dir = Path("mangadex1")
            test_dir.mkdir(exist_ok=True)
            sub_dir = test_dir.joinpath("sub")
            sub_dir.mkdir(exist_ok=True)
            dvks = get_downloaded_titles()
            assert dvks == []
            dvk_handler = DvkHandler()
            dvk_handler.load_dvks([str(test_dir.absolute())])
            dvks = get_downloaded_titles(dvk_handler)
            assert dvks == []
            # DVK 1 - MANGADEX:123
            dvk = Dvk()
            dvk.set_file(str(test_dir.joinpath("dvk1.dvk").absolute()))
            dvk.set_id("id")
            dvk.set_title("dvk")
            dvk.set_artist("artist")
            dvk.set_page_url("https://MangaDex.cc/blah")
            dvk.set_media_file("file")
            dvk.set_web_tags(["mangadex:123"])
            dvk.write_dvk()
            # DVK 2 - REPEAT MANGADEX TAG
            dvk.set_file(str(test_dir.joinpath("dvk2.dvk").absolute()))
            dvk.set_media_file("file")
            dvk.write_dvk()
            # DVK 3 - NEW MANGADEX TAG
            dvk.set_file(str(test_dir.joinpath("dvk3.dvk").absolute()))
            dvk.set_media_file("file")
            dvk.set_web_tags(["MangaDex:702"])
            dvk.write_dvk()
            # DVK 4 - NEW MANGADEX TAG - INVALID PAGE_URL
            dvk.set_file(str(test_dir.joinpath("dvk4.dvk").absolute()))
            dvk.set_media_file("file")
            dvk.set_page_url("something.com")
            dvk.set_web_tags(["blah", "MangaDex:137"])
            dvk.write_dvk()
            # DVK SUB - NEW MANGADEX TAG
            dvk.set_file(str(sub_dir.joinpath("dvk-sub.dvk").absolute()))
            dvk.set_media_file("file")
            dvk.set_page_url("https://MangaDex.org/blah")
            dvk.set_web_tags(["MangaDex:29"])
            dvk.write_dvk()
            # CHECK DVK 1
            dvk_handler.load_dvks([str(test_dir.absolute())])
            dvks = get_downloaded_titles(dvk_handler)
            test = False
            assert len(dvks) == 3
            for dvk in dvks:
                file = dvk.get_file()
                if (str(file.parent.absolute()) == str(test_dir.absolute())
                        and str(file.name) == "dvk1.dvk"):
                    test = dvk.get_web_tags()[0] == "mangadex:123"
                    break
            assert test
            # CHECK DVK 3
            test = False
            for dvk in dvks:
                file = dvk.get_file()
                if (str(file.parent.absolute()) == str(test_dir.absolute())
                        and str(file.name) == "dvk3.dvk"):
                    test = dvk.get_web_tags()[0] == "MangaDex:702"
                    break
            assert test
            # CHECK DVK SUB
            test = False
            for dvk in dvks:
                file = dvk.get_file()
                if str(file.parent.absolute()) == str(sub_dir.absolute()):
                    test = dvk.get_web_tags()[0] == "MangaDex:29"
                    break
            assert test
        finally:
            # DELETE TEST DIRECTORY
            rmtree(test_dir.absolute())

    def test_get_title_info(self):
        """
        Tests the get_title_info function.
        """
        # INVALID
        dvk = get_title_info("bleh")
        assert dvk.get_title() is None
        assert dvk.get_page_url() is None
        dvk = get_title_info("90000000000")
        assert dvk.get_title() is None
        assert dvk.get_page_url() is None
        # TITLE 1
        dvk = get_title_info("34326")
        assert dvk.get_title() == "Randomphilia"
        assert dvk.get_artists() == ["Devin Bosco Le"]
        tags = [
            "Mangadex:34326", "Shounen", "4-Koma", "Full Color", "Long Strip",
            "Official Colored", "Web Comic", "Comedy", "Slice of Life"]
        assert dvk.get_web_tags() == tags
        desc = "English :<br/>&#13;A world where logic does not exist and anything is possible. The only limit is your imagination. Bite-sized comics with dry humor for the broken souls.<br/><br/>&#13;Un monde o&#249; la logique n&#8217;existe pas et o&#249; tout est possible. La seule limite est votre imagination. Des bandes dessin&#233;es mordues."
        assert dvk.get_description() == desc
        page_url = "https://mangadex.cc/title/34326/randomphilia/"
        assert dvk.get_page_url() == page_url
        # TITLE 2
        dvk = get_title_info("27152")
        title = "JoJo's Bizarre Adventure Part 2 - "
        title = title + "Battle Tendency (Official Colored)"
        assert dvk.get_title() == title
        assert dvk.get_artists() == ["Araki Hirohiko"]
        tags = [
            "Mangadex:27152", "Shounen", "Full Color", "Official Colored",
            "Action", "Adventure", "Comedy", "Drama", "Historical", "Horror",
            "Mystery", "Martial Arts", "Supernatural", "Vampires"]
        assert dvk.get_web_tags() == tags
        desc = "Second story arc of JoJo no Kimyou na Bouken series.<br/><br/>&#13;Takes place in the 1930s, and follows the misadventures of Joseph Joestar, the grandson of Jonathan Joestar, as he fights vampires and ancient super beings with some help from a cybernetically-enhanced Nazi and an Italian man he has a lot in common with."
        assert dvk.get_description() == desc
        page_url = "https://mangadex.cc/title/27152/jojo-s-bizarre-adventure-"
        page_url = page_url + "part-2-battle-tendency-official-colored/"
        assert dvk.get_page_url() == page_url

    def test_get_chapters(self):
        """
        Tests the get_chapters function.
        """
        # INVALID
        dvks = get_chapters()
        assert len(dvks) == 0
        dvk = Dvk()
        dvks = get_chapters(dvk)
        assert len(dvks) == 0
        dvk.set_page_url("https://mangadex.cc")
        dvks = get_chapters(dvk)
        assert len(dvks) == 0
        # TITLE 1
        title = "JoJo's Bizarre Adventure Part 2 - "
        title = title + "Battle Tendency (Official Colored)"
        dvk.set_title(title)
        page_url = "https://mangadex.cc/title/27152/jojo-s-bizarre-adventure-"
        page_url = page_url + "part-2-battle-tendency-official-colored/"
        dvk.set_page_url(page_url)
        dvk.set_artist("Araki Hirohiko")
        dvks = get_chapters(dvk, language="English")
        assert len(dvks) == 69
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official Colored) | Vol. 7 Ch. 69  - The Comeback"
        assert dvks[0].get_title() == title
        artists = ["Araki Hirohiko", "JoJo's Colored Adventure"]
        assert dvks[0].get_artists() == artists
        assert dvks[0].get_page_url() == "https://mangadex.cc/chapter/2140/"
        assert dvks[0].get_id() == "2140"
        assert dvks[0].get_time() == "2018/01/18|19:08"
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official Colored) | Vol. 4 Ch. 39  - Chasing the Red Stone to Swizerland"
        assert dvks[30].get_title() == title
        artists = ["Araki Hirohiko", "JoJo's Colored Adventure"]
        assert dvks[30].get_artists() == artists
        assert dvks[30].get_time() == "2018/01/18|18:44"
        assert dvks[30].get_page_url() == "https://mangadex.cc/chapter/2081/"
        assert dvks[30].get_id() == "2081"
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official Colored) | Vol. 1 Ch. 1  - Joseph Joestar of New York"
        assert dvks[68].get_title() == title
        artists = ["Araki Hirohiko", "JoJo's Colored Adventure"]
        assert dvks[68].get_artists() == artists
        assert dvks[68].get_time() == "2018/01/18|16:44"
        assert dvks[68].get_page_url() == "https://mangadex.cc/chapter/1949/"
        assert dvks[68].get_id() == "1949"
        dvks = get_chapters(dvk, language="Italian")
        assert len(dvks) == 26
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official Colored) | Vol. 3 Ch. 26  - La maledizione delle fedi"
        assert dvks[0].get_title() == title
        assert dvks[0].get_artists() == ["Araki Hirohiko", "JoJo No Sense"]
        assert dvks[0].get_time() == "2019/07/31|16:16"
        assert dvks[0].get_page_url() == "https://mangadex.cc/chapter/676740/"
        assert dvks[0].get_id() == "676740"
        # TITLE 2
        dvk.set_title("Randomphilia")
        dvk.set_artist("Devin Bosco Le")
        page_url = "https://mangadex.cc/title/34326/randomphilia/"
        dvk.set_page_url(page_url)
        dvks = get_chapters(dvk, language="English")
        assert len(dvks) == 0
        dvks = get_chapters(dvk, language="French")
        assert len(dvks) == 75
        print(dvks[0].get_title())
        assert dvks[0].get_title() == "Randomphilia | Ch. 75"
        assert dvks[0].get_artists() == ["Biru no Fukuro", "Devin Bosco Le"]
        assert dvks[0].get_time() == "2019/12/21|15:03"
        assert dvks[0].get_page_url() == "https://mangadex.cc/chapter/770792/"
        assert dvks[0].get_id() == "770792"

    def test_get_start_chapter(self):
        test_dir = Path("mangadex2")
        try:
            test_dir.mkdir(exist_ok=True)
            dvk_handler = DvkHandler()
            dvk_handler.load_dvks([str(test_dir.absolute())])
            assert get_start_chapter(dvk_handler) == 0
            title_info = get_title_info("34326")
            chapters = get_chapters(title_info, language="French")
            assert get_start_chapter(dvk_handler, chapters) == 74
            # CREATE DVK
            test_dir.mkdir(exist_ok=True)
            dvk = Dvk()
            dvk.set_id("MDX761781-5")
            dvk.set_title("Randomphilia | Ch. 72 | Pg. 5")
            dvk.set_page_url("https://mangadex.cc/chapter/688478/1")
            dvk.set_artist("whatever")
            file = test_dir.joinpath(dvk.get_filename() + ".dvk")
            dvk.set_file(file.absolute())
            dvk.set_media_file("unimportant.png")
            dvk.write_dvk()
            dvk_handler.load_dvks([str(test_dir.absolute())])
            assert get_start_chapter(dvk_handler, chapters) == 5
            assert get_start_chapter(dvk_handler, chapters, True) == 74
        finally:
            rmtree(test_dir.absolute())

    def test_get_dvks(self):
        """
        Tests the get_dvks function.
        """
        test_dir = Path("mangadex")
        test_dir.mkdir(exist_ok=True)
        try:
            # CREATE DVK
            dvk = Dvk()
            dvk.set_id("MDX770791-3")
            dvk.set_title("Randomphilia | Ch. 74 | Pg. 3")
            dvk.set_page_url("https://mangadex.cc/chapter/770791/3")
            dvk.set_artist("whatever")
            file = test_dir.joinpath(dvk.get_filename() + ".dvk")
            dvk.set_file(file.absolute())
            dvk.set_media_file("unimportant.png")
            dvk.write_dvk()
            # CHECK TITLE
            title_info = get_title_info("34326")
            chapters = get_chapters(title_info, language="French")
            dvk_handler = DvkHandler()
            dvk_handler.load_dvks([str(test_dir.absolute())])
            assert len(dvk_handler.get_paths()) == 1
            dvks = get_dvks(
                dvk_handler,
                chapters,
                False)
            assert len(dvks) == 9
            assert dvks[8].get_id() == "MDX770792-4"
            assert dvks[8].get_title() == "Randomphilia | Ch. 75 | Pg. 4"
            url = "https://s5.mangadex.org/data/2d60025d419442a4d56d58a7bbcdc6db/M4.jpg"
            assert dvks[8].get_direct_url() == url
            assert dvks[0].get_id() == "MDX770791-1"
            assert dvks[0].get_title() == "Randomphilia | Ch. 74 | Pg. 1"
            url = "https://s5.mangadex.org/data/dedabbdba2b1b69f76f299ee748402f8/k1.jpg"
            assert dvks[0].get_direct_url() == url
            # CHECK INVALID
            assert get_dvks(save=False) == []
            chapters = get_chapters()
            dvk_handler = DvkHandler()
            assert get_dvks(dvk_handler, save=False) == []
        finally:
            # REMOVE TEST FILES
            rmtree(test_dir.absolute())


if __name__ == "__main__":
    test_mangadex = TestMangadex()
    test_mangadex.test_all()
