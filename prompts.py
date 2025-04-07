import json
with open('categories.json', 'r') as file:
    data = json.load(file)
with open('department.json', 'r') as file:
    dept = json.load(file)

prompt1 = f'''We are making a webapp that allows users to lodge complaints regarding 
their train travels easily and quickly. We want people to upload a photo and 
categorize what complaint they are trying to share and generate a description 
of that.

Here are all the problem types and subtypes: {data} 

You need to analyze the image and, if confident, predict the type and 
subtype of the problem and generate a description. Otherwise, return 0.

Here is the format of the output:  
If confident about analysis:  
{{
  "type": "Security",
  "subtype": "Theft of Passengers Belongings/Snatching",
  "details": "A person is trying to snatch the bag off of a lady's shoulder forcefully."
}}

If not confident:  
{{
  "type": "0"
}}

return the answer in text format, no code blocks please'''


prompt2 = f'''We are making a webapp that allows users to lodge complaints regarding 
their train travels easily and quickly. We want people to type their issues and 
categorize what complaint they are trying to share and generate a description of that.

Here are all the problem types and subtypes: {data}  

You need to analyze their issue and, if confident, predict the type and 
subtype of the problem and generate a description. Otherwise, return 0.

Here is the format of the output:  
If confident about analysis:  
{{
  "type": "Security",
  "subtype": "Theft of Passengers Belongings/Snatching",
  "details": "A person is trying to snatch the bag off of a lady's shoulder forcefully."
}}

If not confident:  
{{
  "type": "0"
}}

return the answer in text format, no code blocks please'''


prompt3 = f'''We are making a webapp that allows users to lodge complaints regarding 
their train travels easily and quickly. People are giving us problem details, problem types, and other details. We want to assess their severity and assign a department to the complaint.

Here are all the problem types and their respective departments: {dept}  

You need to analyze their issue type and predict the severity and department for the problem type.

Severity can be:  
- **Low**: Minor inconveniences like fan not working, bedsheets not available, etc.  
- **Medium**: Issues that might escalate if not resolved, like water not available, fights between passengers, etc.  
- **High**: Serious ethical or safety concerns that cannot be ignored, like theft, assault, medical needs, bribery, etc.  

Here is the format of the output:  
{{
  "severity": "high",
  "department": "Security"
}}

**Return only the JSON response in this exact format.** Do not include any extra text, code blocks, or markdown syntax.  
Here is the data:'''
