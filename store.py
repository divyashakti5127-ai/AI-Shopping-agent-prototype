import re
from catalog import PRODUCTS

STOP_WORDS = {
    "a", "an", "the", "for", "and", "or", "to", "in", "of", "with",
    "my", "me", "is", "it", "on", "at", "by", "from", "some", "that",
    "this", "need", "want", "looking", "like", "likes", "under", "below",
}


def check_budget(cart_ids, budget):
    """Plain-code safety check: returns (total, ok). Never trust the AI's maths."""
    by_id = {p["id"]: p for p in PRODUCTS}
    total = round(sum(by_id[i]["price"] for i in cart_ids), 2)
    return total, total <= budget


def shortlist(request_text, budget, limit=40):
    """Return up to `limit` products priced <= budget that best match request_text."""
    raw_words = re.findall(r"[a-z0-9]+", (request_text or "").lower())
    words = [w for w in raw_words if w not in STOP_WORDS and len(w) > 1]

    affordable = [p for p in PRODUCTS if p["price"] <= budget]
    scored = []

    for p in affordable:
        name_lower = p["name"].lower()
        cat_lower = p["category"].lower()
        tags_lower = [t.lower() for t in p["tags"]]
        searchable = f"{name_lower} {cat_lower} {' '.join(tags_lower)}"

        score = 0
        for w in words:
            stem = w[:-1] if (len(w) > 3 and w.endswith("s")) else w
            if w in tags_lower or stem in tags_lower:
                score += 3
            if w in cat_lower or stem in cat_lower:
                score += 3
            if w in name_lower or stem in name_lower:
                score += 2
            elif stem in searchable:
                score += 1

        if score > 0:
            scored.append((score, p))

    # Sort best keyword matches first, breaking ties by lower price then id
    scored.sort(key=lambda item: (-item[0], item[1]["price"], item[1]["id"]))
    result = [p for _, p in scored[:limit]]

    # If too few matched, fill up with cheap popular/gift items within budget
    if len(result) < limit:
        picked_ids = {p["id"] for p in result}
        fillers = [p for p in affordable if p["id"] not in picked_ids]
        fillers.sort(
            key=lambda p: (
                0 if ("gift" in p["tags"] or "budget" in p["tags"]) else 1,
                p["price"],
                p["id"],
            )
        )
        for p in fillers:
            if len(result) >= limit:
                break
            result.append(p)

    return result


if __name__ == "__main__":
    print(check_budget([1, 5, 12], 35.00))
    sample = shortlist("gift for my sister, likes books and plants", 30.00)
    print(f"Shortlist count: {len(sample)}")
