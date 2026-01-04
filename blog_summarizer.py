import os
from crewai import LLM, Agent, Process,Task, Crew


from crewai_tools import FirecrawlScrapeWebsiteTool


llm = LLM(
    provider="google",
    model="models/gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY")
)


# llm2 = LLM(
#     provider="openai",
#     model="deepseek-r1:latest", 
#     base_url="http://localhost:11434/v1",
#     api_key="ollama"
# )

tools = FirecrawlScrapeWebsiteTool(os.environ.get("FIRECRAWL_API_KEY"))

# Agent 1 role:
# basic on the input , website ke correspinding data scrap hokar aaye
    # can say - get the blog text from the url

# Agent 2: role:
# generate the summarry


# Create agents
blog_scraper = Agent(
    name="Blog Scraper",
    role="Web Content Researcher",
    goal="Extract complete and accurate content from blog URLs",
    backstory="You are an expert web researcher specialized in extracting main content from blogs while filtering out ads and navigation elements.",
    verbose=True, # jaise hi agent run karega, yeh text ko bhi print karega terminal mein
    allow_delegation=False, # False means apna task kisi ko delegate matt karna
    llm=llm,
    tools=[tools],
)


# now jo text generate hokar aaya hai, from blog_scapper, blog_summarizer uski summary banakar dega
blog_summarizer = Agent(
    name="Blog Summarizer",
    role="Content Analyst",
    goal="Create concise, informative summaries capturing key points from blog content",
    backstory="You are a skilled content analyst with expertise in distilling complex information into clear summaries.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)


# Define Tasks
def scrape_blog_task(url):
    return Task(
        description=f"Scrape content from the blog at {url} using FirecrawlScrapeWebsiteTool. Extract main article text, filtering out navigation/ads. Always use FirecrawlScrapeWebsiteTool.",
        expected_output="Full text content of the blog post in markdown format",
        agent=blog_scraper,
    )


def summarize_blog_task(scrape_task):
    return Task(
        description="Create comprehensive summary of scraped blog content for generating AI podcast episode",
        expected_output=(
            "Concise summary (500-700 words) with key points, insights, and important details. "
            "The summary will be used to generate an AI podcast episode using a text to speech model. "
            "Create summary suitable for podcast format, focusing on clarity and engagement."
            "Do not include that this is a blog summary or mention any links or URLs."
        ),
        agent=blog_summarizer,
        context=[scrape_task],  # Pass Task object, not string, what data collected by scrape_blog_task, pass it here context
    )


# Create Crew
def create_blog_summary_crew(url):
    scrape_task = scrape_blog_task(url)
    summarize_task = summarize_blog_task(scrape_task)  # Pass task object

    crew = Crew(
        agents=[blog_scraper, blog_summarizer],
        tasks=[scrape_task, summarize_task],
        verbose=True,
        process=Process.sequential,
    )
    return crew


# Run process
def summarize_blog(url):
    crew = create_blog_summary_crew(url)
    result = crew.kickoff()
    return result.raw


# Example usage
if __name__ == "__main__":
    blog_url = input("Enter blog URL: ")
    # https://www.cbsnews.com/news/kennedy-center-christmas-eve-jazz-concert-canceled-after-trump-name-added-to-building/
    # https://www.npr.org/2025/12/29/nx-s1-5653358/the-cautionary-tale-of-a-recovering-day-trading-addict-encore
    # https://towardsdatascience.com/
    summary = summarize_blog(blog_url)

    with open("blog_summary.txt", "w") as f:
        f.write(summary)

    print("\n=== BLOG SUMMARY ===\n", summary)