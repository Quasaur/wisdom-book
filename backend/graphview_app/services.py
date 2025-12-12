from topics_app.models import Topic, Description
from thoughts_app.models import Thought, Content
from quotes_app.models import Quote, QuoteContent
from passages_app.models import Passage, PassageContent

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
        topics = Topic.objects.filter(is_active=True).prefetch_related('descriptions')
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

            # Fetch Topic Descriptions
            for desc in topic.descriptions.all():
                nodes.append({
                    'id': desc.neo4j_id,
                    'name': f"Desc: {topic.title}",
                    'type': 'DESCRIPTION',
                    'size': 8,
                    'labels': ['Description']
                })
                links.append({
                    'source': desc.neo4j_id,
                    'target': topic.neo4j_id,
                    'type': 'HAS_DESCRIPTION'
                })

        # 2. Fetch Thoughts
        thoughts = Thought.objects.filter(is_active=True).prefetch_related('contents')
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
            
            # Fetch Thought Content
            for content in thought.contents.all():
                nodes.append({
                    'id': content.neo4j_id,
                    'name': f"Content: {thought.title}",
                    'type': 'CONTENT',
                    'size': 8,
                    'labels': ['Content']
                })
                links.append({
                    'source': content.neo4j_id,
                    'target': thought.neo4j_id,
                    'type': 'HAS_CONTENT'
                })

        # 3. Fetch Quotes
        # Select related parent (Topic) to avoid N+1
        quotes = Quote.objects.filter(is_active=True).select_related('parent').prefetch_related('contents')
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

            # Fetch Quote Content
            for content in quote.contents.all():
                nodes.append({
                    'id': content.neo4j_id,
                    'name': f"Content: {quote.title}",
                    'type': 'CONTENT',
                    'size': 8,
                    'labels': ['Content']
                })
                links.append({
                    'source': content.neo4j_id,
                    'target': quote.neo4j_id,
                    'type': 'HAS_CONTENT'
                })

        # 4. Fetch Passages
        passages = Passage.objects.filter(is_active=True).select_related('parent').prefetch_related('contents')
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

            # Fetch Passage Content
            for content in passage.contents.all():
                nodes.append({
                    'id': content.neo4j_id,
                    'name': f"Content: {passage.title}",
                    'type': 'CONTENT',
                    'size': 8,
                    'labels': ['Content']
                })
                links.append({
                    'source': content.neo4j_id,
                    'target': passage.neo4j_id,
                    'type': 'HAS_CONTENT'
                })
                
        return {
            'nodes': nodes,
            'links': links
        }
