import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import openai  # Optional: Only needed if you use GPT-based suggestions

# =========================
# CONFIGURE YOUR OPENAI KEY
# =========================
# If you want the AI "SEO Genie" to work, uncomment and set your key:
# openai.api_key = "YOUR-OPENAI-API-KEY"

def fetch_html(url):
    """
    Fetch the HTML content of a given URL.
    """
    try:
        # Make sure the URL starts with http or https
        if not url.startswith("http"):
            url = "https://" + url
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            st.warning("Could not retrieve the page. Check URL or status code.")
            return None
    except Exception as e:
        st.error(f"Error fetching the URL: {e}")
        return None

def extract_onpage_data(html):
    """
    Extract relevant on-page SEO elements from the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    title_tag = soup.find('title').text.strip() if soup.find('title') else ""
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag and meta_desc_tag.get('content') else ""
    
    # Collect h1, h2, h3...
    headers = {}
    for h in ['h1', 'h2', 'h3', 'h4']:
        headers[h] = [tag.get_text(strip=True) for tag in soup.find_all(h)]
    
    # For keyword density: parse the visible text from <p>, <span>, etc.
    texts = soup.get_text(separator=' ', strip=True)
    
    return title_tag, meta_desc, headers, texts

def calculate_seo_score(title, meta_desc, headers):
    """
    Very rough, example-based scoring function for demonstration purposes.
    """
    score = 0
    # Title length: ideal ~ 50-60
    if 50 <= len(title) <= 60:
        score += 20
    elif 30 <= len(title) < 50 or 60 < len(title) <= 70:
        score += 10
    else:
        score += 5
    
    # Description length: ideal ~ 120-160
    if 120 <= len(meta_desc) <= 160:
        score += 20
    elif 80 <= len(meta_desc) < 120 or 160 < len(meta_desc) <= 200:
        score += 10
    else:
        score += 5
    
    # Presence of H1
    if len(headers['h1']) > 0:
        score += 20
    else:
        score += 0
    
    # Some weighting for h2, h3 usage
    h2_count = len(headers['h2'])
    h3_count = len(headers['h3'])
    # This is arbitrary, just for a basic demonstration
    if h2_count >= 1:
        score += 10
    if h3_count >= 2:
        score += 10
    
    # Minimum score is 0, maximum is 60 in this example
    return min(score, 60)

def generate_wordcloud(text):
    """
    Generate and display a word cloud from the given text.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=50).generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

def get_top_keywords(text, top_n=10):
    """
    Very simplistic approach to get top words.
    """
    # Remove non-alpha characters, convert to lowercase
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    
    # Sort by frequency
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_freq[:top_n]

def call_seo_genie(page_title, meta_desc):
    """
    Call an AI model to generate an SEO recommendation in a whimsical style.
    """
    # Example prompt if using GPT
    prompt = f"""
    You are an SEO Genie with a fun, witty persona. 
    The user has a webpage with title: "{page_title}" 
    and meta description: "{meta_desc}". 
    Give them 2-3 punchy suggestions to improve their SEO, in a friendly, genie-like tone.
    """
    
    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        st.warning("OpenAI API error or missing API key. Showing static advice instead.")
        return ("1. Ensure your title is eye-catching and includes your main keyword.\n"
                "2. Spice up your meta description with a strong call-to-action.\n"
                "3. Add more engaging headings to structure your content effectively.")

# ================
# STREAMLIT APP
# ================

def main():
    st.title("🔮 SEO Genie: Magic On-Page Analysis & Comparison")
    st.markdown("**Enter two websites below for a delightful SEO check and see how they compare.**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        url1 = st.text_input("Enter your Website URL", "example.com")
    with col2:
        url2 = st.text_input("Enter Competitor Website URL (optional)", "competitor.com")
    
    if st.button("Analyze"):
        if url1:
            st.subheader("Your Site Analysis")
            html1 = fetch_html(url1)
            if html1:
                title1, desc1, headers1, texts1 = extract_onpage_data(html1)
                score1 = calculate_seo_score(title1, desc1, headers1)
                
                st.markdown(f"**Title:** {title1}")
                st.markdown(f"**Meta Description:** {desc1}")
                st.markdown(f"**H1 Tags:** {headers1['h1']}")
                
                # Show SEO Score with a progress bar
                st.metric("SEO Health Score", score1, "/60")
                seo_progress = score1 / 60
                st.progress(seo_progress)
                
                # WordCloud & top keywords
                st.markdown("### Keyword Density")
                generate_wordcloud(texts1)
                top_keywords_1 = get_top_keywords(texts1, top_n=10)
                st.write("Top Keywords (approx.):", top_keywords_1)
                
                # SEO Genie suggestions
                st.markdown("### SEO Genie’s Recommendations")
                suggestions = call_seo_genie(title1, desc1)
                st.info(suggestions)
                
        if url2:
            st.subheader("Competitor Site Analysis")
            html2 = fetch_html(url2)
            if html2:
                title2, desc2, headers2, texts2 = extract_onpage_data(html2)
                score2 = calculate_seo_score(title2, desc2, headers2)
                
                st.markdown(f"**Title:** {title2}")
                st.markdown(f"**Meta Description:** {desc2}")
                st.markdown(f"**H1 Tags:** {headers2['h1']}")
                
                st.metric("SEO Health Score", score2, "/60")
                seo_progress2 = score2 / 60
                st.progress(seo_progress2)
                
                # WordCloud & top keywords for competitor
                st.markdown("### Keyword Density")
                generate_wordcloud(texts2)
                top_keywords_2 = get_top_keywords(texts2, top_n=10)
                st.write("Top Keywords (approx.):", top_keywords_2)
                
                # SEO Genie suggestions for competitor
                st.markdown("### SEO Genie’s Competitor Tips")
                suggestions2 = call_seo_genie(title2, desc2)
                st.info(suggestions2)
                
        # Overall comparison
        if url1 and url2:
            st.title("🎉 Comparison Summary")
            diff_score = (score1 - score2)
            if diff_score > 0:
                st.success(f"Your site leads by {diff_score} points!")
            elif diff_score < 0:
                st.warning(f"Competitor leads by {-diff_score} points!")
            else:
                st.info("It’s a tie! Both sites have the same SEO Health Score.")

    st.markdown("---")
    st.write("**Pro Tip**: Fine-tune your content, meta tags, headings, and keep an eye on competitor strategies. "\
             "Use the magic of the SEO Genie to stay ahead!")

if __name__ == "__main__":
    main()
