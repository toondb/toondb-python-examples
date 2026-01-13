
import os

# Data Scale
NUM_PRODUCTS = 2000  # Scaled down for interactive simulation
NUM_BRANDS = 50
NUM_CATEGORIES = 20

# Vectors
VECTOR_DIM = 1536
DB_PATH = "./sochdb_data_ecommerce"

# Time
DAYS_HISTORY = 30
NOW_TIMESTAMP = 1736465492 # Use the current time from metadata as anchor
SECONDS_PER_DAY = 86400

# Graph Distribution
EDGES_PER_PRODUCT_AVG = 5

# Brands & Categories
BRANDS = [
    f"Brand_{i}" for i in range(NUM_BRANDS)
]

CATEGORIES = {
    "Electronics": ["Laptops", "Phones", "Accessories", "Tablets"],
    "Apparel": ["Shoes", "T-Shirts", "Jackets", "Activewear"],
    "Home": ["Kitchen", "Furniture", "Lighting", "Decor"],
}

# Attributes
COLORS = ["BLK", "WHT", "RED", "BLU", "GRN", "YEL"]
SIZES = ["S", "M", "L", "XL", "42", "44", "9", "10", "11"]
