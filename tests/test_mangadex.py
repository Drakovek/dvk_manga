import unittest
from dvk_archive.file.dvk import Dvk
from dvk_manga.mangadex import get_title_id
from dvk_manga.mangadex import get_title_info
from dvk_manga.mangadex import get_chapters


class TestMangadex(unittest.TestCase):
    """
    Unit tests for the mangadex.py module.
    """

    def test_get_title_num(self):
        """
        Tests the get_title_num function.
        """
        assert get_title_id() == ""
        assert get_title_id("www.differentsite.com") == ""
        assert get_title_id("mangadex.com/title/27153/") == ""
        assert get_title_id("www.mangadex.org/nope/27153/") == ""
        assert get_title_id("www.mangadex.org/title/invalid/") == ""
        assert get_title_id("mangadex.org/title/27152") == "27152"
        i = "www.mangadex.org/title/27153/jojo-s-bizarre-adventure"
        assert get_title_id(i) == "27153"

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
        desc = "English :&#10;A world where logic does not exist and anything "
        desc = desc + "is possible. The only limit is your imagination. "
        desc = desc + "Bite-sized comics with dry humor for the broken souls."
        desc = desc + "&#10;&#10;Un monde o&#249; la logique n&#8217;existe "
        desc = desc + "pas et o&#249; tout est possible. La seule limite est "
        desc = desc + "votre imagination. Des bandes dessin&#233;es mordues."
        assert dvk.get_description() == desc
        page_url = "https://mangadex.org/title/34326/randomphilia/"
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
        desc = "Second story arc of JoJo no Kimyou na Bouken series.&#10;&#10;"
        desc = desc + "Takes place in the 1930s, and follows the "
        desc = desc + "misadventures of Joseph Joestar, the grandson of "
        desc = desc + "Jonathan Joestar, as he fights vampires and ancient "
        desc = desc + "super beings with some help from a cybernetically-"
        desc = desc + "enhanced Nazi and an Italian man he has a lot in "
        desc = desc + "common with."
        assert dvk.get_description() == desc
        page_url = "https://mangadex.org/title/27152/jojo-s-bizarre-adventure-"
        page_url = page_url + "part-2-battle-tendency-official-colored/"
        assert dvk.get_page_url() == page_url

    def test_get_links(self):
        """
        Tests the get_links method.
        """
        # INVALID
        dvks = get_chapters()
        assert len(dvks) == 0
        dvk = Dvk()
        dvks = get_chapters(dvk)
        assert len(dvks) == 0
        dvk.set_page_url("https://mangadex.org")
        dvks = get_chapters(dvk)
        assert len(dvks) == 0
        # TITLE 1
        title = "JoJo's Bizarre Adventure Part 2 - "
        title = title + "Battle Tendency (Official Colored)"
        dvk.set_title(title)
        page_url = "https://mangadex.org/title/27152/jojo-s-bizarre-adventure-"
        page_url = page_url + "part-2-battle-tendency-official-colored/"
        dvk.set_page_url(page_url)
        dvk.set_artist("Araki Hirohiko")
        dvks = get_chapters(dvk, language="English")
        assert len(dvks) == 69
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency "
        title = title + "(Official Colored) | Vol. 7 Ch. 69 - The Comeback"
        assert dvks[0].get_title() == title
        assert dvks[0].get_artists() == ["Araki Hirohiko"]
        assert dvks[0].get_time() == "2018/01/18|19:08"
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency "
        title = title + "(Official Colored) | Vol. 4 Ch. 39 - Chasing the Red "
        title = title + "Stone to Swizerland"
        assert dvks[30].get_title() == title
        assert dvks[30].get_time() == "2018/01/18|18:44"
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official "
        title = title + "Colored) | Vol. 1 Ch. 1 - Joseph Joestar of New York"
        assert dvks[68].get_title() == title
        assert dvks[68].get_time() == "2018/01/18|16:44"
        dvks = get_chapters(dvk, language="Italian")
        assert len(dvks) == 26
        title = "JoJo's Bizarre Adventure Part 2 - Battle Tendency (Official "
        title = title + "Colored) | Vol. 3 Ch. 26 - La maledizione delle fedi"
        assert dvks[0].get_title() == title
        assert dvks[0].get_time() == "2019/07/31|16:16"
        # TITLE 2
        dvk.set_title("Randomphilia")
        page_url = "https://mangadex.org/title/34326/randomphilia/"
        dvk.set_page_url(page_url)
        dvks = get_chapters(dvk, language="English")
        assert len(dvks) == 0
        dvks = get_chapters(dvk, language="French")
        assert len(dvks) == 73
        assert dvks[0].get_title() == "Randomphilia | Ch. 73"
        assert dvks[0].get_time() == "2019/12/05|16:45"