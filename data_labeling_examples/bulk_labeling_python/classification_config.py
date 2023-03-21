# maximum number of DLS Dataset records that can be retrieved from the list_records API operation for labeling
# limit=1000 is the hard limit for list_records
LIST_RECORDS_LIMIT = 1000
# the algorithm that will be used to assign labels to DLS Dataset records
# Possible values for labeling algorithm "FIRST_LETTER_MATCH", "FIRST_REGEX_MATCH", "CUSTOM_LABELS_MATCH"
LABELING_ALGORITHM = "FIRST_LETTER_MATCH"
# an array where the elements are all of the labels that you will use to annotate records in your DLS Dataset with.
# Each element is a separate label.
LABELS = ["jpeg", "jpg"]

# use for first_match labeling algorithm
FIRST_MATCH_REGEX_PATTERN = r'^([^/]*)/.*$'

# For CUSTOM_LABEL_MATCH specify the label map
LABEL_MAP = {"dog/": ["dog", "pup"], "cat/": ["cat", "kitten"]}