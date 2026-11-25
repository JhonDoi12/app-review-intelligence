LABELS_3 = ["negatif", "netral", "positif"]


def rating_to_label(rating: int, three_class: bool = True) -> str | None:
    """Weak label dari bintang. Pada skenario 2 kelas, bintang 3 mengembalikan None."""
    if rating in (1, 2):
        return "negatif"
    if rating == 3:
        return "netral" if three_class else None
    if rating in (4, 5):
        return "positif"
    raise ValueError(f"rating di luar 1-5: {rating}")
