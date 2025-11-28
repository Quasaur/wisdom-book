import React from 'react';

const StartHere: React.FC = () => {
    return (
        <div className="bg-card-bg rounded-2xl p-12 shadow-md mb-6">
            <h1 className="text-4xl font-normal mb-4 leading-tight">Welcome to the Book of Thoughts</h1>
            <p className="text-base leading-relaxed text-text-secondary mb-6"><em>Formerly "The Book of Tweets: Proverbs for the Modern Age"</em></p>

            <p className="text-base leading-relaxed text-text-secondary mb-6">Back in January of 2015 i compiled all the Twitter (now called "X") posts i had posted up to that
                point into an ebook which i made available on Amazon Kindle Unlimited.</p>

            <p className="text-base leading-relaxed text-text-secondary mb-6">Since that time i have made innumerable posts on various social media platforms. My vision for the
                Book of Thoughts then became more ambitious: i wanted to create a LIVE site on which ALL of my
                posted thoughts could be published, read, searched and connected to each other.</p>

            <p className="text-base leading-relaxed text-text-secondary mb-6">Having discovered Obsidian.md, i was excited to find a platform on which i could broadcast the wisdom
                i had collected to the world...</p>

            <h2 className="text-2xl font-normal mt-8 mb-4 text-text-primary">The Tables</h2>
            <p className="text-base leading-relaxed text-text-secondary mb-6">The best place to start is with the tables. The tables will provide you easy and browsable lists of
                The Book of Thoughts content. The Topic (magenta), Passage (light blue), Quote (bright yellow) and
                Thoughts (bright green) nodes are all color-coded.</p>

            <ul className="list-disc pl-5 mb-6 text-text-secondary">
                <li><a href="#" className="text-accent no-underline hover:underline">Table: Topics</a></li>
                <li><a href="#" className="text-accent no-underline hover:underline">Table: Thoughts</a></li>
                <li><a href="#" className="text-accent no-underline hover:underline">Table: Quotes</a></li>
                <li><a href="#" className="text-accent no-underline hover:underline">Table: Bible Passages</a></li>
            </ul>

            <h2 className="text-2xl font-normal mt-8 mb-4 text-text-primary">Graph View</h2>
            <p className="text-base leading-relaxed text-text-secondary mb-6">The prime feature of this site is the Graph View. What the Graph View displays is a function of each
                page's content; that is, when you load the page for a topic, thought, quote or Bible Passage, Graph
                View switches its focus to that topic or thought!</p>
        </div>
    );
};

export default StartHere;
