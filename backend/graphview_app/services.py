from topics_app.models import Topic
from thoughts_app.models import Thought
from quotes_app.models import Quote
from passages_app.models import Passage

class PostgresGraphService:
    """
    Service to generate graph data from Postgres database
    Replaces the Neo4j service for graph visualization
    """
    
    @staticmethod
    def get_graph_data():
        nodes = []
        links = []
        
        # 1. Fetch Topics
        # Only active topics
        topics = Topic.objects.filter(is_active=True)
        for topic in topics:
            nodes.append({
                'id': topic.neo4j_id,
                'name': topic.title,
                'type': 'TOPIC',
                'size': 20 + (5 - min(topic.level, 5)) * 2, # Larger for higher levels (root=0)
                'labels': ['Topic'],
                'level': topic.level
            })
            
            # Link to parent (stored as string ID in Postgres)
            if topic.parent_id:
                links.append({
                    'source': topic.neo4j_id,
                    'target': topic.parent_id,
                    'type': 'HAS_PARENT'
                })

        # 2. Fetch Thoughts
        thoughts = Thought.objects.filter(is_active=True)
        for thought in thoughts:
            nodes.append({
                'id': thought.neo4j_id,
                'name': thought.title,
                'type': 'THOUGHT',
                'size': 15,
                'labels': ['Thought'],
                'level': thought.level
            })
            
            # Link to parent (stored as string ID)
            if thought.parent_id:
                links.append({
                    'source': thought.neo4j_id,
                    'target': thought.parent_id,
                    'type': 'HAS_PARENT'
                })

        # 3. Fetch Quotes
        # Select related parent (Topic) to avoid N+1
        quotes = Quote.objects.filter(is_active=True).select_related('parent')
        for quote in quotes:
            nodes.append({
                'id': quote.neo4j_id,
                'name': quote.title,
                'type': 'QUOTE',
                'size': 10,
                'labels': ['Quote'],
                'level': quote.level
            })
            
            # Link to parent Topic
            if quote.parent:
                links.append({
                    'source': quote.neo4j_id,
                    'target': quote.parent.neo4j_id,
                    'type': 'HAS_QUOTE'
                })

        # 4. Fetch Passages
        passages = Passage.objects.filter(is_active=True).select_related('parent')
        for passage in passages:
            nodes.append({
                'id': passage.neo4j_id,
                'name': passage.title,
                'type': 'PASSAGE',
                'size': 10,
                'labels': ['Passage'],
                'level': passage.level
            })
            
            # Link to parent Topic
            if passage.parent:
                links.append({
                    'source': passage.neo4j_id,
                    'target': passage.parent.neo4j_id,
                    'type': 'HAS_PASSAGE'
                })
                
        return {
            'nodes': nodes,
            'links': links
        }
