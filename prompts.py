import json
with open('categories.json', 'r') as file:
    data = json.load(file)

prompt1 = f'''We are making a webapp that allows users to lodge complaints regarding
their train travels easily and quickly. We want people to upload a photo and
categorize what complaint they are trying to share and generate a description
of that.
Here are all the problem types and subtypes: {data}
You need to analyze the image and if you are confident, predict the type and
subtype of the problem and generate a description, else return 0.

Here is the format of the output:
If confident about analysis:
{{
"type":"Security",
"subtype":"Theft of Passengers Belongings/Snatching",
"details":"a person is trying to snatch the bag off of a lady's shoulder forcefully."
}}

If not confident:
{{
"type":"0"
}}

Strictly adhere to this output format, no code block, no nothing, just the JSON response in the format I just gave you.
'''

prompt2=f'''We are making a webapp that allows users to lodge complaints regarding
their train travels easily and quickly. We want people to type their issues and
categorize what complaint they are trying to share and generate a description
of that.
Here are all the problem types and subtypes: {data}
You need to analyze their issue and if you are confident, predict the type and
subtype of the problem and generate a description, else return 0.

Here is the format of the output:
If confident about analysis:
{{
"type":"Security",
"subtype":"Theft of Passengers Belongings/Snatching",
"details":"a person is trying to snatch the bag off of a lady's shoulder forcefully."
}}

If not confident:
{{
"type":"0"
}}

Strictly adhere to this output format, no code block, no nothing, just the JSON response in the format I just gave you.
here is the text :
'''
