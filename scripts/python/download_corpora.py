from pathlib import Path
import csv
import re
import time
import requests

OUT_DIR = Path("texts/human")
MANIFEST = OUT_DIR / "metadata.csv"
# create the directory if it does not exist
try:
    OUT_DIR.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print(f"The target directory {OUT_DIR} exists")

TEXTS = [
    #############
    ## ENGLISH ##
    #############

    ## Poetry
    # 13th century
#    {"language":"english","genre":"poetry","subgenre":"religious_poetry","title":"ormulum","author":"Orm","year":1200,"url":"https://archive.org/details/ormulumwithnotes01ormmuoft"},
    # {"language":"english","genre":"poetry","subgenre":"debate_poetry","title":"the_owl_and_the_nightingale","author":"Anonymous","year":1225,"url":"https://www.gutenberg.org/ebooks/2489.txt.utf-8"},
#    {"language":"english","genre":"poetry","subgenre":"lyric","title":"harley_lyrics","author":"Anonymous","year":1250,"url":"https://archive.org/details/harleylyricsxx"},
#    {"language":"english","genre":"poetry","subgenre":"romance","title":"king_horn","author":"Anonymous","year":1225,"url":"https://archive.org/details/kinghornflorisce00halluoft"},
#    {"language":"english","genre":"poetry","subgenre":"romance","title":"havelok_the_dane","author":"Anonymous","year":1280,"url":"https://www.gutenberg.org/ebooks/349.txt.utf-8"},
#    {"language":"english","genre":"poetry","subgenre":"romance","title":"floris_and_blaunchflur","author":"Anonymous","year":1250,"url":"https://archive.org/details/kinghornflorisce00halluoft"},
#    {"language":"english","genre":"poetry","subgenre":"saints_life","title":"south_english_legendary","author":"Anonymous","year":1270,"url":"https://archive.org/details/cu31924013113523"},
#    {"language":"english","genre":"prose","subgenre":"religious_instruction","title":"ancrene_wisse_prose","author":"Anonymous","year":1225,"url":"https://archive.org/details/ancrenewisser00morruoft"},
#    {"language":"english","genre":"prose","subgenre":"homily","title":"kentish_sermons","author":"Anonymous","year":1275,"url":"https://archive.org/details/oldenglishhomili00morruoft"},

    # 14th century
    {"language":"english","genre":"poetry","subgenre":"narrative_poetry","title":"troilus_and_criseyde","author":"Geoffrey Chaucer","year":1385,"url":"https://www.gutenberg.org/ebooks/257.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"allegorical_poetry","title":"piers_plowman_vol_1","author":"William Langland","year":1377,"url":"https://www.gutenberg.org/ebooks/43660.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"allegorical_poetry","title":"piers_plowman_vol_2","author":"William Langland","year":1377,"url":"https://www.gutenberg.org/ebooks/43661.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"romance","title":"sir_gawain_and_the_green_knight","author":"Anonymous (Pearl Poet)","year":1390,"url":"https://www.gutenberg.org/ebooks/14568.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"confessional_poetry","title":"confessio_amantis","author":"John Gower","year":1393,"url":"https://www.gutenberg.org/cache/epub/266/pg266.txt"},

    # 15th century
    {"language":"english","genre":"poetry","subgenre":"courtly_poetry","title":"love_poems","author":"Charles d'Orléans","year":1450,"url":"https://archive.org/stream/fortunesstabilne00charuoft/fortunesstabilne00charuoft_djvu.txt"},
    {"language":"english","genre":"poetry","subgenre":"allegorical_poetry","title":"the_temple_of_glass","author":"John Lydgate","year":1420,"url":"https://www.gutenberg.org/cache/epub/29552/pg29552.txt"},
    {"language":"english","genre":"poetry","subgenre":"dream_vision","title":"the_fall_of_princes","author":"John Lydgate","year":1431,"url":"https://archive.org/stream/fallofprincesedi04lydguoft/fallofprincesedi04lydguoft_djvu.txt"},
    {"language":"english","genre":"poetry","subgenre":"ballad","title":"a_lytel_geste_of_robin_hode","author":"Anonymous","year":1495,"url":"https://archive.org/stream/alytellgesterob00rimbgoog/alytellgesterob00rimbgoog_djvu.txt"},

    # 16th century
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"songs_and_sonnets","author":"Sir Thomas Wyatt","year":1557,"url":"https://archive.org/stream/poetryofsirthoma031860mbp/poetryofsirthoma031860mbp_djvu.txt"},
#    {"language":"english","genre":"poetry","subgenre":"anthology","title":"tottels_miscellany","author":"Richard Tottel (ed.)","year":1557,"url":"https://www.gutenberg.org/ebooks/40924.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"pastoral","title":"the_shepheardes_calendar","author":"Edmund Spenser","year":1579,"url":"https://www.gutenberg.org/ebooks/3481.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"epic","title":"the_faerie_queene","author":"Edmund Spenser","year":1590,"url":"https://www.gutenberg.org/ebooks/15272.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"narrative_poetry","title":"venus_and_adonis","author":"William Shakespeare","year":1593,"url":"https://www.gutenberg.org/ebooks/1045.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"narrative_poetry","title":"the_rape_of_lucrece","author":"William Shakespeare","year":1594,"url":"https://www.gutenberg.org/ebooks/1047.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"sonnet_sequence","title":"amoretti","author":"Edmund Spenser","year":1595,"url":"https://www.gutenberg.org/ebooks/35889.txt.utf-8"},

    # 17th century
    {"language":"english","genre":"poetry","subgenre":"epic","title":"paradise_lost","author":"John Milton","year":1667,"url":"https://www.gutenberg.org/ebooks/26.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"shakespeare_sonnets","author":"William Shakespeare","year":1609,"url":"https://www.gutenberg.org/ebooks/1041.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"metaphysical","title":"john_donne_poems","author":"John Donne","year":1633,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},

    # 18th century
    {"language":"english","genre":"poetry","subgenre":"mock_epic","title":"rape_of_the_lock","author":"Alexander Pope","year":1712,"url":"https://www.gutenberg.org/ebooks/9800.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"coleridge_poems","author":"Samuel Taylor Coleridge","year":1798,"url":"https://www.gutenberg.org/ebooks/9622.txt.utf-8"},

    # 19th century
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"wordsworth_selected_poems","author":"William Wordsworth","year":1807,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"keats_poems","author":"John Keats","year":1820,"url":"https://www.gutenberg.org/ebooks/23684.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"shelley_poems","author":"Percy Bysshe Shelley","year":1820,"url":"https://www.gutenberg.org/ebooks/4800.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"narrative_poetry","title":"byron_childe_harold","author":"Lord Byron","year":1812,"url":"https://www.gutenberg.org/ebooks/5131.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"dramatic_monologue","title":"robert_browning_poems","author":"Robert Browning","year":1855,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"tennyson_poems","author":"Alfred Tennyson","year":1842,"url":"https://www.gutenberg.org/ebooks/5690.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"christina_rossetti_poems","author":"Christina Rossetti","year":1862,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"free_verse","title":"leaves_of_grass","author":"Walt Whitman","year":1855,"url":"https://www.gutenberg.org/ebooks/1322.txt.utf-8"},
    {"language":"english","genre":"poetry","subgenre":"lyric","title":"edgar_allan_poe_poems","author":"Edgar Allan Poe","year":1845,"url":"https://www.gutenberg.org/ebooks/50852.txt.utf-8"},

    ## Prose
    # 13th century
    {"language":"english","genre":"prose","subgenre":"religious_instruction","title":"ancrene_wisse","author":"Anonymous","year":1225,"url":"https://archive.org/details/ancrenewisser00morruoft"},
    {"language":"english","genre":"prose","subgenre":"homily","title":"old_english_homilies_second_series","author":"Anonymous","year":1225,"url":"https://archive.org/details/oldenglishhomili00morruoft"},
    {"language":"english","genre":"prose","subgenre":"saints_lives","title":"katherine_group","author":"Anonymous","year":1225,"url":"https://archive.org/details/katherinegroup00dobsuoft"},
    {"language":"english","genre":"prose","subgenre":"religious_prose","title":"hali_meidenhad","author":"Anonymous","year":1230,"url":"https://archive.org/details/katherinegroup00dobsuoft"},
    {"language":"english","genre":"prose","subgenre":"saints_lives","title":"seinte_katerine","author":"Anonymous","year":1225,"url":"https://archive.org/details/katherinegroup00dobsuoft"},
    {"language":"english","genre":"prose","subgenre":"saints_lives","title":"seinte_margarete","author":"Anonymous","year":1225,"url":"https://archive.org/details/katherinegroup00dobsuoft"},
    {"language":"english","genre":"prose","subgenre":"saints_lives","title":"seinte_iuliene","author":"Anonymous","year":1225,"url":"https://archive.org/details/katherinegroup00dobsuoft"},
    {"language":"english","genre":"prose","subgenre":"devotional_prose","title":"wohunge_of_oure_lauerd","author":"Anonymous","year":1250,"url":"https://archive.org/details/wohungeofourelau00anon"},
    {"language":"english","genre":"prose","subgenre":"sermon","title":"kentish_sermons","author":"Anonymous","year":1275,"url":"https://archive.org/details/oldenglishhomili00morruoft"},
    {"language":"english","genre":"prose","subgenre":"religious_instruction","title":"ayenbite_of_inwyt","author":"Dan Michel of Northgate","year":1340,"url":"https://archive.org/details/ayenbiteofinwyt00michuoft"},

    # 14th century
   {"language":"english","genre":"prose","subgenre":"religious_mysticism","title":"the_fire_of_love","author":"Richard Rolle","year":1340,"url":"https://www.gutenberg.org/ebooks/16358.txt.utf-8"},
   {"language":"english","genre":"prose","subgenre":"devotional_prose","title":"the_pricke_of_conscience","author":"Richard Rolle (attrib.)","year":1340,"url":"https://archive.org/details/prickeofconscien00rolluoft"},
   {"language":"english","genre":"prose","subgenre":"religious_instruction","title":"ayenbite_of_inwyt","author":"Dan Michel of Northgate","year":1340,"url":"https://archive.org/details/ayenbiteofinwyt00michuoft"},
   {"language":"english","genre":"prose","subgenre":"travel","title":"the_voiage_and_travaile_of_sir_john_maundeville","author":"John Mandeville (attrib.)","year":1356,"url":"https://www.gutenberg.org/ebooks/782.txt.utf-8"},
   {"language":"english","genre":"prose","subgenre":"religious_mysticism","title":"revelations_of_divine_love","author":"Julian of Norwich","year":1395,"url":"https://www.gutenberg.org/ebooks/52958.txt.utf-8"},
   {"language":"english","genre":"prose","subgenre":"medical_prose","title":"rosa_anglica","author":"John of Gaddesden","year":1320,"url":"https://archive.org/details/rosaanglica00gadduoft"},
   {"language":"english","genre":"prose","subgenre":"chronicle","title":"polychronicon_translation","author":"John Trevisa","year":1387,"url":"https://archive.org/details/polychroniconran04higd"},
   {"language":"english","genre":"prose","subgenre":"scientific_prose","title":"trevisa_on_properties_of_things","author":"John Trevisa","year":1398,"url":"https://archive.org/details/trevisaonpropert00bartuoft"},
   {"language":"english","genre":"prose","subgenre":"religious_prose","title":"the_cloud_of_unknowing","author":"Anonymous","year":1390,"url":"https://archive.org/details/cloudofunknowing00unknuoft"},
   {"language":"english","genre":"prose","subgenre":"devotional_prose","title":"the_book_of_privy_counselling","author":"Anonymous","year":1390,"url":"https://archive.org/details/cloudofunknowing00unknuoft"},

    # 15th century
    {"language":"english","genre":"prose","subgenre":"arthurian_romance","title":"le_morte_darthur","author":"Thomas Malory","year":1485,"url":"https://www.gutenberg.org/ebooks/1251.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"autobiography","title":"the_book_of_margery_kempe","author":"Margery Kempe","year":1430,"url":"https://www.gutenberg.org/ebooks/32263.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"religious_mysticism","title":"the_book_of_showings","author":"Julian of Norwich","year":1413,"url":"https://www.gutenberg.org/ebooks/52958.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"travel","title":"the_voiage_and_travaile_of_sir_john_maundeville","author":"John Mandeville (attrib.)","year":1400,"url":"https://www.gutenberg.org/ebooks/782.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"arthurian_romance","title":"le_morte_darthur","author":"Thomas Malory","year":1485,"url":"https://www.gutenberg.org/ebooks/1251.txt.utf-8"},

    # 16th century
    {"language":"english","genre":"prose","subgenre":"utopian_fiction","title":"utopia","author":"Thomas More","year":1516,"url":"https://www.gutenberg.org/ebooks/2130.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"travel","title":"the_principal_navigations","author":"Richard Hakluyt","year":1598,"url":"https://www.gutenberg.org/ebooks/9326.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"religious_prose","title":"the_book_of_common_prayer","author":"Church of England","year":1559,"url":"https://www.gutenberg.org/ebooks/61273.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"history","title":"chronicles_of_england_scotland_and_ireland","author":"Raphael Holinshed","year":1577,"url":"https://archive.org/details/holinshedschroni01holiuoft"},

    # 17th century
    {"language":"english","genre":"prose","subgenre":"essay","title":"essays_or_counsels_civil_and_moral","author":"Francis Bacon","year":1625,"url":"https://www.gutenberg.org/ebooks/575.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"religious_prose","title":"devotions_upon_emergent_occasions","author":"John Donne","year":1624,"url":"https://www.gutenberg.org/ebooks/23772.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"philosophy","title":"leviathan","author":"Thomas Hobbes","year":1651,"url":"https://www.gutenberg.org/ebooks/3207.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"science","title":"novum_organum","author":"Francis Bacon","year":1620,"url":"https://www.gutenberg.org/ebooks/45988.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"science","title":"micrographia","author":"Robert Hooke","year":1665,"url":"https://archive.org/details/micrographiaorso00hook"},
    {"language":"english","genre":"prose","subgenre":"history","title":"history_of_the_rebellion","author":"Edward Hyde","year":1702,"url":"https://archive.org/details/historyofrebelli01clar"},
    {"language":"english","genre":"prose","subgenre":"diary","title":"the_diary_of_samuel_pepys","author":"Samuel Pepys","year":1660,"url":"https://www.gutenberg.org/ebooks/4200.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"spiritual_autobiography","title":"grace_abounding_to_the_chief_of_sinners","author":"John Bunyan","year":1666,"url":"https://www.gutenberg.org/ebooks/654.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"travel","title":"a_new_voyage_round_the_world","author":"William Dampier","year":1697,"url":"https://www.gutenberg.org/ebooks/15675.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"religious_prose","title":"pilgrims_progress","author":"John Bunyan","year":1678,"url":"https://www.gutenberg.org/ebooks/131.txt.utf-8"},

    # 18th century
    {"language":"english","genre":"prose","subgenre":"science","title":"opticks","author":"Isaac Newton","year":1704,"url":"https://www.gutenberg.org/ebooks/33504.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"travel_satire","title":"gullivers_travels","author":"Jonathan Swift","year":1726,"url":"https://www.gutenberg.org/ebooks/829.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"robinson_crusoe","author":"Daniel Defoe","year":1719,"url":"https://www.gutenberg.org/ebooks/521.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"tom_jones","author":"Henry Fielding","year":1749,"url":"https://www.gutenberg.org/ebooks/6593.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"memoir","title":"autobiography_benjamin_franklin","author":"Benjamin Franklin","year":1791,"url":"https://www.gutenberg.org/ebooks/20203.txt.utf-8"},

    # 19th century
    {"language":"english","genre":"prose","subgenre":"novel","title":"sense_and_sensibility","author":"Jane Austen","year":1811,"url":"https://www.gutenberg.org/ebooks/161.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"pride_and_prejudice","author":"Jane Austen","year":1813,"url":"https://www.gutenberg.org/ebooks/1342.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"frankenstein","author":"Mary Shelley","year":1818,"url":"https://www.gutenberg.org/ebooks/84.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"essay","title":"confessions_english_opium_eater","author":"Thomas De Quincey","year":1821,"url":"https://www.gutenberg.org/ebooks/2040.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"jane_eyre","author":"Charlotte Brontë","year":1847,"url":"https://www.gutenberg.org/ebooks/1260.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"david_copperfield","author":"Charles Dickens","year":1850,"url":"https://www.gutenberg.org/ebooks/766.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"essay","title":"walden","author":"Henry David Thoreau","year":1854,"url":"https://www.gutenberg.org/ebooks/205.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"great_expectations","author":"Charles Dickens","year":1861,"url":"https://www.gutenberg.org/ebooks/1400.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"middlemarch","author":"George Eliot","year":1871,"url":"https://www.gutenberg.org/ebooks/145.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"treasure_island","author":"Robert Louis Stevenson","year":1883,"url":"https://www.gutenberg.org/ebooks/120.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"dracula","author":"Bram Stoker","year":1897,"url":"https://www.gutenberg.org/ebooks/345.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"heart_of_darkness","author":"Joseph Conrad","year":1899,"url":"https://www.gutenberg.org/ebooks/219.txt.utf-8"},

    # 20th century
    {"language":"english","genre":"prose","subgenre":"novel","title":"the_secret_agent","author":"Joseph Conrad","year":1907,"url":"https://www.gutenberg.org/ebooks/974.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"the_wind_in_the_willows","author":"Kenneth Grahame","year":1908,"url":"https://www.gutenberg.org/ebooks/289.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"howards_end","author":"E. M. Forster","year":1910,"url":"https://www.gutenberg.org/ebooks/2946.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"the_secret_garden","author":"Frances Hodgson Burnett","year":1911,"url":"https://www.gutenberg.org/ebooks/17396.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"sons_and_lovers","author":"D. H. Lawrence","year":1913,"url":"https://www.gutenberg.org/ebooks/217.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"dubliners","author":"James Joyce","year":1914,"url":"https://www.gutenberg.org/ebooks/2814.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"a_portrait_of_the_artist_as_a_young_man","author":"James Joyce","year":1916,"url":"https://www.gutenberg.org/ebooks/4217.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"memoir","title":"goodbye_to_all_that","author":"Robert Graves","year":1929,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"the_return_of_the_soldier","author":"Rebecca West","year":1918,"url":"https://www.gutenberg.org/ebooks/37189.txt.utf-8"},
    {"language":"english","genre":"prose","subgenre":"novel","title":"the_age_of_innocence","author":"Edith Wharton","year":1920,"url":"https://www.gutenberg.org/ebooks/541.txt.utf-8"}
]
    ## FRENCH
#    {"language":"french","genre":"poetry","subgenre":"fables","title":"fables_lafontaine","author":"Jean de La Fontaine","year":1668,"url":"https://www.gutenberg.org/ebooks/56098.txt.utf-8"},
#    {"language":"french","genre":"prose","subgenre":"essay","title":"essais_montaigne","author":"Michel de Montaigne","year":1580,"url":"https://www.gutenberg.org/ebooks/3600.txt.utf-8"},
#    {"language":"french","genre":"prose","subgenre":"novel","title":"candide","author":"Voltaire","year":1759,"url":"https://www.gutenberg.org/ebooks/19942.txt.utf-8"},
#    {"language":"french","genre":"prose","subgenre":"novel","title":"bel_ami","author":"Guy de Maupassant","year":1885,"url":"https://www.gutenberg.org/ebooks/11670.txt.utf-8"},

    # SPANISH
#    {"language":"spanish","genre":"poetry","subgenre":"lyric","title":"rimas_leyendas","author":"Gustavo Adolfo Bécquer","year":1871,"url":"https://www.gutenberg.org/ebooks/10814.txt.utf-8"},
#    {"language":"spanish","genre":"prose","subgenre":"novel","title":"lazarillo_de_tormes","author":"Anonymous","year":1554,"url":"https://www.gutenberg.org/ebooks/5346.txt.utf-8"},
#    {"language":"spanish","genre":"prose","subgenre":"essay","title":"ensayos_unamuno","author":"Miguel de Unamuno","year":1900,"url":"https://www.gutenberg.org/ebooks/various.txt.utf-8"},

    # GERMAN
#    {"language":"german","genre":"poetry","subgenre":"drama","title":"faust","author":"Johann Wolfgang von Goethe","year":1808,"url":"https://www.gutenberg.org/ebooks/2229.txt.utf-8"},
#    {"language":"german","genre":"prose","subgenre":"novella","title":"kleist_michael_kohlhaas","author":"Heinrich von Kleist","year":1810,"url":"https://www.gutenberg.org/ebooks/23342.txt.utf-8"},
#    {"language":"german","genre":"prose","subgenre":"novel","title":"siddhartha","author":"Hermann Hesse","year":1922,"url":"https://www.gutenberg.org/ebooks/2500.txt.utf-8"},

    # ITALIAN
#    {"language":"italian","genre":"poetry","subgenre":"epic","title":"orlando_furioso","author":"Ludovico Ariosto","year":1516,"url":"https://www.gutenberg.org/ebooks/615.txt.utf-8"},
#    {"language":"italian","genre":"poetry","subgenre":"epic_poetry","title":"divina_commedia","author":"Dante Alighieri","year":1320,"url":"https://www.gutenberg.org/ebooks/1000.txt.utf-8"},
#    {"language":"italian","genre":"prose","subgenre":"novel","title":"pinocchio","author":"Carlo Collodi","year":1883,"url":"https://www.gutenberg.org/ebooks/500.txt.utf-8"},

    # LATIN
 #   {"language":"latin","genre":"poetry","subgenre":"epic","title":"aeneid","author":"Virgil","year":-19,"url":"https://www.gutenberg.org/ebooks/227.txt.utf-8"},
 #   {"language":"latin","genre":"prose","subgenre":"philosophy","title":"meditations_marcus_aurelius_latin","author":"Marcus Aurelius","year":180,"url":"https://www.gutenberg.org/ebooks/2680.txt.utf-8"},
#]

def clean_gutenberg(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    start = re.search(
        r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .*?\*\*\*",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if start:
        text = text[start.end():]

    end = re.search(
        r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .*?\*\*\*",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if end:
        text = text[:end.start()]

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def download_text(item):
    folder = OUT_DIR / item["language"] / item["genre"]
    folder.mkdir(parents=True, exist_ok=True)

    out_path = folder / f"{item['title']}.txt"

    print(f"Downloading {item['language']}/{item['genre']}/{item['title']}")

    try:
        r = requests.get(item["url"], timeout=40)
        r.raise_for_status()
    except Exception as e:
        print(f"FAILED: {item['title']} -> {e}")
        return None

    cleaned = clean_gutenberg(r.text)


    for index, text in enumerate(cleaned):
        out_path.write_text(cleaned, encoding="utf-8")

    word_count = len(cleaned.split())

    return {
        **item,
        "path": str(out_path),
        "word_count": word_count,
    }

def main():
    rows = []

    for item in TEXTS:
        result = download_text(item)
        if result:
            rows.append(result)
            print(f"Saved {result['path']} | {result['word_count']:,} words")
        time.sleep(2)

    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "language",
                "genre",
                "title",
                "author",
                "year",
                "url",
                "path",
                "word_count",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nMetadata saved to {MANIFEST}")

if __name__ == "__main__":
    main()

