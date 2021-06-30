def group_when_any(values, condition):
    groups = []
    for value in values:
        has_been_assigned_to_group = False
        for group in groups:
            if any(condition(value2, value) for value2 in group):
                group.append(value)
                has_been_assigned_to_group = True
        if not has_been_assigned_to_group:
            group = [value]
            groups.append(group)
    return groups
