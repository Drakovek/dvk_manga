import unittest
from dvk_manga.mangadex import get_title_id
from dvk_manga.mangadex import get_title_info


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
        dvk = get_title_info("90000000000")
        assert dvk.get_title() is None
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
