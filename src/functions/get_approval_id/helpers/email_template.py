def get_email_template(name, action, error=None):
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>Visit Approved</title>
                <style>
                    body {{
                        font-family: Cambria, Cochin, Georgia, Times, "Times New Roman",
                            serif;
                        display: flex;
                        justify-content: center;
                        background-color: #f0f0f0;
                    }}
        
                    h1 {{
                        color: black;
                        font-size: 1rem;
                    }}
                    p {{
                        color: #ae0000;
                    }}
                    img {{
                        margin: 0px auto;
                        height: 50px;
                        margin: 20px auto;
                    }}
                    .page {{
                        display: flex;
                        flex-direction: column;
                    }}
                    .container {{
                        background-color: #fff;
                        padding: 30px 30px;
                        border-radius: 5px;
                        text-align: center;
                        width: auto;
                        height: auto;
                        margin: 10px 15px;
                        box-shadow: rgba(0, 0, 0, 0.16) 0px 3px 6px,
                            rgba(0, 0, 0, 0.23) 0px 3px 6px;
                    }}
                </style>
            </head>
            <body>
                <div class="page">
                    <img
                        src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Watchguard_logo.svg/2560px-Watchguard_logo.svg.png"
                        alt="Logo"
                    />
                    <div class="container">
                        {f'<h1>{action}</h1><p>Visitor - {name}</p><p>Thank You!</p>' if not error else f'<h1>{error}</h1>'}
                    </div>
                </div>
            </body>
        </html>
        
            """
    return html_content
