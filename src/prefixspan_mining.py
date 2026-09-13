from prefixspan import PrefixSpan

def mine_patterns(sequences, min_support=50):
    ps = PrefixSpan(sequences)
    patterns = ps.frequent(min_support)
    return patterns