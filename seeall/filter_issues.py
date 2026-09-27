"""Filter grouped issues for the Issues tab: all / critical only / measured only / AI only."""


def filter_groups(groups, mode):
    if mode == "critical":
        return [g for g in groups if g.get("severity") == "critical"]
    if mode == "measured":
        return [g for g in groups if g.get("source") == "measured"]
    if mode == "ai":
        return [g for g in groups if "ai" in g.get("source", "")]
    return groups
