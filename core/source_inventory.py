import json

def build_inventory():
    with open('data/extracted_q_and_a.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    inventory = {
        "Q1": {
            "a": {}, "b": {}, "c": {}, "d": {}
        },
        "Q2": {
            "a": {}, "b": {}, "c": {}, "d": {}
        }
    }
    
    # We will just dump all the raw data we extracted directly for now
    inventory["raw"] = data
    
    with open('data/reference_answers.json', 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4)
        
    print("Inventory built.")

if __name__ == '__main__':
    build_inventory()
