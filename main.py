import asyncio
import json
import os
import csv
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field

# Base URL for scraping (page number will be appended)
BASE_URL = "https://tenders.etimad.sa/Tender/AllTendersForVisitor?PageNumber={page}"

# Instruction to the LLM to extract the required fields
INSTRUCTION_TO_LLM = """
Extract the following fields from each tender opportunity. Some fields are visible on the card, 
but most require opening each tender to view details:
1. Title of the project ("اسم المنافسة")
2. Description ("الغرض من المنافسة")
3. Reference Number ("الرقم المرجعي")
4. Contract Duration ("مدة العقد")
5. Governmental Entity ("الجهة الحكومية")
6. Questions Deadline ("آخر موعد لإستلام الإستفسارات")
7. Bid Deadline ("آخر موعد لتقديم العروض")
8. Location ("مكان التنفيذ")
9. Date of Publication ("تاريخ النشر")
10. Categories/Tags ("نشاط المنافسة")
11. Bid Price ("قيمة وثائق المنافسة")
"""

# Define a Pydantic model for the extracted data
class TenderOpportunity(BaseModel):
    title: str = Field(..., alias="اسم المنافسة")
    description: str = Field(..., alias="الغرض من المنافسة")
    reference_number: str = Field(..., alias='الرقم المرجعي')
    contract_duration: str = Field(..., alias="مدة العقد")
    governmental_entity: str = Field(..., alias="الجهة الحكومية")
    questions_deadline: str = Field(..., alias="آخر موعد لإستلام الإستفسارات")
    bid_deadline: str = Field(..., alias="آخر موعد لتقديم العروض")
    location: str = Field(..., alias="مكان التنفيذ")
    date_of_publication: str = Field(..., alias="تاريخ النشر")
    categories_tags: str = Field(..., alias="نشاط المنافسة")
    bid_price: str = Field(..., alias="قيمة وثائق المنافسة")

async def scrape_page(crawler: AsyncWebCrawler, crawl_config: CrawlerRunConfig, page: int):
    """Scrape a single page of tenders"""
    url = BASE_URL.format(page=page)
    print(f"🔄 Scraping page {page}...")
    result = await crawler.arun(url=url, config=crawl_config)
    
    if result.success:
        data = json.loads(result.extracted_content)
        print(f"✅ Found {len(data)} tenders on page {page}")
        return data
    else:
        print(f"❌ Error scraping page {page}: {result.error_message}")
        return []

async def main():
    # Configure LLM
    llm_config = LLMConfig(
        provider="deepseek/deepseek-chat",
        api_token=os.getenv("DEEPSEEK_API"),
    )

    # Configure LLM extraction strategy with higher limits
    llm_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=TenderOpportunity.model_json_schema(),
        extraction_type="schema",
        instruction=INSTRUCTION_TO_LLM,
        chunk_token_threshold=2000,  # Increased from 1000
        overlap_rate=0.1,  # Small overlap helps with continuity
        apply_chunking=True,
        input_format="markdown",
        extra_args={
            "temperature": 0.0,
            "max_tokens": 2000,  # Increased from 800
        },
    )

    # Configure the crawler with improved settings
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=True,  # Changed to True for better JS support
        remove_overlay_elements=True,
        exclude_external_links=True,
        wait_for_page_idle_sec=10,  # Wait for dynamic content
        scroll_to_load_content=True,  # Scroll to load all items
    )

    # Configure the browser
    browser_cfg = BrowserConfig(
        headless=True,
        verbose=True,
        viewport_width=1280,  # Larger viewport helps with responsive sites
        viewport_height=2000,  # Taller viewport to show more items
    )

    all_tenders = []
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Scrape multiple pages (adjust range as needed)
        for page in range(1, 6):  # Pages 1 through 5
            page_data = await scrape_page(crawler, crawl_config, page)
            all_tenders.extend(page_data)
            
            # Small delay between pages to avoid rate limiting
            await asyncio.sleep(5)

    # Save all collected data to CSV
    if all_tenders:
        csv_file = "tender_opportunities.csv"
        with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=all_tenders[0].keys())
            writer.writeheader()
            writer.writerows(all_tenders)
        
        print(f"\n🎉 Success! Saved {len(all_tenders)} tenders to {csv_file}")
    else:
        print("❌ No tender data was collected")

if __name__ == "__main__":
    asyncio.run(main())