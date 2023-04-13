import openai
import javalang as jl
import openai


def __get_start_end_for_node(node_to_find):
    start = None
    end = None
    for path, node in tree:
        if start is not None and node_to_find not in path:
            end = node.position
            return start, end
        if start is None and node == node_to_find:
            start = node.position
    return start, end


def __get_string(start, end):
    if start is None:
        return ""

    # positions are all offset by 1. e.g. first line -> lines[0], start.line = 1
    end_pos = None

    if end is not None:
        end_pos = end.line - 1

    lines = data.splitlines(True)
    string = "".join(lines[start.line:end_pos])
    string = lines[start.line - 1] + string

    # When the method is the last one, it will contain a additional brace
    if end is None:
        left = string.count("{")
        right = string.count("}")
        if right - left == 1:
            p = string.rfind("}")
            string = string[:p]

    return string

# Set up the OpenAI API credentials
openai.organization = "org-pJCoNF4wqAwPGcYJZ6yRvnsN"
openai.api_key = "<Put your key here>"

openai.Model.list()


if __name__ == '__main__':

    data = open("source/Test.java").read()
    tree = jl.parse.parse(data)
    methods = {}
    for _, node in tree.filter(jl.tree.MethodDeclaration):
        start, end = __get_start_end_for_node(node)
        methods[node.name] = __get_string(start, end)
    prompt = methods.get('main').replace("\t", "")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Please provide code explaination for this :"+prompt,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )

    codeExplainResponse = response.choices[0].text

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + "\nTime complexity for this is: ",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )

    timeComplexityResponse = response.choices[0].text

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Provide code review for this : "+data,
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0,
    )

    codeReviewResponse = response.choices[0].text

    blackduckfile = open("source/blackduck-scan-summary-1.1.0-Iteration-2.txt", "r")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Convert my short hand into a first-hand account of the meeting:\n\n" + blackduckfile.read(),
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    blackduckResponse = response.choices[0].text

    file = open('responses/FinalReviewComments.txt', 'w')
    file.write("************** Code Explaination ************** \n")
    file.write(codeExplainResponse)
    file.write("\n\n************** Time Complexity ************** \n\n")
    if timeComplexityResponse != ' O(n)':
        file.write("Time complexity for this method is "+timeComplexityResponse+" which doesn't meet company standards. Refactoring of this code is required.")
    else:
        file.write("Time complexity for this method is " + timeComplexityResponse + " which meets company standards. Refactoring is not required.")
    file.write("\n\n************** Code Review Comments ************** \n")
    file.write(codeReviewResponse)
    file.write("\n\n************** Blackduck scan Report **************")
    file.write(blackduckResponse)
    file.close()

    print("Code has been analysed and final comments are drafted in the file - FinalReviewComments.txt")