from collections import Counter
from catalog import PRODUCTS

REQUIRED_FIELDS = ("id", "name", "price", "category", "tags")


def validate():
    errors = []
    seen_ids = set()

    if not (250 <= len(PRODUCTS) <= 300):
        errors.append(f"Expected 250-300 products, found {len(PRODUCTS)}")

    for idx, p in enumerate(PRODUCTS, start=1):
        # Check required fields and non-empty values
        for field in REQUIRED_FIELDS:
            if field not in p or p[field] is None or p[field] == "":
                errors.append(f"Item at position {idx} is missing field '{field}'")

        pid = p.get("id")
        if pid in seen_ids:
            errors.append(f"Duplicate id: {pid}")
        seen_ids.add(pid)

        if pid != idx:
            errors.append(f"ID gap or out-of-order at position {idx}: got id={pid}")

        price = p.get("price")
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            errors.append(f"Product id={pid} has non-numeric price: {price!r}")
        else:
            if price < 1.50 or price > 60.00:
                errors.append(f"Product id={pid} price {price} is outside 1.50..60.00")

        tags = p.get("tags")
        if not isinstance(tags, list) or not tags:
            errors.append(f"Product id={pid} must have a non-empty tags list")
        elif pid >= 25 and not (4 <= len(tags) <= 8):
            errors.append(f"Product id={pid} has {len(tags)} tags (expected 4-8)")

    counts = Counter(p["category"] for p in PRODUCTS)
    print(f"Total products: {len(PRODUCTS)}")
    print(f"Total categories: {len(counts)}\n")
    print("Products per category:")
    for category, count in sorted(counts.items()):
        print(f"  - {category}: {count}")

    if errors:
        print("\nValidation FAILED:")
        for e in errors:
            print("  !", e)
        raise SystemExit(1)

    print("\nAll validation checks PASSED: unique sequential IDs, no missing fields, numeric prices <= $60.00.")


if __name__ == "__main__":
    validate()
