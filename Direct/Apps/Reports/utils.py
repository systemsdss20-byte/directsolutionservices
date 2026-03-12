from django.db.models import Q


def build_query(groups):
    final_q = Q()
    first_group = True

    for group in groups:
        group_q = Q()
        first_rule = True

        for rule in group["rules"]:
            condition = Q(**{
                f"{rule['field']}__{rule['operator']}": rule["value"]
            })

            if first_rule:
                group_q = condition
                first_rule = False
            else:
                group_q &= condition

        if first_group:
            final_q = group_q
            first_group = False
        else:
            final_q = final_q | group_q if group["connector"] == "OR" else final_q & group_q

    return final_q

