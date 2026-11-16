from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import ast

app = FastAPI(title="AI Code Reviewer")

# إعداد قوالب HTML
templates = Jinja2Templates(directory="templates")

class CodeRequest(BaseModel):
    code: str

class CodeReviewer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            self.issues.append({
                "line": node.lineno,
                "type": "Missing Docstring",
                "message": f"Function '{node.name}' lacks a documentation string (docstring)."
            })
        
        if len(node.args.args) > 5:
            self.issues.append({
                "line": node.lineno,
                "type": "Too Many Arguments",
                "message": f"Function '{node.name}' has {len(node.args.args)} arguments. Consider refactoring."
            })
            
        self.generic_visit(node)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/review")
def review_code(data: CodeRequest):
    code_content = data.code
    
    if not code_content.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Syntax Error at line {e.lineno}: {e.text}",
            "issues": []
        }

    reviewer = CodeReviewer()
    reviewer.visit(tree)

    return {
        "status": "success",
        "issues": reviewer.issues
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)