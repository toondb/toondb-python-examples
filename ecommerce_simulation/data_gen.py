
import random
import uuid
import numpy as np
from typing import List, Dict, Tuple
from config import (
    NUM_PRODUCTS, BRANDS, CATEGORIES, COLORS, SIZES, 
    VECTOR_DIM, EDGES_PER_PRODUCT_AVG, DAYS_HISTORY, 
    NOW_TIMESTAMP, SECONDS_PER_DAY
)

class DataGenerator:
    def __init__(self):
        self.products = []
        self.category_centroids = {}
        self._init_centroids()
    
    def _init_centroids(self):
        """Initialize random vector centroids for each subcategory."""
        for main_cat, sub_cats in CATEGORIES.items():
            for sub in sub_cats:
                vec = np.random.randn(VECTOR_DIM)
                vec /= np.linalg.norm(vec)
                self.category_centroids[sub] = vec

    def generate_products(self) -> List[Dict]:
        """Generate product catalog with vectors."""
        print(f"Generating {NUM_PRODUCTS} products...")
        all_subs = [sub for cats in CATEGORIES.values() for sub in cats]
        
        for i in range(NUM_PRODUCTS):
            brand = random.choice(BRANDS)
            sub_cat = random.choice(all_subs)
            
            # Find main category
            main_cat = next(k for k, v in CATEGORIES.items() if sub_cat in v)
            
            model = f"Model_{random.randint(100, 999)}"
            color = random.choice(COLORS)
            size = random.choice(SIZES)
            
            sku = f"{brand}-{model}-{size}-{color}".upper()
            title = f"{brand} {model} {sub_cat} ({color})"
            desc = f"Premium {sub_cat} from {brand}. Features high quality materials in {color}."
            
            # Vector = Category Centroid + Noise
            base_vec = self.category_centroids[sub_cat]
            noise = np.random.randn(VECTOR_DIM) * 0.15
            vec = base_vec + noise
            vec /= np.linalg.norm(vec)
            
            product = {
                "id": str(uuid.uuid4()),
                "sku": sku,
                "title": title,
                "description": desc,
                "brand": brand,
                "category": main_cat,
                "subcategory": sub_cat,
                "attributes": {
                    "color": color,
                    "size": size,
                    "model": model
                },
                "vector": vec.tolist(),
                "base_price": round(random.uniform(20.0, 500.0), 2)
            }
            self.products.append(product)
        
        return self.products

    def generate_graph_edges(self) -> List[Dict]:
        """Generate BOUGHT_TOGETHER and COMPATIBLE_WITH edges."""
        edges = []
        
        # BOUGHT_TOGETHER (Zipf-like logic: some products very popular)
        # For simplicity, random connections biased by category
        for prod in self.products:
            num_edges = random.randint(1, 10)
            target_ids = random.sample(self.products, num_edges)
            
            for target in target_ids:
                if target["id"] == prod["id"]: continue
                
                edges.append({
                    "from_id": prod["id"],
                    "to_id": target["id"],
                    "type": "BOUGHT_TOGETHER",
                    "properties": {"weight": f"{random.random():.2f}"}
                })

            # COMPATIBLE_WITH (accessories -> main items)
            if prod["subcategory"] == "Accessories":
                # Find compatible electronics
                electronics = [p for p in self.products if p["category"] == "Electronics" and p["subcategory"] != "Accessories"]
                if electronics:
                    matches = random.sample(electronics, min(3, len(electronics)))
                    for m in matches:
                        edges.append({
                            "from_id": prod["id"],
                            "to_id": m["id"],
                            "type": "COMPATIBLE_WITH",
                            "properties": {}
                        })
                        
        return edges

    def generate_temporal_data(self) -> List[Dict]:
        """Generate price history for products."""
        temporal_entries = []
        
        for prod in self.products:
            # 30% of products have price changes
            if random.random() < 0.3:
                curr_price = prod["base_price"]
                
                # Generate 4 weekly price points
                for week in range(4):
                    # Time going backwards
                    timestamp = NOW_TIMESTAMP - (week * 7 * SECONDS_PER_DAY)
                    
                    # Random price fluctuation
                    price = curr_price * random.uniform(0.8, 1.2)
                    price = round(price, 2)
                    
                    temporal_entries.append({
                        "node_id": prod["id"],
                        "type": "PRICE",
                        "value": str(price),
                        "valid_from": timestamp - (7 * SECONDS_PER_DAY),
                        "valid_until": timestamp
                    })
        return temporal_entries

    def generate_queries(self) -> List[Dict]:
        """Generate mixed workload queries."""
        queries = []
        
        # 1. Exact SKU
        targets = random.sample(self.products, 3)
        for t in targets:
            queries.append({
                "type": "exact",
                "text": t["sku"],
                "target_id": t["id"]
            })
            
        # 2. Semantic / Intent
        # "Charger for <Laptop Brand>"
        laptops = [p for p in self.products if p["subcategory"] == "Laptops"]
        if laptops:
            target = random.choice(laptops)
            queries.append({
                "type": "intent",
                "text": f"Charger for {target['brand']} laptop",
                "vector": (self.category_centroids["Accessories"] + np.random.randn(VECTOR_DIM)*0.05).tolist(),
                "target_category": "Accessories"
            })
            
        # 3. Temporal
        # "Price of X 2 weeks ago"
        queries.append({
            "type": "temporal",
            "target_id": self.products[0]["id"],
            "query_time": NOW_TIMESTAMP - (14 * SECONDS_PER_DAY)
        })
        
        return queries
