import os
import smtplib
import scraper
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

subscribers = pd.read_csv('docs/subscribers.csv')

url = 'https://techcrunch.com/category/artificial-intelligence/'
news_title, news_content, content_link = scraper.get_content(url)

# Club and Department News
club_news = pd.read_csv('docs/club_news.csv')
dept_news = pd.read_csv('docs/dept_news.csv')

recent_club_news = club_news.iloc[-1]
recent_dept_news = dept_news.iloc[-1]

current_date = datetime.now()

date_split_club = [int(x) for x in recent_club_news['Date'].split('/')]
date_split_dept = [int(x) for x in recent_dept_news['Date'].split('/')]

recent_club_news_date = datetime(date_split_club[2], date_split_club[1], date_split_club[0]) 
recent_dept_news_date = datetime(date_split_dept[2], date_split_dept[1], date_split_dept[0]) 

club_news_difference = current_date - recent_club_news_date
dept_news_difference = current_date - recent_dept_news_date

# Helper function to clean text
def clean_text(text):
    """Remove or replace unicode characters that cause encoding issues"""
    replacements = {
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\xa0': ' ',    # Non-breaking space
        '\u2026': '...', # Ellipsis
    }
    for unicode_char, ascii_char in replacements.items():
        text = str(text).replace(unicode_char, ascii_char)
    return text

# Build HTML formatted message
final_message = f"""<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: white; }}
.header {{ text-align: center; border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
.section-title {{ color: #4CAF50; font-size: 20px; margin-top: 30px; margin-bottom: 15px; }}
.quote {{ background-color: #f9f9f9; border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0; font-style: italic; }}
.footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; color: #777; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1 style="color: #4CAF50; margin: 0;">NexusBytes Newsletter</h1>
<p style="color: #777; font-size: 14px;">{datetime.now().strftime("%B %d, %Y")}</p>
</div>

<h2 class="section-title">AI News of the Week</h2>
<h3>{clean_text(news_title)}</h3>
"""

# Limit no.of Paragraphs
max_paragraphs = 5

for i, paragraph in enumerate(news_content):
    if i >= max_paragraphs:
        break
    final_message += f'<p style="margin-bottom: 15px;">{clean_text(paragraph)}</p>\n'

# Add "Read full article" link if there are more paragraphs
if len(news_content) > max_paragraphs:
    final_message += f'<p style="margin-top: 15px; margin-bottom: 20px;"><a href="{content_link}" style="color: #4CAF50; text-decoration: none; font-weight: bold; font-size: 16px;">📰 Read the full article →</a></p>\n'

# Add club news if recent
if club_news_difference.days < 7:
    club_content_formatted = clean_text(recent_club_news['Content']).replace('\n', '<br>')
    final_message += f"""
<h2 class="section-title">Club News</h2>
<p>{club_content_formatted}</p>
"""

# Add department news if recent
if dept_news_difference.days < 7:
    dept_content_formatted = clean_text(recent_dept_news['Content']).replace('\n', '<br>')
    final_message += f"""
<h2 class="section-title">Department News</h2>
<p>{dept_content_formatted}</p>
"""

# Add quote and footer
final_message += """
<div class="quote">
"The best way to predict the future is to invent it." - Alan Kay
</div>

<div class="footer">
<p><strong>Thank you for reading!</strong></p>
<p>Stay curious and keep innovating!</p>
</div>
</div>
</body>
</html>
"""

sender_mail = os.getenv("EMAIL_USER")
sender_password = os.getenv("EMAIL_PASS")

for idx, row in subscribers.iterrows():
    receiver_mail = row['email_address']

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_mail, sender_password)

    # Create MIME message for HTML email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"NexusBytes Newsletter - {datetime.now().strftime('%B %d, %Y')}"
    msg['From'] = sender_mail
    msg['To'] = receiver_mail

    # Attach HTML content
    html_part = MIMEText(final_message, 'html')
    msg.attach(html_part)

    # Send the message
    s.sendmail(sender_mail, receiver_mail, msg.as_string())
    s.quit()
