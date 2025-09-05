from crewai import Agent, Task, Crew, Process
from tools import TwitterTools
from dotenv import load_dotenv
import os
from litellm import completion
from textwrap import dedent

load_dotenv()

# Configure your LLM
# You can use any model supported by LiteLLM (e.g., "gpt-4", "claude-3-opus", "gemini/gemini-pro")
# Make sure you have the corresponding API key set in your .env file
llm_model = os.getenv("LITELLM_MODEL", "gpt-4")

# Define Agents
class FinancialContentCrew:
    def __init__(self):
        self.llm_config = {"model": llm_model}

    def run(self):
        # Define agents
        keyword_generator = Agent(
            role='Keyword Generator',
            goal='Generate relevant keywords for searching X (Twitter) creators focused on US financial markets.',
            backstory='An expert in financial news and social media trends, capable of identifying key terms and phrases related to the US stock market, economy, and investment strategies.',
            verbose=True,
            allow_delegation=True, # Allow delegation to other agents
            llm=self.llm_config, # Use litellm configured LLM
        )

        user_search_agent = Agent(
            role='X User Searcher',
            goal='Find X (Twitter) creators who post about US financial markets, have more than 5000 followers, and have posted more than 5 tweets in the last 2 weeks.',
            backstory='A diligent social media analyst with expertise in filtering and identifying influential users based on specific criteria and using the X (Twitter) API.',
            verbose=True,
            allow_delegation=True, # Allow delegation to keyword generator if needed
            tools=[TwitterTools.search_tweets, TwitterTools.search_x_users],
            llm=self.llm_config,
        )

        result_formatter = Agent(
            role='Result Formatter',
            goal='Format the filtered X (Twitter) user data into a JSON file, including overall statistics.',
            backstory='A meticulous data engineer specialized in structuring and presenting social media data in a clear, concise, and statistically informative JSON format.',
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config,
        )

        # Define tasks
        generate_keywords_task = Task(
            description='Generate a comprehensive list of search keywords related to US financial markets, including terms for stocks, bonds, commodities, cryptocurrencies, economic indicators, investment strategies, and popular financial news topics. Focus on terms that active X (Twitter) creators would use.',
            agent=keyword_generator,
            expected_output='A comma-separated list of highly relevant search keywords.',
        )

        search_and_filter_users_task = Task(
            description=dedent("""Using the generated keywords, search X (Twitter) for relevant tweets. 
                From these tweets, identify unique usernames. Then, for each unique username, retrieve their detailed profile information 
                including follower count and recent tweet activity (approximated as avg. posts per week). 
                Filter these users based on the following criteria:
                - More than 5000 followers
                - More than 5 tweets in the last 2 weeks (approximated by avg. posts per week > 2.5, as 5 tweets in 2 weeks means 2.5 per week)
                
                Return a JSON string representing a dictionary with three keys: 
                'total_users_found' (integer),
                'total_users_filtered' (integer),
                and 'filtered_users' (a list of user dictionaries, each containing: username, displayname, followersCount, url, and avg_posts_per_week).
                """),
            agent=user_search_agent,
            expected_output=dedent("""A JSON string representing a dictionary with three keys: 
                'total_users_found' (integer),
                'total_users_filtered' (integer),
                and 'filtered_users' (a list of user dictionaries, each containing: username, displayname, followersCount, url, and avg_posts_per_week).
                """),
            context=[generate_keywords_task]
        )

        format_results_task = Task(
            description=dedent("""Take the list of filtered user dictionaries and format them into a final JSON output. 
                The JSON should contain a list of 'users' with the following fields for each user: 
                'url', 'username', 'followers', 'avg_posts_per_week'.
                Also, include overall statistics:
                - 'processing_time': The total time taken for the entire crew to run (this will be calculated outside the agent and passed in if possible, otherwise marked as N/A).
                - 'total_users_found': The total number of unique users initially found before filtering.
                - 'total_users_filtered': The total number of users that met the filtering criteria.
                Save the final JSON output to a file named 'financial_creators.json'.
                """),
            agent=result_formatter,
            expected_output='A JSON file named financial_creators.json with the formatted results and statistics.',
            context=[search_and_filter_users_task]
        )

        crew = Crew(
            agents=[keyword_generator, user_search_agent, result_formatter],
            tasks=[generate_keywords_task, search_and_filter_users_task, format_results_task],
            verbose=2,
            process=Process.sequential,
        )

        import time
        start_time = time.time()
        try:
            result = crew.kickoff()
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            # Parse the result from the search_and_filter_users_task
            import json
            try:
                parsed_search_results = json.loads(result)
                total_users_found = parsed_search_results.get("total_users_found", 0)
                total_users_filtered = parsed_search_results.get("total_users_filtered", 0)
                filtered_users_list = parsed_search_results.get("filtered_users", [])
            except json.JSONDecodeError:
                print("Error: Could not decode JSON from search_and_filter_users_task result. Setting statistics to N/A.")
                total_users_found = "N/A"
                total_users_filtered = "N/A"
                filtered_users_list = []
            
            final_output_data = {
                "overall_statistics": {
                    "processing_time": f"{processing_time} seconds",
                    "total_users_found": total_users_found,
                    "total_users_filtered": total_users_filtered
                },
                "users": filtered_users_list # This now directly uses the filtered_users list
            }

            output_filename = "financial_creators.json"
            with open(output_filename, "w") as f:
                json.dump(final_output_data, f, indent=4)
            
            print(f"Results saved to {output_filename}")
            return json.dumps(final_output_data, indent=4) # Return the final JSON string, not just the raw result

        except Exception as e:
            print(f"An error occurred during the CrewAI kickoff: {e}")
            return f"CrewAI execution failed: {e}"

if __name__ == "__main__":
    print("## Starting Financial Content Crew")
    financial_crew = FinancialContentCrew()
    result = financial_crew.run()
    print("\n\n## Crew Work Results:")
    print(result)
