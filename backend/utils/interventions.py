def create_plan(row):

    actions = []

    if row["absences"] > 10:
        actions.append(
            "Attendance monitoring"
        )

    if row["studytime"] < 2:
        actions.append(
            "Extra study sessions"
        )

    if row["failures"] > 1:
        actions.append(
            "Mentor support"
        )

    if len(actions) == 0:
        actions.append(
            "Normal tracking"
        )

    return actions