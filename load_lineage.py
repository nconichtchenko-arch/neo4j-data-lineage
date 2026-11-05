from neo4j import GraphDatabase

# Подключение к Neo4j
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password") # Если пароль менял, впиши новый

# Наш граф зависимостей
dependencies = [
    ("stg_sales", "dim_customers"),
    ("stg_sales", "dim_products"),
    ("stg_sales", "fct_sales"),
    ("dim_customers", "fct_sales"),
    ("dim_products", "fct_sales"),
    ("fct_sales", "mart_sales_funnel"),
    ("mart_sales_funnel", "executive_dashboard"),
]

def create_graph(tx):
    # Очищаем базу перед загрузкой
    tx.run("MATCH (n) DETACH DELETE n")
    
    for parent, child in dependencies:
        tx.run("""
            MERGE (p:Model {name: $parent})
            MERGE (c:Model {name: $child})
            MERGE (p)-[:DEPENDS_ON]->(c)
        """, parent=parent, child=child)

def main():
    print("Подключаемся к Neo4j...")
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ Подключение успешно!")
        
        with driver.session() as session:
            print("Создаем граф...")
            session.execute_write(create_graph)
            print("✅ Граф создан!")
            
            result = session.run("MATCH (n:Model) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"Всего узлов в базе: {count}")

if __name__ == "__main__":
    main()