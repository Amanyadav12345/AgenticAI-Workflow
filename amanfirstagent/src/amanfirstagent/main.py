#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from amanfirstagent.crew import Amanfirstagent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        Amanfirstagent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_truck_booking():
    """
    Run the truck booking workflow.
    """
    inputs = {
        'user_request': 'I need a truck from Mumbai to Delhi',
        'pickup_location': 'Mumbai',
        'delivery_location': 'Delhi',
        'date': datetime.now().strftime("%Y-%m-%d"),
        'user_id': 'user123'
    }
    
    try:
        result = Amanfirstagent().truck_booking_crew().kickoff(inputs=inputs)
        print("Truck booking workflow completed:")
        print(result)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the truck booking workflow: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Amanfirstagent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Amanfirstagent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Amanfirstagent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "truck_booking":
            run_truck_booking()
        elif sys.argv[1] == "train":
            train()
        elif sys.argv[1] == "replay":
            replay()
        elif sys.argv[1] == "test":
            test()
        else:
            run()
    else:
        run()
