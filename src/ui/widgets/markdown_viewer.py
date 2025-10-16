from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QUrl
import markdown
from markdown.extensions import fenced_code, tables, nl2br
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
import plantuml
import tempfile
import os
import base64
import re


class MarkdownViewer(QTextBrowser):
    """Widget for rendering markdown with PlantUML and syntax highlighting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)

        # Setup font
        font = QFont("Consolas" if os.name == 'nt' else "Monaco")
        font.setPointSize(10)
        self.setFont(font)

        # Initialize PlantUML
        try:
            self.plantuml = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
        except:
            self.plantuml = None

    def set_markdown(self, text: str):
        """Set and render markdown content"""
        if not text:
            self.setHtml("")
            return

        # Process PlantUML blocks first
        text = self._process_plantuml(text)

        # Convert markdown to HTML with extensions
        html = markdown.markdown(
            text,
            extensions=[
                'fenced_code',
                'tables',
                'nl2br',
                'codehilite',
                'sane_lists'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True
                }
            }
        )

        # Process code blocks for syntax highlighting
        html = self._process_code_blocks(html)

        # Wrap in styled HTML
        styled_html = self._create_styled_html(html)
        self.setHtml(styled_html)

    def _process_plantuml(self, text: str) -> str:
        """Process PlantUML code blocks and replace with rendered images"""
        if not self.plantuml:
            return text

        # Find PlantUML blocks
        pattern = r'```plantuml\n(.*?)```'
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in reversed(list(matches)):
            uml_code = match.group(1)
            try:
                # Generate PlantUML diagram
                img_data = self._generate_plantuml_image(uml_code)
                if img_data:
                    # Replace code block with image
                    img_tag = f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%;" />'
                    text = text[:match.start()] + img_tag + text[match.end():]
            except Exception as e:
                # If PlantUML fails, show error
                error_msg = f'<div style="color: red;">PlantUML Error: {str(e)}</div>'
                text = text[:match.start()] + error_msg + text[match.end():]

        return text

    def _generate_plantuml_image(self, uml_code: str) -> str:
        """Generate PlantUML image and return as base64"""
        try:
            # Create temporary file for PlantUML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write('@startuml\n')
                f.write(uml_code)
                f.write('\n@enduml')
                temp_path = f.name

            # Generate image
            output_path = temp_path.replace('.puml', '.png')
            self.plantuml.processes_file(temp_path, outfile=output_path)

            # Read and encode image
            with open(output_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')

            # Cleanup
            os.unlink(temp_path)
            os.unlink(output_path)

            return img_data
        except Exception as e:
            print(f"PlantUML generation failed: {e}")
            return None

    def _process_code_blocks(self, html: str) -> str:
        """Process code blocks for syntax highlighting"""
        # Find code blocks with language specification
        pattern = r'<code class="language-(\w+)">(.*?)</code>'

        def highlight_code(match):
            lang = match.group(1)
            code = match.group(2)

            # Unescape HTML entities
            code = code.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except ClassNotFound:
                try:
                    lexer = guess_lexer(code)
                except:
                    return match.group(0)

            formatter = HtmlFormatter(style='monokai', noclasses=True)
            highlighted = highlight(code, lexer, formatter)
            return highlighted

        html = re.sub(pattern, highlight_code, html, flags=re.DOTALL)
        return html

    def _create_styled_html(self, content: str) -> str:
        """Wrap content in styled HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333;
                    padding: 10px;
                    background-color: #ffffff;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                h3 {{ font-size: 1.25em; }}
                code {{
                    padding: 0.2em 0.4em;
                    margin: 0;
                    font-size: 85%;
                    background-color: rgba(27,31,35,0.05);
                    border-radius: 3px;
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                }}
                pre {{
                    padding: 16px;
                    overflow: auto;
                    font-size: 85%;
                    line-height: 1.45;
                    background-color: #f6f8fa;
                    border-radius: 3px;
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                }}
                pre code {{
                    display: inline;
                    padding: 0;
                    margin: 0;
                    overflow: visible;
                    line-height: inherit;
                    background-color: transparent;
                    border: 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}
                table th, table td {{
                    padding: 6px 13px;
                    border: 1px solid #dfe2e5;
                }}
                table tr {{
                    background-color: #fff;
                    border-top: 1px solid #c6cbd1;
                }}
                table tr:nth-child(2n) {{
                    background-color: #f6f8fa;
                }}
                blockquote {{
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                    margin: 0 0 16px 0;
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                img {{
                    max-width: 100%;
                    box-sizing: content-box;
                    background-color: #fff;
                }}
                .highlight {{
                    margin: 16px 0;
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
