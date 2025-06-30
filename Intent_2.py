from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime, timedelta
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

# Global token tracking
token_usage = {
    'total_input_tokens': 0,
    'total_output_tokens': 0,
    'api_calls': 0,
    'analysis_calls': 0,
    'segment_calls': 0
}

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

def count_tokens(text: str) -> int:
    """Simple token counter (approximate for gpt-4o-mini)"""
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)

def calculate_cost(input_tokens: int, output_tokens: int, usd_to_inr_rate: float = 85.0) -> dict:
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

def parse_line(line):
    """Parse a line to extract role and timestamp."""
    try:
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and error markers
            return None, None
            
        # Find the role (first bracket pair)
        role_start = line.find('[') + 1
        role_end = line.find(']')
        if role_start == 0 or role_end == -1:
            return None, None
        role = line[role_start:role_end]

        # Find the timestamp (second bracket pair)
        time_start = line.find('[', role_end) + 1
        time_end = line.find(']', time_start)
        if time_start == 0 or time_end == -1:
            return None, None
        
        time_str = line[time_start:time_end]
        timestamp = datetime.strptime(time_str, "%H:%M:%S")

        return role, timestamp
    except Exception as e:
        # Debug: uncomment the line below to see parsing errors
        # print(f"Parse error: {e} for line: {line[:50]}...")
        return None, None

def calculate_talk_times(file_path):
    """Calculate talk times for each speaker in the conversation."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    talk_times = {'Customer': timedelta(), 'Sales Agent': timedelta()}
    parsed = []

    for line in lines:
        role, timestamp = parse_line(line)
        if role and timestamp:
            parsed.append((role, timestamp))

    for i in range(len(parsed) - 1):
        current_role, current_time = parsed[i]
        next_role, next_time = parsed[i + 1]
        duration = next_time - current_time
        talk_times[current_role] += duration

    # Handle the last line (assume default 1 second duration)
    if parsed:
        talk_times[parsed[-1][0]] += timedelta(seconds=1)

    return talk_times

def extract_customer_lines(file_path):
    """Extract only customer lines from the speaker-segmented transcript."""
    customer_lines = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith('[Customer]['):
            # Extract timestamp and text
            try:
                # Find the second bracket pair for timestamp
                first_bracket_end = line.find(']')
                timestamp_start = line.find('[', first_bracket_end) + 1
                timestamp_end = line.find(']', timestamp_start)
                timestamp = line[timestamp_start:timestamp_end]
                
                # Extract the spoken text
                text_start = line.find('] ', timestamp_end) + 2
                text = line[text_start:]
                
                customer_lines.append({
                    'timestamp': timestamp,
                    'text': text
                })
            except:
                continue
    
    return customer_lines

def analyze_customer_intent_and_sentiment(customer_lines):
    """Analyze customer intent and sentiment using OpenAI."""
    global token_usage
    
    # Combine all customer statements
    combined_text = "\n".join([f"[{line['timestamp']}] {line['text']}" for line in customer_lines])
    
    system_message = "You are an expert sales analyst specializing in customer intent and sentiment analysis for travel bookings. Provide detailed, accurate analysis based on customer behavior patterns."
    
    prompt = f"""
Analyze the following customer statements from a sales call transcript. The customer is discussing a travel package to Bali.

Please provide a comprehensive analysis in JSON format with the following structure:

{{
    "overall_intent": "string describing the main customer intent",
    "purchase_likelihood": "High/Medium/Low",
    "sentiment_analysis": {{
        "overall_sentiment": "Positive/Negative/Neutral",
        "confidence_score": "percentage (0-100)",
        "sentiment_indicators": ["list of words/phrases that indicate sentiment"]
    }},
    "key_interests": ["list of things the customer is most interested in"],
    "concerns_objections": ["list of customer concerns or objections"],
    "buying_signals": ["list of positive buying signals detected"],
    "decision_stage": "Awareness/Consideration/Decision/Post-Decision",
    "commitment_level": "High/Medium/Low",
    "detailed_analysis": "paragraph explaining the analysis"
}}

Important sentiment indicators:
- POSITIVE signals: words like "visa", "passport", "appointment", "booking", "confirm", "let's do it", "sounds good", "I like", "perfect", "great"
- ENGAGEMENT signals: asking detailed questions, discussing specific dates, comparing options
- NEGATIVE signals: "expensive", "too much", "not sure", "maybe", "I need to think", "budget constraints"

Customer Statements:
{combined_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # Track actual token usage from API response
        if hasattr(response, 'usage') and response.usage:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            token_usage['total_input_tokens'] += input_tokens
            token_usage['total_output_tokens'] += output_tokens
            token_usage['analysis_calls'] += 1
            print(f"  🔍 Overall Analysis - Input: {input_tokens:,}, Output: {output_tokens:,}")
        
        token_usage['api_calls'] += 1
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error analyzing customer intent: {e}")
        return None

def analyze_conversation_flow(customer_lines):
    """Analyze how customer sentiment evolves throughout the conversation."""
    global token_usage
    
    # Split into conversation segments (every 5 minutes)
    segments = []
    current_segment = []
    
    for line in customer_lines:
        timestamp = line['timestamp']
        # Convert timestamp to minutes
        time_parts = timestamp.split(':')
        minutes = int(time_parts[1])
        
        # Group by 5-minute segments
        segment_number = minutes // 5
        
        if not segments or len(segments) <= segment_number:
            segments.extend([[] for _ in range(segment_number + 1 - len(segments))])
        
        segments[segment_number].append(line)
    
    # Analyze each segment
    segment_analysis = []
    for i, segment in enumerate(segments):
        if not segment:
            continue
            
        segment_text = " ".join([line['text'] for line in segment])
        
        system_message = "You are a conversation analyst. Respond only with valid JSON."
        prompt = f"""
Analyze this conversation segment for customer sentiment and engagement level.
Respond with ONLY a JSON object:

{{
    "sentiment": "Positive/Negative/Neutral",
    "engagement": "High/Medium/Low",
    "key_points": ["main points discussed"],
    "buying_signals": "Yes/No"
}}

Customer statements in this segment:
{segment_text}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Track actual token usage from API response
            if hasattr(response, 'usage') and response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                token_usage['total_input_tokens'] += input_tokens
                token_usage['total_output_tokens'] += output_tokens
                token_usage['segment_calls'] += 1
                print(f"  📊 Segment {i+1} - Input: {input_tokens:,}, Output: {output_tokens:,}")
            
            token_usage['api_calls'] += 1
            
            segment_analysis.append({
                "segment": i + 1,
                "time_range": f"{i*5}-{(i+1)*5} minutes",
                "analysis": response.choices[0].message.content
            })
            
        except Exception as e:
            print(f"Error analyzing segment {i+1}: {e}")
            continue
    
    return segment_analysis

def clean_and_structure_data(overall_analysis, segment_analysis, total_statements, talk_times):
    """Clean and restructure the analysis data for better readability."""
    global token_usage
    
    # Clean the overall analysis
    if overall_analysis.startswith('```json\n'):
        json_start = overall_analysis.find('{')
        json_end = overall_analysis.rfind('}') + 1
        clean_json_str = overall_analysis[json_start:json_end]
        overall_analysis_clean = json.loads(clean_json_str)
    else:
        overall_analysis_clean = json.loads(overall_analysis)
    
    # Clean the conversation flow analysis
    conversation_flow = []
    for segment in segment_analysis:
        try:
            analysis_data = json.loads(segment['analysis'])
            clean_segment = {
                "segment": segment['segment'],
                "time_range": segment['time_range'],
                "analysis": analysis_data
            }
            conversation_flow.append(clean_segment)
        except json.JSONDecodeError:
            continue
    
    # Calculate actual call duration from talk times
    total_duration = sum(talk_times.values(), timedelta())
    actual_minutes = int(total_duration.total_seconds() // 60)
    actual_seconds = int(total_duration.total_seconds() % 60)
    
    # Calculate cost breakdown
    cost_breakdown = calculate_cost(
        token_usage['total_input_tokens'], 
        token_usage['total_output_tokens']
    )
    
    # Create the clean structure
    clean_data = {
        "call_metadata": {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_customer_statements": total_statements,
            "actual_call_duration": f"{actual_minutes}m {actual_seconds}s",
            "talk_time_breakdown": {
                "customer_time": f"{int(talk_times['Customer'].total_seconds() // 60)}m {int(talk_times['Customer'].total_seconds() % 60)}s",
                "agent_time": f"{int(talk_times['Sales Agent'].total_seconds() // 60)}m {int(talk_times['Sales Agent'].total_seconds() % 60)}s",
                "customer_percentage": round((talk_times['Customer'].total_seconds() / total_duration.total_seconds()) * 100, 1) if total_duration.total_seconds() > 0 else 0,
                "agent_percentage": round((talk_times['Sales Agent'].total_seconds() / total_duration.total_seconds()) * 100, 1) if total_duration.total_seconds() > 0 else 0
            }
        },
        "overall_analysis": overall_analysis_clean,
        "conversation_flow": conversation_flow,
        "summary_metrics": {
            "segments_with_buying_signals": sum(1 for seg in conversation_flow if seg['analysis']['buying_signals'] == 'Yes'),
            "total_segments": len(conversation_flow),
            "positive_segments": sum(1 for seg in conversation_flow if seg['analysis']['sentiment'] == 'Positive'),
            "neutral_segments": sum(1 for seg in conversation_flow if seg['analysis']['sentiment'] == 'Neutral'),
            "negative_segments": sum(1 for seg in conversation_flow if seg['analysis']['sentiment'] == 'Negative'),
            "high_engagement_segments": sum(1 for seg in conversation_flow if seg['analysis']['engagement'] == 'High')
        },
        "token_usage": {
            "api_calls_made": token_usage['api_calls'],
            "total_input_tokens": token_usage['total_input_tokens'],
            "total_output_tokens": token_usage['total_output_tokens'],
            "total_tokens": token_usage['total_input_tokens'] + token_usage['total_output_tokens']
        },
        "cost_breakdown": cost_breakdown
    }
    
    return clean_data

def create_formatted_report(clean_data, output_file):
    """Create a beautifully formatted text report."""
    
    report = []
    
    # Header
    report.append("🎯 CUSTOMER INTENT & SENTIMENT ANALYSIS")
    report.append("=" * 80)
    report.append(f"📅 Analysis Date: {clean_data['call_metadata']['analysis_date']}")
    report.append(f"📞 Total Customer Statements: {clean_data['call_metadata']['total_customer_statements']}")
    report.append(f"⏱️  Actual Call Duration: {clean_data['call_metadata']['actual_call_duration']}")
    report.append("")
    
    # Talk Time Breakdown
    talk_breakdown = clean_data['call_metadata']['talk_time_breakdown']
    report.append("🎙️  TALK TIME BREAKDOWN")
    report.append("-" * 40)
    report.append(f"👤 Customer:    {talk_breakdown['customer_time']} ({talk_breakdown['customer_percentage']}%)")
    report.append(f"🏢 Sales Agent: {talk_breakdown['agent_time']} ({talk_breakdown['agent_percentage']}%)")
    report.append("")
    
    # Executive Summary
    overall = clean_data['overall_analysis']
    sentiment = overall['sentiment_analysis']
    
    report.append("📊 EXECUTIVE SUMMARY")
    report.append("-" * 40)
    report.append(f"🎯 Intent: {overall['overall_intent']}")
    report.append(f"💰 Purchase Likelihood: {overall['purchase_likelihood']}")
    report.append(f"😊 Overall Sentiment: {sentiment['overall_sentiment']} ({sentiment['confidence_score']}%)")
    report.append(f"🎪 Decision Stage: {overall['decision_stage']}")
    report.append(f"🤝 Commitment Level: {overall['commitment_level']}")
    report.append("")
    
    # Cost Analysis Section
    token_info = clean_data['token_usage']
    cost_info = clean_data['cost_breakdown']
    report.append("💰 GPT-4o MINI COST ANALYSIS")
    report.append("-" * 40)
    report.append(f"🔄 API Calls Made: {token_info['api_calls_made']}")
    report.append(f"📝 Input Tokens: {token_info['total_input_tokens']:,}")
    report.append(f"📤 Output Tokens: {token_info['total_output_tokens']:,}")
    report.append(f"🔢 Total Tokens: {token_info['total_tokens']:,}")
    report.append("")
    report.append(f"💵 Cost Breakdown (USD):")
    report.append(f"   • Input Cost: ${cost_info['input_cost_usd']:.6f}")
    report.append(f"   • Output Cost: ${cost_info['output_cost_usd']:.6f}")
    report.append(f"   • Total Cost: ${cost_info['total_cost_usd']:.6f}")
    report.append("")
    report.append(f"💸 Cost Breakdown (INR @ ₹{cost_info['usd_to_inr_rate']}):")
    report.append(f"   • Input Cost: ₹{cost_info['input_cost_inr']:.4f}")
    report.append(f"   • Output Cost: ₹{cost_info['output_cost_inr']:.4f}")
    report.append(f"   • Total Cost: ₹{cost_info['total_cost_inr']:.4f}")
    report.append("")
    
    # Key Insights
    report.append("🔍 KEY INSIGHTS")
    report.append("-" * 40)
    
    report.append("✅ PRIMARY INTERESTS:")
    for interest in overall['key_interests']:
        report.append(f"   • {interest}")
    report.append("")
    
    report.append("⚠️  CONCERNS & OBJECTIONS:")
    for concern in overall['concerns_objections']:
        report.append(f"   • {concern}")
    report.append("")
    
    report.append("🚀 BUYING SIGNALS:")
    for signal in overall['buying_signals']:
        report.append(f"   • {signal}")
    report.append("")
    
    report.append("💬 SENTIMENT INDICATORS:")
    for indicator in sentiment['sentiment_indicators']:
        report.append(f"   • \"{indicator}\"")
    report.append("")
    
    # Detailed Analysis
    report.append("📝 DETAILED ANALYSIS")
    report.append("-" * 40)
    report.append(overall['detailed_analysis'])
    report.append("")
    
    # Conversation Flow
    report.append("📈 CONVERSATION FLOW ANALYSIS")
    report.append("-" * 40)
    
    metrics = clean_data['summary_metrics']
    report.append(f"📊 Summary Metrics:")
    report.append(f"   • Segments with Buying Signals: {metrics['segments_with_buying_signals']}/{metrics['total_segments']}")
    report.append(f"   • High Engagement Segments: {metrics['high_engagement_segments']}/{metrics['total_segments']}")
    report.append(f"   • Positive: {metrics['positive_segments']} | Neutral: {metrics['neutral_segments']} | Negative: {metrics['negative_segments']}")
    report.append("")
    
    # Segment-by-segment analysis
    for segment in clean_data['conversation_flow']:
        seg_data = segment['analysis']
        
        # Emoji for sentiment
        sentiment_emoji = {"Positive": "😊", "Neutral": "😐", "Negative": "😞"}.get(seg_data['sentiment'], "😐")
        engagement_emoji = {"High": "🔥", "Medium": "⚡", "Low": "💤"}.get(seg_data['engagement'], "⚡")
        buying_signal_emoji = "✅" if seg_data['buying_signals'] == 'Yes' else "❌"
        
        report.append(f"📍 Segment {segment['segment']} ({segment['time_range']})")
        report.append(f"   {sentiment_emoji} Sentiment: {seg_data['sentiment']}")
        report.append(f"   {engagement_emoji} Engagement: {seg_data['engagement']}")
        report.append(f"   {buying_signal_emoji} Buying Signals: {seg_data['buying_signals']}")
        
        if seg_data.get('key_points'):
            report.append(f"   🔑 Key Points:")
            for point in seg_data['key_points']:
                report.append(f"      • {point}")
        report.append("")
    
    # Sales Recommendations
    report.append("🎯 SALES RECOMMENDATIONS")
    report.append("-" * 40)
    
    if overall['purchase_likelihood'] == 'High':
        report.append("🚀 HIGH PRIORITY LEAD - Act Fast!")
        report.append("   • Schedule immediate follow-up within 24 hours")
        report.append("   • Prepare customized proposal addressing specific concerns")
        report.append("   • Focus on value proposition for unique experiences")
    
    if overall['commitment_level'] == 'High':
        report.append("   • Customer is ready to make decisions - present clear options")
        report.append("   • Address accommodation concerns immediately")
        report.append("   • Provide detailed cost breakdown for transparency")
    
    report.append("")
    report.append("=" * 80)
    report.append("🎉 Analysis Complete - Ready for Sales Action!")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

def display_console_summary(clean_data):
    """Display a summary in the console."""
    print("\n🔍 Analyzing Customer Intent and Sentiment...")
    print("="*60)
    
    overall = clean_data['overall_analysis']
    sentiment = overall['sentiment_analysis']
    metrics = clean_data['summary_metrics']
    talk_breakdown = clean_data['call_metadata']['talk_time_breakdown']
    token_info = clean_data['token_usage']
    cost_info = clean_data['cost_breakdown']
    
    print(f"📊 Found {clean_data['call_metadata']['total_customer_statements']} customer statements")
    print(f"⏱️  Actual call duration: {clean_data['call_metadata']['actual_call_duration']}")
    
    # Talk time breakdown
    print(f"\n🎙️  Talk Time Breakdown:")
    print(f"   👤 Customer:    {talk_breakdown['customer_time']} ({talk_breakdown['customer_percentage']}%)")
    print(f"   🏢 Sales Agent: {talk_breakdown['agent_time']} ({talk_breakdown['agent_percentage']}%)")
    
    # Token usage and cost breakdown
    print(f"\n💰 GPT-4o Mini Usage & Cost:")
    print(f"   🔄 API Calls Made: {token_info['api_calls_made']}")
    print(f"   📝 Input Tokens: {token_info['total_input_tokens']:,}")
    print(f"   📤 Output Tokens: {token_info['total_output_tokens']:,}")
    print(f"   🔢 Total Tokens: {token_info['total_tokens']:,}")
    print(f"   💵 Total Cost (USD): ${cost_info['total_cost_usd']}")
    print(f"   💸 Total Cost (INR): ₹{cost_info['total_cost_inr']}")
    print(f"   📊 Exchange Rate: ${1} = ₹{cost_info['usd_to_inr_rate']}")
    
    print("\n" + "="*60)
    print("CUSTOMER INTENT & SENTIMENT ANALYSIS")
    print("="*60)
    
    print(f"🎯 Overall Intent: {overall['overall_intent']}")
    print(f"💰 Purchase Likelihood: {overall['purchase_likelihood']}")
    print(f"😊 Overall Sentiment: {sentiment['overall_sentiment']} ({sentiment['confidence_score']}%)")
    print(f"🎪 Decision Stage: {overall['decision_stage']}")
    print(f"🤝 Commitment Level: {overall['commitment_level']}")
    
    print(f"\n📊 Flow Summary:")
    print(f"   • Segments with Buying Signals: {metrics['segments_with_buying_signals']}/{metrics['total_segments']}")
    print(f"   • High Engagement Segments: {metrics['high_engagement_segments']}/{metrics['total_segments']}")
    print(f"   • Sentiment Distribution: Positive({metrics['positive_segments']}) | Neutral({metrics['neutral_segments']}) | Negative({metrics['negative_segments']})")

def main(file_path):
    print("🚀 Starting Integrated Customer Analysis...")
    print("="*60)
    
    # Step 1: Calculate talk times
    print("⏱️  Step 1: Calculating talk times...")
    talk_times = calculate_talk_times(file_path)
    
    # Display talk time analysis
    print(f"\n{'='*50}")
    print("TALK TIME ANALYSIS")
    print(f"{'='*50}")
    
    total_time = sum(talk_times.values(), timedelta())
    
    for role, duration in talk_times.items():
        total_seconds = duration.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        percentage = (duration.total_seconds() / total_time.total_seconds()) * 100 if total_time.total_seconds() > 0 else 0
        
        print(f"{role:12}: {minutes:2d}m {seconds:2d}s ({percentage:.1f}%)")
    
    total_seconds = total_time.total_seconds()
    total_minutes = int(total_seconds // 60)
    total_seconds_remainder = int(total_seconds % 60)
    print(f"{'Total':12}: {total_minutes:2d}m {total_seconds_remainder:2d}s (100.0%)")
    print(f"{'='*50}")
    
    # Step 2: Extract customer lines
    print("\n📝 Step 2: Extracting customer statements...")
    customer_lines = extract_customer_lines(file_path)
    
    if not customer_lines:
        print("❌ No customer statements found in the file!")
        return
    
    # Step 3: Perform overall analysis
    print("🎯 Step 3: Analyzing overall intent and sentiment...")
    overall_analysis = analyze_customer_intent_and_sentiment(customer_lines)
    
    if not overall_analysis:
        print("❌ Failed to analyze customer intent!")
        return
    
    # Step 4: Analyze conversation flow
    print("🔄 Step 4: Analyzing conversation flow...")
    segment_analysis = analyze_conversation_flow(customer_lines)
    
    # Step 5: Clean and structure the data
    print("🧹 Step 5: Cleaning and structuring data...")
    clean_data = clean_and_structure_data(overall_analysis, segment_analysis, len(customer_lines), talk_times)
    
    # Step 6: Generate outputs
    print("📄 Step 6: Generating reports...")
    
    # Base filename for outputs
    base_name = file_path.replace('.txt', '')
    
    # Save clean JSON
    clean_json_file = f"{base_name}_ANALYSIS.json"
    with open(clean_json_file, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)
    
    # Create formatted report
    report_file = f"{base_name}_REPORT.txt"
    create_formatted_report(clean_data, report_file)
    
    # Display console summary
    display_console_summary(clean_data)
    
    print(f"\n💾 Files Generated:")
    print(f"   📊 Clean JSON: {clean_json_file}")
    print(f"   📄 Formatted Report: {report_file}")
    print("\n🎉 Analysis Complete - Ready for Sales Action!")
    print("="*60)

if __name__ == "__main__":
    import sys
    
    # Allow command line arguments or use default
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    else:
        file_path = "CALL_1117711_speaker_segmented.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        print("Please ensure the transcript file exists in the current directory.")
        sys.exit(1)
    
    main(file_path)