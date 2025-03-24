import asyncio
import json
import os
import csv 
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy
from pydantic import BaseModel, Field

# URL of the website to scrape
URL_TO_SCRAPE = "https://tenders.etimad.sa/Tender/AllTendersForVisitor?PageNumber=1"

# Instruction to the LLM to extract the required fields
INSTRUCTION_TO_LLM = """
Extract the following fields from each tender opportunity, Some fields will show from the card on the outside but most fields are inside of each card opportunity which you will have to go in:
1. Title of the project ("اسم المنافسة")
2. Description ("الغرض من المنافسة")
3. Contract Duration ("مدة العقد")
4. Governmental Entity ("الجهة الحكومية")
5. Questions Deadline ("آخر موعد لإستلام الإستفسارات")
6. Bid Deadline ("آخر موعد لتقديم العروض")
7. Location ("مكان التنفيذ")
8. Date of Publication ("تاريخ النشر")
9. Categories/Tags ("نشاط المنافسة")
"""

# Define a Pydantic model for the extracted data
class TenderOpportunity(BaseModel):
    title: str = Field(..., alias="اسم المنافسة")
    description: str = Field(..., alias="الغرض من المنافسة")
    reference_number: str =Field(..., alias='الرقم المرجعي')
    contract_duration: str = Field(..., alias="مدة العقد")
    governmental_entity: str = Field(..., alias="الجهة الحكومية")
    questions_deadline: str = Field(..., alias="آخر موعد لإستلام الإستفسارات")
    bid_deadline: str = Field(..., alias="آخر موعد لتقديم العروض")
    location: str = Field(..., alias="مكان التنفيذ")
    date_of_publication: str = Field(..., alias="تاريخ النشر")
    categories_tags: str = Field(..., alias="نشاط المنافسة")
    bid_price: str = Field(..., alias="قيمة وثائق المنافسة")
    


async def main():
    # Create LLMConfig with valid parameters
    llm_config = LLMConfig(
        provider="deepseek/deepseek-chat",  # Use supported provider
        api_token=os.getenv("DEEPSEEK_API"),  # Matching API key
    )

    # Configure LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=TenderOpportunity.model_json_schema(),
        extraction_type="schema",
        instruction=INSTRUCTION_TO_LLM,
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",
        extra_args={"temperature": 0.0, "max_tokens": 800},
    )

    # Configure the crawler
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
    )

    # Configure the browser
    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Navigate to the website
        result = await crawler.arun(url=URL_TO_SCRAPE, config=crawl_config)

        if result.success:
            # Parse the extracted content as JSON
            data = json.loads(result.extracted_content)

                # Save to CSV
            csv_file = "tender_opportunities.csv"
            with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Data saved to {csv_file}")
        else:
            print("Error:", result.error_message)

            # Print the extracted data
        #     print("Extracted Tender Opportunities:")
        #     for opportunity in data:
        #         print(json.dumps(opportunity, indent=4, ensure_ascii=False))

        #     # Show LLM usage statistics
        #     llm_strategy.show_usage()
        # else:
        #     print("Error:", result.error_message)


if __name__ == "__main__":
    asyncio.run(main())
