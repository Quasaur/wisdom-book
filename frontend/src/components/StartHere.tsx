import React from 'react';

const StartHere: React.FC = () => {
    return (
        <div className="card !p-0 overflow-hidden">
            <img src="/images/start-here-hero.png" alt="Start Here Hero" className="w-[40%] h-auto mx-auto block mt-[5px]" />
            <div className="p-12">
                <h1>Welcome to the Book of Wisdom!</h1>
                <p><em>Formerly "The Book of Tweets: Proverbs for the Modern Age"</em></p>

                <p>Back in January of 2015 i compiled all the Twitter (now called "X") posts i had posted up to that
                    point into an ebook which i made available on Amazon Kindle Unlimited.</p>

                <p>Since that time i have made innumerable posts on various social media platforms. My vision for the
                    Book of Thoughts then became more ambitious: i wanted to create a LIVE site on which ALL of my
                    posted thoughts could be published, read, searched and connected to each other.</p>

                <p>Having discovered Obsidian.md, i was excited to find a platform on which i could broadcast the wisdom
                    i had collected to the world...</p>

                <h2>The Tables</h2>
                <p>The best place to start is with the tables. The tables will provide you easy and browsable lists of
                    The Book of Thoughts content. The Topic (magenta), Passage (light blue), Quote (bright yellow) and
                    Thoughts (bright green) nodes are all color-coded.</p>

                <ul className="list-disc pl-5 mb-6 text-text-secondary">
                    <li><a href="#">Table: Topics</a></li>
                    <li><a href="#">Table: Thoughts</a></li>
                    <li><a href="#">Table: Quotes</a></li>
                    <li><a href="#">Table: Bible Passages</a></li>
                </ul>

                <h2>Graph View</h2>
                <p>The prime feature of this site is the Graph View. What the Graph View displays is a function of each
                    page's content; that is, when you load the page for a topic, thought, quote or Bible Passage, Graph
                    View switches its focus to that topic or thought!</p>
            </div>
        </div>
    );
};

export default StartHere;
