FILTER_FIELDS = {
    "cusname": {
        "label": "Customer Name",
        "type": "string",
    },
    "state": {
        "label": "State",
        "type": "string",
    },
    "clientstatus": {
        "label": "Client Status",
        "type": "choice",
        "choices": ["Active", "Inactive"]
    },
    "since": {
        "label": "Client Since",
        "type": "date",
    },
    "credithold": {
        "label": "Credit Hold",
        "type": "boolean",
    },
}

OPERATORS = {
    "string": [
        ("icontains", "Contains"),
        ("exact", "="),
    ],
    "date": [
        ("gte", ">="),
        ("lte", "<="),
    ],
    "boolean": [("exact", "=")],
    "choice": [("exact", "=")],
}
