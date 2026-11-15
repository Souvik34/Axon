from app.services.agent.agent_service import run_agent

result = run_agent(
    "Calculate 100 divided by zero, then provide the result."
)

print("\nGOAL:")
print(result["goal"])

for attempt in result["attempts"]:
    print(f"\nATTEMPT {attempt['attempt']}")
    print("PLAN:", attempt["plan"])
    print("EXECUTION:", attempt["execution"]["results"])

print("\nFINAL SUMMARY:")
print(result["final_execution"]["summary"])

print("\nRETRIES:", result["retry_count"])