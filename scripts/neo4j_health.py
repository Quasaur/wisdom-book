import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, SessionExpired, TransientError

REQUIRED = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
missing = [k for k in REQUIRED if not os.getenv(k)]
if missing:
    raise SystemExit(f"Missing required env vars: {missing}. Populate .env first.")

uri = os.getenv("NEO4J_URI")
auth = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
database = os.getenv("NEO4J_DATABASE", "neo4j")

def main():
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session(database=database) as session:
            rec = session.run("RETURN 1 AS ok").single()
            if rec and rec["ok"] == 1:
                print("Neo4j health: OK")
            else:
                print("Neo4j health: UNEXPECTED RESPONSE")
    except AuthError:
        print("Neo4j health: AUTH ERROR")
        raise
    except ServiceUnavailable:
        print("Neo4j health: SERVICE UNAVAILABLE")
        raise
    except (SessionExpired, TransientError) as e:
        print(f"Neo4j health: TEMPORARY ISSUE ({e.__class__.__name__})")
        raise
    finally:
        try:
            driver.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()