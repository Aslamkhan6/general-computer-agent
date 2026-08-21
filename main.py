from app.planner.planner import Planner


def main():

    planner = Planner()

    goal = "Create a directory called AI-Agent"

    plan = planner.create_plan(goal)

    print("=== TASK PLAN ===")

    print("Goal:")
    print(plan.goal)

    print("\nSteps:")

    for step in plan.steps:
        print(
            f"{step.id}: "
            f"{step.description}"
        )


if __name__ == "__main__":
    main()