def get_deviation_patterns(patterns):

    deviation_patterns = [
        (support, pattern)
        for support, pattern in patterns
        if pattern[-1] == "Protocol Deviation"
    ]

    return deviation_patterns

def add_support_percentage(patterns, total_sequences):

    patterns_with_percentage = []

    for support, pattern in patterns:

        percentage = round(
            (support / total_sequences) * 100,
            2
        )

        patterns_with_percentage.append(
            (support, percentage, pattern)
        )

    return patterns_with_percentage

def sort_patterns(patterns):

    return sorted(
        patterns,
        key=lambda x: x[0],
        reverse=True
    )
