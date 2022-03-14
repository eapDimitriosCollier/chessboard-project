# Θέλουμε set αντί για list ή dict διότι
# 1. Το κάθε item στην λίστα είναι μοναδικό
# 2. Κάνουμε μόνο check ύπαρξης tag μέσα σε αυτά τα sets κάτι που τα set κάνουν πιο γρήγορα
# 3. Δεν μας αφορά η σειρά με την οποία βρίσκονται τα tags. 

REQUIRED_TAG_IDENTIFIERS = {
    'Event',
    'Site',
    'White',
    'Black',
    'Result',
}