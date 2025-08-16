I'm on MACOS Sequoia; I'm setting up GitHub Copilot Pro, the Neo4j AuraDB (through API calls using the neo4j_driver service/library), Tailwind CSS, Visual Studio Code (VSCode) and git to develop an online Book of Wisdom website using a Django framework-based backend with a React Framework frontend?

I have an existing account on GitHub as Quasaur using the email address devcalvinlm@gmail.com .

I'm include the GitHub CoPilot extension(s) for VSCode which will allows me to interact with GPT-5 from within VSCode.

An existing Neo4j AuraDB will provide data to Django web project through the neo4_driver library. D3.js will provide graph visualization of the data downloaded from the AuraDB Source.

The Django project folder will be named "wisdom-book". I don't want a "wisdom-book-project" folder in the "wisdom-book/backend" folder; the project folder will be "wisdom-book".

The Django apps developed in the project will be named:

- starthere_app (for the Home page)
neo4j_app (a backend app for querying the AuraDB; this app will have no views of its own, but will supply AuraDB data to the - other apps)
graphview_app (for displaying a D3.js view of the entire contents - of the AuraDB; will be displayed on the React side panel menu)
topics_app (for accessing and displaying the TOPIC nodes in the - AuraDB; will be displayed on the React side panel menu)
thoughts_app (for accessing and displaying the THOUGHT nodes in - the AuraDB; will be displayed on the React side panel menu)
quotes_app (for accessing and displaying the QUOTE nodes in the - AuraDB; will be displayed on the React side panel menu)
passages_app (for accessing and displaying the PASSAGE nodes in - the AuraDB; will be displayed on the React side panel menu)
tags_app (for accessing displaying and searching for tag arrays contained in TOPIC, THOUGHT, QUOTE and PASSAGE nodes in the AuraDB; each tag array contains five tags; will be displayed on - the React side panel menu)
donate_app (for accepting donations and / or subscriptions from visitors and subscribers to the site; will be displayed on the - React side panel menu)
Each of these Django apps in the project (with the exception of neo4j_app, which is a backend app) will appear as a menu item on a left sidebar menu which will appear on all pages included in - the Django project.

NOTE: I only want to use GPT-5 to develop the Django project; I do not want use GPT-5 in the Django project's code.

The project folder is named "wisdom-book" and not "wisdom-book-project" and that the backend and frontend folders are named "backend" and "frontend" respectively, for simplicity.