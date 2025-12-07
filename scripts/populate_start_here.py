import os
import django
import sys

# Add backend to path
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')
django.setup()

from starthere_app.models import StartHerePage

def populate():
    print("Populating Start Here Page content...")
    
    content = """
    <p class="mb-4">Back in January of 2015 i compiled all the Twitter (now called "X") posts i had posted up to that point into an ebook which i made available on Amazon Kindle Unlimited.</p>

    <p class="mb-4">Since that time i have made innumerable posts on <a href="https://www.clmjournal.com/all-the-links" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">various social media platforms</a>. My vision for the Book of Tweets then became more ambitious: i wanted to create a LIVE site on which ALL of my posted thoughts could be published, read, searched and connected to each other.</p>

    <p class="mb-4">Having discovered <a href="https://obsidian.md" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">Obsidian.md</a>, i was excited to find a platform on which i could broadcast the wisdom i had collected to the world and immediately commenced to transfer the content of The Book of Tweets to an Obsidian vault created for that purpose…</p>

    <p class="mb-4">…there was just one small problem: <a href="https://obsidian.md/publish" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">Obsidian Publish</a> did not have critical features that the desktop version of Obsidian had inspired so much excitement in me.</p>

    <p class="mb-4">Years have come and gone…</p>

    <p class="mb-4">…and now I believe that, with the technology provided by the author of <a href="https://quartz.jzhao.xyz/" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">Quartz</a>, i now have all the components i need to see my dream come to fruition!</p>

    <p class="mb-4">So…here’s how to get started:</p>

    <h2 class="text-xl font-bold mt-6 mb-2">The Tables</h2>
    <p class="mb-4">The best place to start is with the tables. The tables will provide you easy and browsable lists of The Book of Thoughts (formerly The Book of Tweets) content. The Topic (magenta), Passage (light blue), Quote (bright yellow) and Thoughts (bright green) nodes are all color-coded. The Table nodes are not color coded because i intend to exclude them from the main (global) Graph View eventually.</p>

    <p class="mb-4">It should be noted that in my zeal to add entries continually, the tables are not always up to date; the Graph Views and search feature, however, are always current…so if you visit the page of any table its Graph should always display recently-added nodes. Likewise searches should always include the latest entries. Up till now I’ve always managed to update the tables once per week.</p>

    <p class="mb-4">Whether or not the sidebars to the left and right are visible is a function of how wide you’ve set the webpage in your browser; so I’m also going to list the Tables here…go ahead and select one!</p>

    <ul class="list-disc pl-5 mb-6 text-text-secondary">
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: Topics</a></li>
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: Thoughts</a></li>
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: Quotes</a></li>
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: Bible Passages</a></li>
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: RECENT (sorted by Last Modified)</a></li>
        <li><a href="#" class="text-blue-400 hover:text-blue-300">Table: MultiLingual (sorted by Last Modified)</a></li>
    </ul>

    <h2 class="text-xl font-bold mt-6 mb-2">The Tags</h2>
    <p class="mb-4">Tags are objects meant to make searching the increasingly vast ocean of The Book of Thoughts easier. Clicking on a tag in either a topic (‘#type/topic/L2’, for instance) or a thought (anything with a hashtag [’#’] in front of it) will take you to a page which will list every thought that tag is found in.</p>
    <p class="mb-4">NOTICE; I have removed the Social Tags column from The Thoughts Table (“table-THOUGHTS-MD-File.md”) so that the Graph View doesn’t repeat tags unnecessarily.</p>

    <h2 class="text-xl font-bold mt-6 mb-2">The Templates</h2>
    <p class="mb-4">I’m still learning the use of the Templater Obsidian plugin which, i’m sure, will enhance the features of The Book of Thoughts. Meanwhile, I’m employing (and, when necessary, updating) the following templates based on the core plugin:</p>
    <ul class="list-disc pl-5 mb-6 text-text-secondary">
        <li>topic</li>
        <li>thought</li>
        <li>quote</li>
        <li>passage</li>
    </ul>

    <h2 class="text-xl font-bold mt-6 mb-2">Graph View</h2>
    <p class="mb-4">The prime feature of this site is the Graph View, seen either at the top right or bottom of each page. What the Graph View displays is a function of each page’s content; that is, when you load the page for a topic, thought, quote or Bible Passage, Graph View switches its focus to that topic or thought!</p>
    <p class="mb-4">At the upper-right corner of the Graph View window there is a small icon; click on it and the Graph View will expand its size for easier navigation. You can always DRAG the content of the Graph View around to center on the area of your choice.</p>
    <p class="mb-4">If your mouse has a Scroll Button, you can use it to ZOOM in and out of the Graph View to better discover the lines that link objects as well as receive a clearer view of the objects themselves. Every topic will (eventually) be preceded by the word “topic;” every tag will be preceded by a hashtag (’#’); and everything else will probably be a Thought, Quote or Bible Passage meant to feed your soul and spirit with Wisdom!</p>
    <p class="mb-4">Also be aware that if you hover your pointer over a particular node, when you zoom in or out with your scroll bar that node will remain the center of the zoom!</p>
    <p class="mb-4">As in the Obsidian Desktop app, Every Topic (magenta), Passage (light blue), Quote (light yellow) and Thought (green) is color coded for easier navigation.</p>

    <h2 class="text-xl font-bold mt-6 mb-2">Donate</h2>
    <p class="mb-4">Wisdom is PRICELESS. Money will not save you from old age and death, but Wisdom will! If you find VALUE in the Wisdom presented at this site, <a href="https://clmjournal.com/contact" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">let me know</a>: my Cash App ID is <a href="https://cash.app/$Quasaur" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">@Quasaur</a>.</p>

    <h2 class="text-xl font-bold mt-6 mb-2">Roadmap</h2>
    <p class="mb-4">This is what i intend to accomplish in the next few years:</p>
    <ol class="list-decimal pl-5 mb-6 text-text-secondary">
        <li class="mb-2">The 85 Thoughts originally posted must have their notes edited…this might take a few weeks (COMPLETED).</li>
        <li class="mb-2">There are HUNDREDS of more tweets in the original Book of Tweets (667, to be exact); all of these must be added as well (IN-PROCESS).</li>
        <li class="mb-2">All of my social media posts across all platforms I am currently a member of will be added next (IN-PROCESS).</li>
        <li class="mb-2">I will also add quotes from my other <a href="https://www.clmjournal.com/books" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">nine books</a> (IN PROCESS).</li>
        <li class="mb-2">I will then add a new section/folder filled with the proverbs from the Biblical Texts of Ecclesiastes and Proverbs as well as wisdom literature from the entire Bible (IN-PROCESS).</li>
        <li class="mb-2">I will add multi-language support (English, Spanish, French, Hindi and Simplified Mandarin) to all Topics (Description), Thoughts, Quotes and Biblical Passages (IN-PROCESS).</li>
        <li class="mb-2">I’d like to add pagination to my tables so their growing contents don’t have to be displayed all at once, keeping page loading times reasonable (BEING RESEARCHED)</li>
    </ol>

    <h2 class="text-xl font-bold mt-6 mb-2">Preface to the First Edition</h2>
    <p class="mb-4"><a href="#" class="text-blue-400 hover:text-blue-300">BookOfTweets-Preface</a></p>

    <h2 class="text-xl font-bold mt-6 mb-2">Never Finished</h2>
    <p class="mb-4">I brought this site to a condition that, i believe, you will benefit from. This site is NOT finished…it will NEVER be finished, even after I’m dead. I promise you, however, that i will NEVER stop adding to it until i am dead.</p>

    <h2 class="text-xl font-bold mt-6 mb-2">About the Author</h2>
    <p class="mb-4"><a href="https://clmjournal.com/author" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300">About the Author</a></p>

    <h2 class="text-xl font-bold mt-6 mb-2">Latest Update</h2>
    <p class="mb-4">The most recent file(s) were created or updated between 16-Nov-2024 and 29-Nov-2024.</p>
    """
    
    page, created = StartHerePage.objects.get_or_create(pk=1)
    page.title = "Welcome to the Book of Wisdom!"
    page.subtitle = "Formerly 'The Book of Tweets: Proverbs for the Modern Age'"
    page.hero_image_url = "/images/start-here-hero.png"
    page.content = content
    page.save()
    
    print(f"Successfully {'created' if created else 'updated'} Start Here Page content.")

if __name__ == "__main__":
    populate()
