from mongo_connection import RecipeDatabase

def test_connection():
    print("Starting connection test...")
    
    # Create a database instance
    db = RecipeDatabase()
    
    # Try to connect
    if db.connect():
        print("Connection successful!")
        
        # Test a simple query to verify we can access data
        try:
            # Get the total number of recipes
            count = db.collection.count_documents({})
            print(f"Total recipes in database: {count}")
            
            # Get a single recipe to verify data access
            sample = db.collection.find_one({})
            if sample:
                print("\nFound a sample recipe:")
                print(f"Name: {sample.get('name', 'Unknown')}")
                print(f"Cooking time: {sample.get('minutes', 'Unknown')} minutes")
                print(f"Number of ingredients: {len(sample.get('ingredients', []))}")
                print(f"Number of steps: {len(sample.get('steps', []))}")
            else:
                print("Could not retrieve a sample recipe. The collection might be empty.")
        
        except Exception as e:
            print(f"Error executing query: {e}")
    else:
        print("Connection failed. Please check your MongoDB URI and network connection.")
    
    # Always close the connection when done
    print("\nClosing connection...")
    db.close()
    print("Test completed.")

if __name__ == "__main__":
    test_connection()