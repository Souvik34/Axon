from app.services.agent.agent_service import run_agent

result = run_agent(
    "Calculate the total cost of 5 items each costing 250."
)

print("\nGOAL:")
print(result["goal"])

for attempt in result["attempts"]:
    print(f"\nATTEMPT {attempt['attempt']}")

    print("\nPLAN:")
    for step in attempt["plan"]:
        print(step)

    print("\nEXECUTION:")
    for item in attempt["execution"]["results"]:
        print(item)

print("\nFINAL SUMMARY:")
print(result["final_execution"]["summary"])

print("\nRETRIES:", result["retry_count"])

assert result["final_execution"]["summary"]["failed"] == 0
assert result["final_execution"]["summary"]["completed"] >= 1

print("\nAgent service test successful!")