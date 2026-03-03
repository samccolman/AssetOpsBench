"""
Sample client for tracking Asset Ops Bench runs

run this like:
$ uv run mcp/plan_execute/tracking.py 

"""
from os import environ
import asyncio, json

from dotenv import load_dotenv
from scenario_client.client import AOBench

from llm.litellm import LiteLLMBackend
from plan_execute.runner import PlanExecuteRunner


def main():

    # environment variables for scenario server and mlflow server
    abi: str = environ["SCENARIO_SERVER_URI"]
    mfi: str = environ["MLFLOW_TRACKING_URI"]

    # AOBench client
    aob = AOBench(scenario_uri=abi, tracking_uri=mfi)

    # Pick the scenario set of interest
    scenario_set_id = "b3aa206a-f7dc-43c9-a1f4-dcf984417487" #Asset Ops Bench - IoT
    # enable tracking on mlflow
    tracking = True

    # get the scenarios from the server
    scenario_set, tracking_context = aob.scenario_set(
        scenario_set_id=scenario_set_id, tracking=tracking
    )

    scenarios = [
        {"id": s["id"], "query": s["query"]} for s in scenario_set["scenarios"]
    ]

    # provide the name of this run
    run_name = "demo first 5"
    
    # Loop over first five scenarios and collect the agent responses
    answers = []
    for scenario in scenarios[:5]:
        scenario_id = scenario["id"]
        query = scenario["query"]

        print(f"{scenario_id=}")
        print(f"{query=}")

        runner = PlanExecuteRunner(llm=LiteLLMBackend("watsonx/meta-llama/llama-3-3-70b-instruct"))


        try: 
            response = asyncio.run( aob.arun(
                afunc=runner.run,
                scenario_id=scenario_id,
                run_name=run_name,
                tracking_context=tracking_context,
                post_process=None,
                question=query,
            ))
            print(f"{response=}")

            answers.append(response)


        except Exception as e:
            print(e)

        print(" * * * * ")


    ## send the responses to the server for grading
    ## server requires update w latest evals so this is commented out for now
    #grades = aob.grade(
    #    scenario_set_id=scenario_set_id,
    #    answers=answers,
    #    tracking_context=tracking_context,
    #)

    ## print the grading results to the console
    #print(json.dumps(grades, indent=2))




if __name__ == '__main__':
    load_dotenv()
    main()