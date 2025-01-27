from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# from fastapi import FastAPI

# print("hello jajja")
# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, jajja brand!"}

# @app.post("/items/")
# def create_item(item: dict):
#     return {"item": item}



print("hello jajja")
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    app = FastAPI()

    class Item(BaseModel):
        name: str
        description: str = None
        price: float
        tax: float = None

    items = {}

    @app.get("/", response_class=HTMLResponse)
    def read_root():
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }
                .container {
                    width: 80%;
                    margin: auto;
                    overflow: hidden;
                }
                header {
                    background: #333;
                    color: #fff;
                    padding-top: 30px;
                    min-height: 70px;
                    border-bottom: #77aaff 3px solid;
                }
                header a {
                    color: #fff;
                    text-decoration: none;
                    text-transform: uppercase;
                    font-size: 16px;
                }
                header ul {
                    padding: 0;
                    list-style: none;
                }
                header li {
                    float: right;
                    display: inline;
                    padding: 0 20px 0 20px;
                }
                .showcase {
                    min-height: 400px;
                    background: url('showcase.jpg') no-repeat 0 -400px;
                    text-align: center;
                    color: #fff;
                }
                .showcase h1 {
                    margin-top: 100px;
                    font-size: 55px;
                    margin-bottom: 10px;
                }
                .showcase p {
                    font-size: 20px;
                }
            </style>
        </head>
        <body>
            <header>
                <div class="container">
                    <h1>My Portfolio</h1>
                    <ul>
                        <li><a href="#">Home</a></li>
                        <li><a href="#">About</a></li>
                        <li><a href="#">Projects</a></li>
                        <li><a href="#">Contact</a></li>
                    </ul>
                </div>
            </header>
            <section class="showcase">
                <div class="container">
                    <h1>Welcome to My Portfolio</h1>
                    <p>Check out my projects and get to know more about me.</p>
                </div>
            </section>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    @app.post("/items/")
    def create_item(item: Item):
        items[item.name] = item
        return item

    @app.put("/items/{item_name}")
    def update_item(item_name: str, item: Item):
        if item_name not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        items[item_name] = item
        return item

    @app.delete("/items/{item_name}")
    def delete_item(item_name: str):
        if item_name not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        del items[item_name]
        return {"message": "Item deleted successfully"}
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }
            .container {
                width: 80%;
                margin: auto;
                overflow: hidden;
            }
            header {
                background: #333;
                color: #fff;
                padding-top: 30px;
                min-height: 70px;
                border-bottom: #77aaff 3px solid;
            }
            header a {
                color: #fff;
                text-decoration: none;
                text-transform: uppercase;
                font-size: 16px;
            }
            header ul {
                padding: 0;
                list-style: none;
            }
            header li {
                float: right;
                display: inline;
                padding: 0 20px 0 20px;
            }
            .showcase {
                min-height: 400px;
                background: url('showcase.jpg') no-repeat 0 -400px;
                text-align: center;
                color: #fff;
            }
            .showcase h1 {
                margin-top: 100px;
                font-size: 55px;
                margin-bottom: 10px;
            }
            .showcase p {
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>My Portfolio</h1>
                <ul>
                    <li><a href="#">Home</a></li>
                    <li><a href="#">About</a></li>
                    <li><a href="#">Projects</a></li>
                    <li><a href="#">Contact</a></li>
                </ul>
            </div>
        </header>
        <section class="showcase">
            <div class="container">
                <h1>Welcome to My Portfolio</h1>
                <p>Check out my projects and get to know more about me.</p>
            </div>
        </section>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)