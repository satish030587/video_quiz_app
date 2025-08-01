import psycopg2
import psycopg2.extras

# PostgreSQL database connection parameters
db_params = {
    'dbname': 'video_quiz_db',
    'user': 'postgres',
    'password': 'Admin@123',
    'host': 'localhost',
    'port': '5432'
}

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get list of all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print("=== TABLES IN DATABASE ===")
    for table in tables:
        table_name = table[0]
        print(f"\n--- TABLE: {table_name} ---")
        
        # Get column information
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        # If table has data, show a sample row
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            row = cursor.fetchone()
            print("Sample row:")
            for col, val in zip(columns, row):
                # Truncate long values for display
                if isinstance(val, str) and len(val) > 100:
                    val = val[:100] + "..."
                print(f"  - {col[0]}: {val}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
