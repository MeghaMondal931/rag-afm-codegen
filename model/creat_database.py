# %%
from langchain_community.document_loaders import PyMuPDFLoader
import re
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.vectorstores import VectorStoreRetriever


# %%
# Flatten all pages into a single line list with page tracking
# page tracking required as we can use them to search for things inside pdf
import fitz  

pdf_path="C:\\Users\\megha\\OneDrive\\Desktop\\Papers\\programmers-manual copy.pdf"
doc = fitz.open(pdf_path)

all_lines = []
footer_keywords = [
    "©", 
    "Script Programmers Manual", 
    "Object Reference", 
    "all rights reserved"
]

for page_num, page in enumerate(doc, start=1):
    lines = page.get_text().splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if any(footer in line for footer in footer_keywords):
            continue
        all_lines.append((line, page_num))

# %%
import re

# headings have patterns 7.1.1.1
heading_pattern = re.compile(r"^7(?:\.\d+){3}\b")
heading_shorter_pattern = re.compile(r"^7(?:\.\d+){1,2}\b")
# Parse into structured method/property blocks
method_blocks = []
current_block = {
    "heading": None,
    "page_start": None,
    "page_end": None,
    "class_type": None,
    "content": []
}

for line, page in all_lines:
    if heading_pattern.match(line):
        if current_block["heading"]:
            method_blocks.append(current_block.copy())
        # we need to check whether the actual heading is in the same line(check for space with strip the line)
        parts = line.strip().split(" ",1)
        heading = parts[0]  #id
        content_start = parts[1].strip() if len(parts) > 1 else ""


        current_block = {
            "heading": parts[0],
            "page_start": page,
            "page_end": page,
            "content": [content_start] if content_start else []
        }
    elif heading_shorter_pattern.match(line) and current_block["heading"]:
        # Stop collecting if a shorter heading (section heading) appears
        method_blocks.append(current_block.copy())
        current_block = {"heading": None, "content": []}

    else:
        if current_block["heading"]:
            current_block["content"].append(line)
            current_block["class_type"] = "main class" if current_block["content"][0].startswith("Application") else "Online object or Data Processing object"
            current_block["page_end"] = page

# Add last block
if current_block["heading"]:
    method_blocks.append(current_block)


# %%
for i in range(len(method_blocks)):
    print(f"\n--- Method Block {i+1} ---")
    print(method_blocks[i])
print(len(method_blocks))

# %%
idx_Del=[]
for i in range(len(method_blocks)-1):
    
    if(method_blocks[i]['content'][0]==method_blocks[i+1]['content'][0]): 
        idx_Del.append(i)
print(idx_Del)
# Remove duplicates

corrected_method_block=[]
for i in range(len(method_blocks)):
    if i not in idx_Del:
        corrected_method_block.append(method_blocks[i])
for i in range(len(corrected_method_block)):
    print(f"\n--- Corrected Method Block {i+1} ---")
    print(corrected_method_block[i])


# %%
print(len(corrected_method_block))

# %%
def extract_sections(content: list[str]) -> dict:
    result = {}
    i = 0
    current_section = None
    section_buffer = {"argument_section": [], "setting_section": [], "remark_section": []}

    section_keywords = {
        "arguments": "argument_section",
        "setting": "setting_section",
        "settings": "setting_section",
        "remarks": "remark_section"
    }

    while i < len(content):
        line = content[i].strip()
        lower_line = line.lower()

        if lower_line in section_keywords:
            current_section = section_keywords[lower_line]
            i += 1
            continue

        elif line.lower() in {"example", "syntax", "result", "see also"}:
            current_section = None

        elif current_section:
            section_buffer[current_section].append(line)

        i += 1

    # Only add non-empty sections to result
    for key, val in section_buffer.items():
        if val:
            result[key] = val

    return result

# %%
#extracting the names and descriptions
class_table_dict={}
seen = set()
duplicates = 0
for i in range(len(corrected_method_block)):
    method_name = None
    method_description = None
    object_name = None
    
    class_type = corrected_method_block[i]["class_type"]
    content = corrected_method_block[i]["content"]
    
    if(content[0] != "Application::System" and content[0] != "Application::SPMCtrlManager"):
        #need the location of the syntax in content

        syntax_idx = content.index("Syntax")
        object_name =  content[0].split("::")[0].strip()
        start_idx = 1
        # if( "::"  in content[0]):
        #     start_idx = 1 #if the first line has a class name then start from 1
    
        method_description = " ".join(content[start_idx:syntax_idx]).replace("\n", " ").strip() #all text before syntax starting from content[1]
        if method_description in seen:
            duplicates += 1
        else:
            seen.add(method_description) 
        method_name = content[syntax_idx+1] #the text after syntax
        sections = extract_sections(content)
        class_table_dict[( method_description, object_name)]={
            "method_name" : method_name,
            "class_type": class_type,
            **sections
            
        } 
    # else:
    #     print(i)       
        
print(len(class_table_dict))
print(duplicates)
print(seen)
    

# %%
class_table_dict[('Returns a object pointer to the single System class object','Application')] = {"method name":'application.System', "class_type": 'main class'}


# %%


def patch_method_name_prefix(class_table_dict):
    """
    Modifies method_name so that it always starts with the actual object_name used.
    This way, you don't have to track object_name separately in validators.
    """
    for (method_description, object_name), function in class_table_dict.items():
        raw_method = function.get("method_name", "")
        # Replace the object part of method_name with the actual object_name
        fixed_method = re.sub(r"^\w+\.", f"{object_name}.", raw_method)
        function["method_name"] = fixed_method
    return class_table_dict


# %%
class_table_dict_new = patch_method_name_prefix(class_table_dict)
for k, v in class_table_dict_new.items():
    print(k)
    print(v)

# %%
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.vectorstores import VectorStoreRetriever


persist_path = "./chroma_db"
docs = []
#split
for (desc,obj_name), function in class_table_dict.items():
    argument_text = "\n".join(function.get("argument_section", []))
    setting_text = "\n".join(function.get("setting_section", []))
    remark_text = "\n".join(function.get("remark_section", []))

    combined_info = "\n".join(filter(None, [argument_text, setting_text, remark_text]))
    flat_metadata = {
        "method_name": function.get("method_name", ""),
        "class_type": function.get("class_type", ""),
        "object_name": obj_name,
        "Arguments": combined_info
    }

    
    d = Document(page_content=desc, metadata=flat_metadata)
    docs.append(d)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(docs, embedding_model,persist_directory=persist_path)
vectorstore.persist()