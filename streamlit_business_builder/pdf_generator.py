from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime
import os
import re

# PDF text translations
PDF_TRANSLATIONS = {
    "en": {
        "report_title": "Business Strategy Report",
        "initial_idea": "Initial Business Idea",
        "clarity_analysis": "Clarity Analysis",
        "niche_strategy": "Niche Strategy",
        "action_plan": "Action Plan",
        "business_strategy": "Business Strategy",
        "todo_list": "Action Items",
        "table_of_contents": "Table of Contents",
        "page": "Page",
        "generated_on": "Generated on",
        "confidential": "CONFIDENTIAL"
    },
    "nl": {
        "report_title": "Business Strategie Rapport",
        "initial_idea": "Initieel Business Idee",
        "clarity_analysis": "Helderheidsanalyse",
        "niche_strategy": "Niche Strategie",
        "action_plan": "Actieplan",
        "business_strategy": "Business Strategie",
        "todo_list": "Actiepunten",
        "table_of_contents": "Inhoudsopgave",
        "page": "Pagina",
        "generated_on": "Gegenereerd op",
        "confidential": "VERTROUWELIJK"
    }
}

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self._texts = kwargs.get('texts', PDF_TRANSLATIONS['en'])

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.draw_header_footer()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page = f"{self._texts['page']} {self._pageNumber} / {page_count}"
        self.setFont("Helvetica", 9)
        self.drawRightString(200*mm, 10*mm, page)

    def draw_header_footer(self):
        # Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawString(72, letter[1] - 30, self._texts['confidential'])
        
        # Date in header
        date_str = f"{self._texts['generated_on']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.drawRightString(letter[0] - 72, letter[1] - 30, date_str)
        
        # Line under header
        self.setStrokeColor(colors.HexColor('#CCCCCC'))
        self.line(72, letter[1] - 40, letter[0] - 72, letter[1] - 40)
        
        # Line above footer
        self.line(72, 50, letter[0] - 72, 50)

def create_cover_page(elements, title_style, texts, username):
    # Logo (if exists)
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=2*inch, height=1*inch))
    
    elements.append(Spacer(1, 2*inch))
    
    # Title
    elements.append(Paragraph(texts["report_title"], title_style))
    elements.append(Spacer(1, inch))
    
    # Date and user
    date_style = ParagraphStyle(
        'DateStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"{texts['generated_on']}: {datetime.now().strftime('%Y-%m-%d')}", date_style))
    elements.append(Paragraph(f"Generated for: {username}", date_style))
    
    elements.append(PageBreak())

def create_table_of_contents(elements, heading_style, texts, sections):
    elements.append(Paragraph(texts["table_of_contents"], heading_style))
    elements.append(Spacer(1, 20))
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=12,
        leading=24
    )
    
    for section, page in sections:
        elements.append(Paragraph(f"{section}{'.'*40}{page}", toc_style))
    
    elements.append(PageBreak())

def clean_text(text):
    # First, normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove markdown headers while preserving structure
    text = re.sub(r'#{1,6}\s*(.*?)\n', r'\1\n', text)
    
    # Remove asterisks while preserving the text
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    
    # Convert bullet points to proper format
    text = re.sub(r'^\s*[-•]\s*', '\n• ', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'---+', '\n', text)
    
    # Handle sections with numbers (e.g., "1.", "2.", etc.)
    text = re.sub(r'(\d+\.\s+)', r'\n\1', text)
    
    # Fix spacing around bullet points
    text = re.sub(r'([.!?])\s*\n\s*•', r'\1\n\n•', text)
    
    # Ensure proper spacing between sections
    text = re.sub(r'([.!?])\s*\n\s*(\d+\.)', r'\1\n\n\2', text)
    
    # Fix multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Fix multiple newlines while preserving paragraph structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Split into paragraphs and clean each one
    paragraphs = []
    current_paragraph = []
    
    for line in text.split('\n'):
        line = line.strip()
        if line:
            if line.startswith('•') and current_paragraph:
                # Start a new paragraph for bullet points
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                current_paragraph = [line]
            elif line.startswith('•'):
                current_paragraph.append(line)
            elif any(line.startswith(str(i) + '.') for i in range(1, 10)):
                # Start a new paragraph for numbered sections
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                current_paragraph = [line]
            else:
                current_paragraph.append(line)
        elif current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    # Join paragraphs with proper spacing
    return '\n\n'.join(p.strip() for p in paragraphs if p.strip())

def format_text_to_paragraphs(text):
    # Clean the text first
    text = clean_text(text)
    # Split text into paragraphs and preserve line breaks
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        # Replace single newlines with <br/> for line breaks within paragraphs
        para = para.strip().replace('\n', '<br/>')
        if para:
            formatted_paragraphs.append(para)
    
    return formatted_paragraphs

def create_pdf_report(filename_base, user_input, clarity_response, niche_response, action_response, final_response, language="en", username="User"):
    """Create a professionally formatted PDF report"""
    pdf_filename = f"{filename_base}.pdf"
    
    # Get translations
    texts = PDF_TRANSLATIONS[language]
    
    # Document setup
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#283593'),
        borderColor=colors.HexColor('#283593'),
        borderWidth=1,
        borderPadding=8,
        borderRadius=5
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,  # Increased line spacing
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        firstLineIndent=20  # Add paragraph indentation
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=35,
        firstLineIndent=0,
        spaceBefore=3,
        spaceAfter=3
    )

    # Build content
    elements = []
    
    # Cover page and TOC
    create_cover_page(elements, title_style, texts, username)
    create_table_of_contents(elements, heading_style, texts, [(texts["initial_idea"], "1"), (texts["business_strategy"], "2")])
    
    # Initial Business Idea
    elements.append(Paragraph(texts["initial_idea"], heading_style))
    elements.append(Paragraph(clean_text(user_input), body_style))
    elements.append(PageBreak())
    
    # Business Strategy
    elements.append(Paragraph(texts["business_strategy"], heading_style))
    strategy_text = final_response.split('TO-DO:')[0] if 'TO-DO:' in final_response else final_response
    
    # Process each paragraph of the strategy text
    for para in clean_text(strategy_text).split('\n\n'):
        if para.strip():
            if para.strip().startswith('•'):
                elements.append(Paragraph(para.strip(), bullet_style))
            else:
                elements.append(Paragraph(para.strip(), body_style))
            elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # Action Items (TO-DO list)
    if 'TO-DO:' in final_response:
        elements.append(Paragraph(texts["todo_list"], heading_style))
        todo_text = final_response.split('TO-DO:')[1].strip()
        todo_items = [x.strip() for x in clean_text(todo_text).split('\n') if x.strip()]
        
        for item in todo_items:
            if item.startswith('•'):
                item = item[1:].strip()
            elements.append(Paragraph(f"• {item}", bullet_style))
            elements.append(Spacer(1, 3))

    # Build PDF
    doc.build(elements, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, texts=texts, **kwargs))
    
    return pdf_filename 