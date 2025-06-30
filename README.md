# 🎯 Customer Intent & Sentiment Analysis Pipeline

## 📖 Overview

This is a complete AI-powered pipeline for analyzing customer conversations from sales calls. The system processes raw conversation transcripts through three main stages: **Speaker Segmentation**, **Intent & Sentiment Analysis**, and **Professional PDF Report Generation**. Each stage tracks GPT-4o mini token usage and costs (USD/INR) for complete transparency.

## 🔧 System Architecture

```
Raw Transcript → Speaker Segmentation → Intent Analysis → PDF Report
    (Step 1)           (Step 2)          (Step 3)        (Output)
     ↓                    ↓                 ↓              ↓
segmentation.py    →   Intent_2.py   →  pdf_report_    Professional
                                       generator_new.py   PDF Report
```

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API key** (GPT-4o mini access)
3. **Required Python packages** (see installation below)

### Installation

1. **Clone or download** this project to your local machine
2. **Install dependencies** for each component:

```bash
# For segmentation step
pip install -r requirements_segment.txt

# For PDF generation (optional, for enhanced reports)
pip install -r requirements_pdf.txt
```

3. **Update API key** in both `segmentation.py` and `Intent_2.py`:
```python
client = OpenAI(api_key="your-openai-api-key-here")
```

### Running the Pipeline

#### Step 1: Speaker Segmentation
```bash
python segmentation.py
```
- **Input**: `CALL_*_segments.txt` (raw transcript file)
- **Output**: `CALL_*_speaker_segmented.txt` (speaker-labeled transcript)
- **Cost File**: `CALL_*_speaker_segmented_SEGMENTATION_COST.json`

#### Step 2: Intent & Sentiment Analysis
```bash
python Intent_2.py
```
- **Input**: `CALL_*_speaker_segmented.txt` (from Step 1)
- **Output**: `CALL_*_speaker_segmented_ANALYSIS.json` (analysis data)
- **Report**: `CALL_*_speaker_segmented_REPORT.txt` (formatted text report)

#### Step 3: Professional PDF Report Generation
```bash
python pdf_report_generator_new.py
```
- **Input**: `CALL_*_speaker_segmented_ANALYSIS.json` (from Step 2)
- **Output**: `CALL_*_speaker_segmented_PROFESSIONAL_REPORT.pdf`

## 📁 File Structure

```
lead scoring/
│
├── 📄 segmentation.py              # Step 1: Speaker identification
├── 📄 Intent_2.py                  # Step 2: Intent & sentiment analysis
├── 📄 pdf_report_generator_new.py  # Step 3: PDF report generation
│
├── 📋 requirements_segment.txt     # Dependencies for segmentation
├── 📋 requirements_pdf.txt         # Dependencies for PDF generation
│
├── 📊 Input Files:
│   └── CALL_*_segments.txt         # Raw conversation transcript
│
├── 🔄 Intermediate Files:
│   ├── CALL_*_speaker_segmented.txt              # Speaker-labeled transcript
│   ├── CALL_*_speaker_segmented_SEGMENTATION_COST.json  # Segmentation costs
│   ├── CALL_*_speaker_segmented_ANALYSIS.json    # Analysis results
│   └── CALL_*_speaker_segmented_REPORT.txt       # Text report
│
└── 📊 Final Output:
    └── CALL_*_speaker_segmented_PROFESSIONAL_REPORT.pdf  # Professional PDF report
```

## 🔍 Detailed Component Breakdown

### 1. 🎙️ Speaker Segmentation (`segmentation.py`)

**Purpose**: Identifies who is speaking (Customer vs Sales Agent) in conversation transcripts.

**Key Features**:
- ✅ Processes transcripts in configurable blocks (default: 15 segments)
- 📊 Real-time token usage and cost tracking
- 🔄 Robust error handling for failed blocks
- 💾 Saves detailed cost analysis to JSON file
- 🌍 Supports USD/INR cost conversion

**Process**:
1. Reads raw transcript file with timestamps
2. Groups segments into processing blocks
3. Uses GPT-4o mini to identify speakers
4. Outputs speaker-labeled transcript
5. Tracks and reports token costs

**Console Output Example**:
```
🚀 Starting Speaker Segmentation Process...
📊 Processing 158 segments in 11 blocks...
🔄 Processing block 1/11...
  Block tokens - Input: 1,245, Output: 987
💰 TOKEN USAGE & COST ANALYSIS
📥 Total Input Tokens:  14,537
📤 Total Output Tokens: 13,908
💸 Total Cost (INR):    ₹0.8947
```

### 2. 🧠 Intent & Sentiment Analysis (`Intent_2.py`)

**Purpose**: Analyzes customer intent, sentiment, and buying signals from speaker-segmented conversations.

**Key Features**:
- 🎯 **Overall Intent Analysis**: Purchase likelihood, decision stage, commitment level
- 😊 **Sentiment Analysis**: Positive/Neutral/Negative with confidence scores
- 🚀 **Buying Signal Detection**: Identifies key purchase indicators
- 📈 **Conversation Flow Analysis**: Tracks sentiment evolution over time
- ⏱️ **Talk Time Analysis**: Calculates customer vs agent speaking time
- 💰 **Cost Tracking**: Comprehensive token usage and cost analysis

**Analysis Categories**:
- **Intent Classification**: Overall customer intent and interests
- **Sentiment Scoring**: Emotion analysis with specific indicators
- **Buying Signals**: "visa", "passport", "booking", "confirm", etc.
- **Objections/Concerns**: Budget constraints, hesitations
- **Decision Stage**: Awareness → Consideration → Decision → Post-Decision

**Output Files**:
- **JSON**: Structured analysis data for further processing
- **Text Report**: Human-readable formatted report with insights
- **Console**: Real-time progress and summary display

### 3. 📊 Professional PDF Report (`pdf_report_generator_new.py`)

**Purpose**: Creates a comprehensive, professionally formatted PDF report combining both segmentation and analysis costs.

**Key Features**:
- 🎨 **Professional Design**: Custom styling, colors, and layouts
- 📈 **Interactive Charts**: Sentiment distribution and engagement charts (matplotlib)
- 💰 **Complete Cost Analysis**: Combined segmentation + analysis cost breakdown
- 📋 **Executive Summary**: Key metrics and insights at a glance
- 🎯 **Sales Recommendations**: Actionable next steps based on analysis
- 📊 **Analytics Dashboard**: Visual representation of conversation data

**Report Sections**:
1. **Cover Page**: Overview with complete pipeline costs (USD/INR)
2. **Executive Summary**: Key metrics and findings
3. **Cost Analysis**: Detailed breakdown of both segmentation and analysis costs
4. **Key Insights**: Interests, concerns, buying signals
5. **Analytics Dashboard**: Charts and visualizations
6. **Conversation Flow**: Segment-by-segment analysis
7. **Sales Recommendations**: Action plan and next steps

## 💰 Cost Tracking & Transparency

### GPT-4o Mini Pricing (as of 2025)
- **Input tokens**: $0.15 per 1M tokens
- **Output tokens**: $0.60 per 1M tokens
- **Exchange rate**: $1 = ₹85 (configurable)

### Cost Tracking Features
- ✅ **Real-time monitoring** during processing
- ✅ **Per-block cost tracking** in segmentation
- ✅ **Per-API-call tracking** in analysis
- ✅ **Combined pipeline costs** in PDF report
- ✅ **USD and INR conversion** with current rates
- ✅ **Cost efficiency metrics** (cost per 1K tokens, ratios)

### Typical Cost Range
For a 30-minute conversation (≈150-200 segments):
- **Segmentation**: ₹0.50 - ₹1.20 INR
- **Analysis**: ₹0.30 - ₹0.80 INR
- **Total Pipeline**: ₹0.80 - ₹2.00 INR ($0.01 - $0.024 USD)

## 🛠️ Configuration Options

### Segmentation Parameters
```python
# In segmentation.py
block_size = 15  # Number of segments per processing block
usd_to_inr_rate = 85.0  # Exchange rate for cost conversion
```

### Analysis Parameters
```python
# In Intent_2.py
segment_size_minutes = 5  # Minutes per conversation segment for flow analysis
usd_to_inr_rate = 85.0   # Exchange rate for cost conversion
```

### PDF Generation Options
```python
# In pdf_report_generator_new.py
MATPLOTLIB_AVAILABLE = True  # Enable/disable charts (requires matplotlib)
```

## 🔍 Output Analysis Guide

### Understanding the Results

#### Purchase Likelihood Scores
- **High**: Strong buying signals, ready to purchase
- **Medium**: Interested but has concerns to address
- **Low**: Early stage, needs nurturing

#### Sentiment Indicators
- **Positive**: "great", "perfect", "sounds good", "let's do it"
- **Engagement**: Asking detailed questions, discussing dates
- **Negative**: "expensive", "too much", "not sure", "maybe"

#### Decision Stages
- **Awareness**: Just learning about the product
- **Consideration**: Comparing options, asking questions
- **Decision**: Ready to make a choice
- **Post-Decision**: Already decided, working on details

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   Solution: Update API key in both segmentation.py and Intent_2.py
   ```

2. **File Not Found**
   ```
   Error: Input file not found
   Solution: Ensure input file exists and filename matches in script
   ```

3. **Missing Dependencies**
   ```
   Error: ModuleNotFoundError
   Solution: Install requirements: pip install -r requirements_segment.txt
   ```

4. **Charts Not Showing in PDF**
   ```
   Warning: matplotlib not available
   Solution: Install matplotlib: pip install matplotlib>=3.7.0
   ```

### Debug Mode
Enable detailed logging by modifying the scripts:
```python
# Add at the top of any script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Sample Workflow

Here's a complete example workflow:

```bash
# 1. Start with raw transcript
CALL_1117711_DIAa627c702b059f843e7a3570e994aef86_1747605641_segments.txt

# 2. Run speaker segmentation
python segmentation.py
# Outputs: CALL_1117711_speaker_segmented.txt
#          CALL_1117711_speaker_segmented_SEGMENTATION_COST.json

# 3. Run intent analysis
python Intent_2.py
# Outputs: CALL_1117711_speaker_segmented_ANALYSIS.json
#          CALL_1117711_speaker_segmented_REPORT.txt

# 4. Generate professional PDF
python pdf_report_generator_new.py
# Outputs: CALL_1117711_speaker_segmented_PROFESSIONAL_REPORT.pdf
```

## 🎯 Key Benefits

- **🔬 Comprehensive Analysis**: Intent, sentiment, buying signals, objections
- **💰 Cost Transparency**: Real-time tracking of GPT-4o mini usage and costs
- **📊 Professional Reports**: Beautifully formatted PDF reports for stakeholders
- **⚡ Efficient Processing**: Optimized for speed and cost-effectiveness
- **🔄 Robust Pipeline**: Error handling and recovery mechanisms
- **📈 Actionable Insights**: Clear recommendations for sales teams

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Ensure API keys are correctly configured
4. Check that input files exist and are properly formatted

## 🔮 Future Enhancements

- **Multi-language support** for international conversations
- **Custom model fine-tuning** for domain-specific analysis
- **Real-time processing** for live conversation analysis
- **Advanced visualizations** with interactive dashboards
- **Integration with CRM systems** for automated workflow

---

**Version**: 2.0  
**Last Updated**: June 30, 2025  
**GPT Model**: GPT-4o mini  
**Python Compatibility**: 3.8+
