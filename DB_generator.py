# python
# insertion script (run in project root; requires pymongo)

import collections

try:
    # normal (older) import may still exist in some environments
    from collections import MutableMapping  # type: ignore
except Exception:
    # ensure MutableMapping is available on `collections` for legacy code
    import collections.abc as _abc

    collections.MutableMapping = _abc.MutableMapping
from pymongo import MongoClient
from models.reptile import Reptile

# python
# Place this at the top of `DB_generator.py` before importing pymongo.
# Provides a compatibility alias for older packages that import MutableMapping


# adjust URI or use environment variable as needed
client = MongoClient("mongodb://localhost:27017")
db = client["herpetarium"]
reptiles_col = db["reptiles"]

# create leopard gecko named gary in tank 1
gary = Reptile(
    id=1,
    name="gary",
    species="leopard gecko",
    age_years=2,
    age_months=0,
    weight=0.06,
    tank_id=1,
)

result = reptiles_col.insert_one(gary.to_dict())
print("Inserted _id:", result.inserted_id)
