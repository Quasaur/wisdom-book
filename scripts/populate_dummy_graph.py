import os
import sys
import random

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')

import django
django.setup()

from neo4j_app.neo4j_service import neo4j_service

def populate_dummy_data():
    print("Populating Neo4j with dummy data...")
    try:
        # Create Topics
        topics = ["Wisdom", "Knowledge", "Understanding", "Life", "Universe"]
        for t in topics:
            # Create Topic with description property
            query = """
            MERGE (t:TOPIC {name: $name})
            SET t.alias = $name, 
                t.level = 1, 
                t.tags = ['dummy'],
                t.description = 'This is a description for ' + $name + '.'
            """
            neo4j_service.run_query(query, {"name": t}, write=True)
            
            # Create linked DESCRIPTION node (as used by some services)
            desc_query = """
            MATCH (t:TOPIC {name: $name})
            MERGE (d:DESCRIPTION {name: 'desc.' + $name})
            SET d.en_content = 'Detailed content description for ' + $name + '.',
                d.en_title = $name + ' Description',
                d.es_content = 'Descripción detallada del contenido para ' + $name + '.',
                d.es_title = 'Descripción de ' + $name,
                d.fr_content = 'Description détaillée du contenu pour ' + $name + '.',
                d.fr_title = 'Description de ' + $name,
                d.hi_content = $name + ' का विस्तृत विवरण।',
                d.hi_title = $name + ' विवरण',
                d.zh_content = $name + ' 的详细内容描述。',
                d.zh_title = $name + ' 描述'
            MERGE (t)-[:HAS_DESCRIPTION]->(d)
            """
            neo4j_service.run_query(desc_query, {"name": t}, write=True)
            print(f"Created topic: {t} with description")

        # Create Thoughts connected to Topics
        thoughts = [
            ("Wisdom is power", "Wisdom"),
            ("Knowledge is knowing", "Knowledge"),
            ("Understanding is deep", "Understanding"),
            ("Life is a journey", "Life"),
            ("The Universe is vast", "Universe")
        ]
        
        for text, topic in thoughts:
            query = """
            MATCH (t:TOPIC {name: $topic})
            MERGE (th:THOUGHT {name: $text})
            SET th.alias = $text, th.level = 2, th.tags = ['dummy', 'thought']
            MERGE (th)-[:BELONGS_TO]->(t)
            """
            neo4j_service.run_query(query, {"text": text, "topic": topic}, write=True)
            print(f"Created thought: '{text}' linked to {topic}")

        print("Dummy data population complete.")
    except Exception as e:
        print(f"Error populating dummy data: {e}")

if __name__ == "__main__":
    populate_dummy_data()
