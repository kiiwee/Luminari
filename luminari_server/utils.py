import inspect
import requests
from bs4 import BeautifulSoup
import json
prompt_beginning = """
You are an AI assistant that can help the user with a variety of tasks. You have access to the following functions:

"""

system_prompt_end = """

When the user asks you a question, if you need to use functions, provide ONLY the function calls, and NOTHING ELSE, in the format:
<function_calls>    
[
    { "name": "function_name_1", "params": { "param_1": "value_1", "param_2": "value_2" }, "output": "The output variable name, to be possibly used as input for another function},
    { "name": "function_name_2", "params": { "param_3": "value_3", "param_4": "output_1"}, "output": "The output variable name, to be possibly used as input for another function"},
    ...
]
"""


class FunctionCaller:
    """
    A class to call functions from tools.py.
    """

    def __init__(self):
        # Initialize the functions dictionary
        self.functions = {
            # "get_weather_forecast": get_weather_forecast,
            "internet_search": internet_search,
            # "get_random_city": get_random_city,
            # "get_random_number": get_random_number,
        }
        self.outputs = {}

    def create_functions_metadata(self) -> list[dict]:
        """Creates the functions metadata for the prompt. """
        def format_type(p_type: str) -> str:
            """Format the type of the parameter."""
            # If p_type begins with "<class", then it is a class type
            if p_type.startswith("<class"):
                # Get the class name from the type
                p_type = p_type.split("'")[1]

            return p_type

        functions_metadata = []
        i = 0
        for name, function in self.functions.items():
            i += 1
            descriptions = function.__doc__.split("\n")
            print(descriptions)
            functions_metadata.append({
                "name": name,
                "description": descriptions[0],
                "parameters": {
                    "properties": [  # Get the parameters for the function
                        {
                            "name": param_name,
                            "type": format_type(str(param_type)),
                        }
                        # Remove the return type from the parameters
                        for param_name, param_type in function.__annotations__.items() if param_name != "return"
                    ],

                    "required": [param_name for param_name in function.__annotations__ if param_name != "return"],
                } if function.__annotations__ else {},
                "returns": [
                    {
                        "name": name + "_output",
                        "type": {param_name: format_type(str(param_type)) for param_name, param_type in function.__annotations__.items() if param_name == "return"}["return"]
                    }
                ]
            })

        return functions_metadata

    def call_function(self, function):
        """
        Call the function from the given input.

        Args:
            function (dict): A dictionary containing the function details.
        """

        def check_if_input_is_output(input: dict) -> dict:
            """Check if the input is an output from a previous function."""
            for key, value in input.items():
                if value in self.outputs:
                    input[key] = self.outputs[value]
            return input

        # Get the function name from the function dictionary
        function_name = function["name"]

        # Get the function params from the function dictionary
        function_input = function["params"] if "params" in function else None
        function_input = check_if_input_is_output(
            function_input) if function_input else None

        # Call the function from tools.py with the given input
        # pass all the arguments to the function from the function_input
        output = self.functions[function_name](
            **function_input) if function_input else self.functions[function_name]()
        self.outputs[function["output"]] = output
        return output


def get_func_response(chat_completion,messages):
    """
    Parse the function calls from the model response.
    Args:
        function_calls (list[dict[str, str]]): A list of dictionaries containing the function details.
    """
    function_calls = chat_completion.choices[0].message.content

    # If it ends with a <function_calls>, get everything before it
    if function_calls.startswith("<function_calls>"):
        function_calls = function_calls.split("<function_calls>")[1]

    # Read function calls as json
    try:
        function_calls_json: list[dict[str, str]] = json.loads(function_calls)
    except json.JSONDecodeError:
        function_calls_json = []
        print("Model response not in desired JSON format")
    finally:
        print("Function calls:")
        print(function_calls_json)
    function_message = '<tool_call>' + str(function_calls_json) + '</tool_call>'
    messages.append({'role': 'assistant', 'content': function_message})
    return messages, function_calls_json

def call_functions(messages,function_calls_json,function_caller:FunctionCaller):
    """
    Call the functions from the given input.
    Args:
        function_calls_json (list[dict[str, str]]): A list of dictionaries containing the function details.
    """


    # Call the functions
    output = ""
    out_json=[]
    urls=[]
    for function in function_calls_json:
        print(function)
        output = f"{function_caller.call_function(function)}"
        out_json = function_caller.call_function(function)
    for i in out_json:
        urls.append(i['url'])
    
    tool_output = '<tool_response> ' + output + ' </tool_response>'
    messages.append({'role': 'tool', 'content': tool_output})

    return messages,urls


def search(query):
    url = "http://localhost:8080/search"
    params = {
        'q': query,
        'format': 'json',
        'language': 'en',
    }
    response = requests.get(url, params=params, cookies={'lang;': 'en'})
    return response.json()


def get_text_from_url(results):
    res_l = []
    for result in results:

        url = result.get('url')
        if 'medium.com' in url:
            url = 'https://freedium.cfd/'+url
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        text = [p.text for p in soup.find_all(
            ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

        ai_res = {}
        ai_res['url'] = url
        ai_res['title'] = result.get('title')
        ai_res['content'] = result.get('content')
        ai_res['text'] = text

        res_l.append(ai_res)

    return res_l


def internet_search(query: str) -> list[dict[str, str]]:
    """Retrieves an internet search for a given query"""

    result = search(query)
    response = get_text_from_url(result.get('results')[:2])

    return response
