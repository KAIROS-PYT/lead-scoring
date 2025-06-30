from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import timedelta
from typing import Dict

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Check if API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your OpenAI API key:")
    print("OPENAI_API_KEY=your_api_key_here")
    exit(1)

# Token usage tracking
total_input_tokens = 0
total_output_tokens = 0

def calculate_cost(input_tokens: int, output_tokens: int, usd_to_inr_rate: float = 85.0) -> Dict[str, float]:
    """
    Calculate the cost based on token usage for GPT-4o-mini
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        usd_to_inr_rate: USD to INR conversion rate
    Returns:
        dict: Cost breakdown in USD and INR
    """
    # GPT-4o-mini pricing per 1M tokens
    input_cost_per_1m = 0.15  # $0.15 per 1M input tokens
    output_cost_per_1m = 0.60  # $0.60 per 1M output tokens
    
    input_cost_usd = (input_tokens / 1_000_000) * input_cost_per_1m
    output_cost_usd = (output_tokens / 1_000_000) * output_cost_per_1m
    total_cost_usd = input_cost_usd + output_cost_usd
    
    input_cost_inr = input_cost_usd * usd_to_inr_rate
    output_cost_inr = output_cost_usd * usd_to_inr_rate
    total_cost_inr = total_cost_usd * usd_to_inr_rate
    
    return {
        "usd_to_inr_rate": usd_to_inr_rate,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": round(input_cost_usd, 6),
        "output_cost_usd": round(output_cost_usd, 6),
        "input_cost_inr": round(input_cost_inr, 4),
        "output_cost_inr": round(output_cost_inr, 4),
        "total_cost_usd": round(total_cost_usd, 6),
        "total_cost_inr": round(total_cost_inr, 4)
    }

def seconds_to_hms(seconds_float):
    return str(timedelta(seconds=int(seconds_float))).zfill(8)

def parse_segments(filepath):
    segments = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split("] ", 1)
                if len(parts) == 2:
                    timestamp = parts[0].replace("[", "").replace("]", "")
                    start_sec = float(timestamp.split("-->")[0].strip())
                    text = parts[1]
                    segments.append((start_sec, text))
    return segments

def format_prompt(block):
    joined = "\n".join([f"[{seconds_to_hms(start)}] {text}" for start, text in block])
    return f"""
Below is a transcript of a conversation between a sales agent and a customer. Assign each line to either [Sales Agent] or [Customer] based on the text content and provide it back in the format:

[Speaker][hh:mm:ss] Sentence

Transcript:
{joined}
"""

def call_gpt4o(prompt):
    global total_input_tokens, total_output_tokens
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a transcription analyst."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    # Track token usage
    if hasattr(response, 'usage') and response.usage:
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        print(f"  Block tokens - Input: {input_tokens:,}, Output: {output_tokens:,}")
    
    return response.choices[0].message.content

def segment_and_label(input_txt, output_txt, block_size=15):
    global total_input_tokens, total_output_tokens
    
    # Reset token counters
    total_input_tokens = 0
    total_output_tokens = 0
    
    segments = parse_segments(input_txt)
    total_blocks = (len(segments) + block_size - 1) // block_size
    successful_blocks = 0
    
    print(f"🚀 Starting Speaker Segmentation Process...")
    print(f"📊 Processing {len(segments)} segments in {total_blocks} blocks...")
    print("="*60)
    
    with open(output_txt, "w", encoding="utf-8") as out:
        for i in range(0, len(segments), block_size):
            block_num = (i // block_size) + 1
            block = segments[i:i + block_size]
            prompt = format_prompt(block)
            try:
                print(f"🔄 Processing block {block_num}/{total_blocks}...")
                result = call_gpt4o(prompt)
                out.write(result.strip() + "\n\n")
                successful_blocks += 1
            except Exception as e:
                print(f"❌ Error in block {block_num}: {e}")
                # Write the original block with error marker
                error_block = "\n".join([f"[ERROR][{seconds_to_hms(start)}] {text}" for start, text in block])
                out.write(error_block + "\n\n")
    
    print("\n" + "="*60)
    print("📊 SEGMENTATION ANALYSIS COMPLETE")
    print("="*60)
    print(f"✅ Processing complete: {successful_blocks}/{total_blocks} blocks successful")
    
    # Calculate and display cost analysis
    cost_analysis = calculate_cost(total_input_tokens, total_output_tokens)
    
    print(f"\n💰 TOKEN USAGE & COST ANALYSIS")
    print("-"*40)
    print(f"📥 Total Input Tokens:  {cost_analysis['input_tokens']:,}")
    print(f"📤 Total Output Tokens: {cost_analysis['output_tokens']:,}")
    print(f"🔢 Total Tokens:        {cost_analysis['total_tokens']:,}")
    
    print(f"\n💵 COST BREAKDOWN (USD)")
    print("-"*40)
    print(f"Input Cost:  ${cost_analysis['input_cost_usd']:.6f}")
    print(f"Output Cost: ${cost_analysis['output_cost_usd']:.6f}")
    print(f"Total Cost:  ${cost_analysis['total_cost_usd']:.6f}")
    
    print(f"\n💸 COST BREAKDOWN (INR @ {cost_analysis['usd_to_inr_rate']})")
    print("-"*40)
    print(f"Input Cost:  ₹{cost_analysis['input_cost_inr']:.4f}")
    print(f"Output Cost: ₹{cost_analysis['output_cost_inr']:.4f}")
    print(f"Total Cost:  ₹{cost_analysis['total_cost_inr']:.4f}")
    
    # Save cost analysis to JSON file
    cost_file = output_txt.replace('.txt', '_SEGMENTATION_COST.json')
    with open(cost_file, 'w', encoding='utf-8') as f:
        json.dump({
            "process": "Speaker Segmentation",
            "model": "gpt-4o-mini",
            "blocks_processed": successful_blocks,
            "total_blocks": total_blocks,
            "success_rate": f"{(successful_blocks/total_blocks*100):.1f}%",
            "cost_analysis": cost_analysis
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Cost analysis saved to: {cost_file}")
    print("="*60)
    
    return cost_analysis

if __name__ == "__main__":
    input_path = "CALL_1117711_DIAa627c702b059f843e7a3570e994aef86_1747605641_segments.txt"
    output_path = "CALL_1117711_speaker_segmented.txt"
    
    print("🎯 SPEAKER SEGMENTATION WITH COST TRACKING")
    print("="*60)
    
    cost_analysis = segment_and_label(input_path, output_path)
    
    print(f"\n📁 Speaker-labeled output saved to: {output_path}")
    print("🎉 Segmentation process completed successfully!")
    print("="*60)

