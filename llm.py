#Note: The openai-python library support for Azure OpenAI is in preview.
import os
import openai
import streamlit as st
openai.api_type = "azure"
openai.api_base = "https://hamzeplayground.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = st.secrets["OPENAI_API_KEY"]

data = """
Year
1900    49752
1901    53177
1902    52889
1903    51443
1904    51075
Name: Number of births, dtype: int64
"""

prompt = f"""
Analyzing Name Trends and Potential Correlations with Political or Social Changes. In this analytical analysis,
we will examine the trends of baby names during the early 20th century and explore any potential correlations with political or social changes.
Our objective is to identify interesting facts and investigate if changes in naming trends align with broader societal shifts during this period. 
The dataset provided includes the number of births for five consecutive years. data is the fallowing:{data}

format: Please use Markdown format
Style: Analytical like Harvard Business Review style with supporting markdown tables and asci art charts
Notic: Please stress on who trend of names changed over the years and how it is related to political or social changes.
Worrining: Dont use the word "I" in your analysis. also dont use python or any other programming language in your analysis.
"""

def anlyze_data(data,comment=None):
    prompt = f"""
    Analyzing Name Trends and Potential Correlations with Political or Social Changes. In this analytical analysis,
    we will examine the trends of baby names during the early 20th century and explore any potential correlations with political or social changes.
    Our objective is to identify interesting facts and investigate if changes in naming trends align with broader societal shifts during this period. 
    The dataset provided includes the number of births for five consecutive years. data is the fallowing:{data}

    format: Please use Markdown format
    Style: Analytical like Harvard Business Review style with supporting markdown tables and asci art charts
    Notice: Please stress on who trend of names changed over the years and how it is related to political or social changes.
    About dateset: {comment}. Please use this context to write your analysis and choose veray creative title of text.
    Worrining: Dont use the word "I" in your analysis. also dont use python or any other programming language in your analysis.

    """
    try:
        response = openai.ChatCompletion.create(
        engine="mini_project",
        messages = [{"role":"system","content":prompt}],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
        
        response_content = response.choices[0].message.content
        return response_content
    except Exception as ex:
        print(ex)
        return "I am sorry, I could not u"
    
if __name__ == "__main__":
    from rich import print
    from rich.markdown import Markdown
    
    print(Markdown(anlyze_data(data)))

