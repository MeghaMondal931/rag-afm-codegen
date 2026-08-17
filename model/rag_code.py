

# %%
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata
from sentence_transformers import SentenceTransformer
# %%
from langchain.retrievers.multi_query import MultiQueryRetriever
# from langchain.chat_models import ChatOpenAI  # or use a local LLM
from langchain_groq import ChatGroq
import nanosurf
import time
import os
from dotenv import load_dotenv
load_dotenv()
api_key_groq = os.getenv("GROQ_API_KEY")
api_key_gpt = os.getenv("OPENAI_API_KEY_PLANNER")
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)




# %%
# decomposes user query in procedural tasks to get one function per step
def decompose_user_task(user_task: str, llm) -> list:
    planner_prompt = f"""
You are an expert AFM programming assistant.

Break down the user query using following instructions into a step-by-step sequence of procedural programming sub-tasks.

Make each step:
- No need to initialize AFM system or AFM software control panel
- focused on one atomic action
- clear enough to retrieve a function for
- calculate the scanning delay corresponding to the current sample size and scan speed 
- no extra sub-task or step without being asked to by user 
- suitable to write as Python code

User task: "{user_task}"

Return each step on a new line.
"""
    response = llm.invoke(planner_prompt)
    return [line.strip("-• ") for line in response.content.strip().split("\n") if line.strip()]


# %%
#reranking mechanism  new
from sentence_transformers import util, CrossEncoder

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')

def jaccard_similarity(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0.0

def hybrid_score_n(sub_query, doc_text, alpha=0.7, beta=0.3):
    # d_vec = model.encode(doc_text, convert_to_tensor=True)

    semantic_sim = cross_encoder.predict([(sub_query, doc_text)])[0]
    keyword_sim = jaccard_similarity(sub_query, doc_text)

    return alpha * semantic_sim + beta * keyword_sim

def rerank_mqr_results_n(sub_query,functs,k):
    # docs = multi_query_retriever.get_relevant_documents(user_query)
    
    reranked = sorted(functs, key=lambda d: hybrid_score_n(sub_query, d.page_content), reverse=True)[:k]
    

    return reranked

# %%
standard_setup = """# Required imports and controller setup
import time
import nanosurf
spm = nanosurf.SPM()
app = spm.application
"""

standard_teardown = """# Clean up
del spm"""

instruction_set = """ #Instructions:
- Always begin with the setup code.                                     
- Use 'spm' as the controller object.
- Use 'app' as the main_class object.                                             
- Use the teardown code at the end.
- All class types except 'main_class' are objects of the main class object. 
- Create them using  'object_name' in its exact same format from the field value in metadata.
- Method calls must follow this format: 'object_name.method_name(arguments)' using retrieved metadata.
- Use the retrieved functions to implement the logic. 
- Do not assume or simulate any fake placeholder function definitions unless explicitly provided.  
- From the query derive the required values for arguments for each retrieved function.
- Use provided 'Arguments' metadata to fill in function arguments with sensible values.
- Always skip unrelated or duplicate steps.
- Add 'time.sleep()' if a delay is implied.
- Print a status message after each step.
"""


from langchain_core.prompts import PromptTemplate

code_template = PromptTemplate.from_template("""
You are a Python assistant that writes complete code for controlling a Nanosurf SPM system.

Given a user query and a set of function definitions, generate full working Python code to complete the task.

Instructions:
{instructions}

User Query:
{query}

Setup Code:
{setup}

Function Definitions:
{retrieved}

Teardown Code:
{teardown}

Write the full Python code below:
""")


def generate_afm_code(user_query: str, multi_query_retriever, llm, model) -> str:
    
    sub_queries = decompose_user_task(user_query, llm) 
    # print(sub_queries)
    all_results = []
    for subquery in sub_queries:
        subquery = subquery.strip("-• ").strip()
        docs = multi_query_retriever.retriever.get_relevant_documents(subquery)
        # q_vec = model.encode(subquery, convert_to_tensor=True)
        results_methods = rerank_mqr_results_n(subquery, docs, k=1)
        all_results.append((subquery,results_methods))
    for step, docs in all_results:
        print(f"\nStep: {step}")
        for doc in docs:
            print("  Description:", doc.page_content)
            print("  Function:", doc.metadata.get("method_name", "N/A"))
        
    retrieved_funcs = ""
    for step, docs in all_results:
        retrieved_funcs += f"\n# Step: {step}\n"
        for doc in docs:
            retrieved_funcs += f"# {doc.page_content}\n{doc.metadata.get('method_name', 'N/A')}\n"
        # Only include Arguments if present
            if doc.metadata.get("Arguments"):
                retrieved_funcs += f"# Arguments / Settings / Remarks:\n{doc.metadata['Arguments']}\n"   

    full_prompt = code_template.format(
        instructions = instruction_set,
        query=user_query,
        setup=standard_setup,
        retrieved=retrieved_funcs,
        teardown=standard_teardown
    )
    start_time = time.time()
    response = llm.invoke(full_prompt)
    end_time = time.time()
    time_taken = end_time - start_time
    return response.content, response.response_metadata , all_results, retrieved_funcs, time_taken


# # %%
# def validate_and_repair_code(query, multi_query_retriever, llm, model=None, threshold=0.6):
#     # Step 1: Generate code
#     code, all_results, retrieved_funcs = generate_afm_code(query, multi_query_retriever, llm, model, return_metadata=True)

#     # Step 2: Build validation metadata from retrieved functions
#     valid_methods = []
#     method_to_object = {}
#     function_argument_map = {}

#     for step, docs in all_results:
#         for doc in docs:
#             raw_method = doc.metadata.get("method_name", "").split()[0]
#             object_name = doc.metadata.get("method_name", "").split('.')[0]
#             method_to_object[raw_method] = object_name
#             valid_methods.append(raw_method)

#             args_raw = doc.metadata.get("Arguments", "").split("\n")
#             args_cleaned = [args_raw[i] for i in range(0, len(args_raw), 3) if i < len(args_raw)]
#             function_argument_map[raw_method] = args_cleaned

#     # Step 3: Score the code
#     mean_score, line_scores = score_code_lines(
#         code,
#         valid_objects=list(set(method_to_object.values())),
#         valid_methods=valid_methods,
#         method_to_object=method_to_object,
#         function_argument_map=function_argument_map
#     )

#     if mean_score >= 0.8:
#         return code  # Code is valid

#     # Step 4: Build re-prompt for low-score lines
#     low_score_lines = [line for line, score in zip(code.splitlines(), line_scores) if score < threshold]
#     if not low_score_lines:
#         return code

#     repair_prompt = f"""# Original Query: {query}
# # Instructions:
# {instruction_set}
# # Lines needing rewrite (low score < {threshold}):
# {chr(10).join(low_score_lines)}
# # Retrieved Functions:
# {retrieved_funcs}

# Please rewrite only the above lines using the retrieved functions and metadata.
# """

#     # Step 5: Call LLM to rewrite
#     rewritten = llm.invoke(repair_prompt).content.splitlines()
#     rewritten_iter = iter(rewritten)

#     # Step 6: Replace low-score lines in original code
#     final_lines = []
#     for line, score in zip(code.splitlines(), line_scores):
#         if score < threshold:
#             final_lines.append(next(rewritten_iter))
#         else:
#             final_lines.append(line)

#     return "\n".join(final_lines)


