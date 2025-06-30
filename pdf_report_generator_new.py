import json
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Warning: matplotlib not available. Charts will be skipped.")
from io import BytesIO

class CustomerAnalysisPDFGenerator:
    def __init__(self, json_file_path):
        """Initialize the PDF generator with analysis data."""
        self.json_file_path = json_file_path
        self.data = self.load_json_data()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def load_json_data(self):
        """Load the analysis data from JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return None
    
    def setup_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        # Helper function to safely add styles
        def safe_add_style(style):
            if style.name not in self.styles:
                self.styles.add(style)
        
        safe_add_style(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold'
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomSectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495E'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=8,
            backColor=colors.HexColor('#EBF3FD')
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomSubHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#2980B9'),
            fontName='Helvetica-Bold'
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomBulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            fontName='Helvetica'
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomHighlightBox',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=12,
            borderWidth=2,
            borderColor=colors.HexColor('#E74C3C'),
            borderPadding=12,
            backColor=colors.HexColor('#FADBD8'),
            fontName='Helvetica-Bold'
        ))
        
        safe_add_style(ParagraphStyle(
            name='CustomMetricBox',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.HexColor('#27AE60'),
            borderPadding=8,
            backColor=colors.HexColor('#E8F8F5'),
            fontName='Helvetica-Bold'
        ))

    def create_header_footer(self, canvas, doc):
        """Create header and footer for each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#2C3E50'))
        canvas.drawString(inch, letter[1] - 0.75*inch, "Customer Intent & Sentiment Analysis Report")
        canvas.drawString(letter[0] - 2*inch, letter[1] - 0.75*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Header line
        canvas.setStrokeColor(colors.HexColor('#3498DB'))
        canvas.setLineWidth(2)
        canvas.line(inch, letter[1] - 0.85*inch, letter[0] - inch, letter[1] - 0.85*inch)
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7F8C8D'))
        canvas.drawString(inch, 0.75*inch, "Confidential - Sales Analysis Report")
        canvas.drawRightString(letter[0] - inch, 0.75*inch, f"Page {doc.page}")
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#BDC3C7'))
        canvas.setLineWidth(1)
        canvas.line(inch, 0.9*inch, letter[0] - inch, 0.9*inch)
        
        canvas.restoreState()

    def create_sentiment_chart(self):
        """Create a sentiment distribution chart."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            metrics = self.data['summary_metrics']
            
            # Data for the chart
            sentiments = ['Positive', 'Neutral', 'Negative']
            values = [metrics['positive_segments'], metrics['neutral_segments'], metrics['negative_segments']]
            colors_list = ['#2ECC71', '#F39C12', '#E74C3C']
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(values, labels=sentiments, colors=colors_list, 
                                            autopct='%1.1f%%', startangle=90, 
                                            textprops={'fontsize': 12, 'weight': 'bold'})
            
            # Customize the chart
            ax.set_title('Sentiment Distribution Across Conversation Segments', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Error creating sentiment chart: {e}")
            return None

    def create_engagement_chart(self):
        """Create an engagement level chart."""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            conversation_flow = self.data['conversation_flow']
            
            # Extract segment data
            segments = []
            engagements = []
            sentiments = []
            
            for segment in conversation_flow:
                segments.append(f"Seg {segment['segment']}")
                
                # Map engagement to numeric values
                eng_map = {'High': 3, 'Medium': 2, 'Low': 1}
                engagements.append(eng_map.get(segment['analysis']['engagement'], 1))
                
                # Color based on sentiment
                sent_colors = {'Positive': '#2ECC71', 'Neutral': '#F39C12', 'Negative': '#E74C3C'}
                sentiments.append(sent_colors.get(segment['analysis']['sentiment'], '#F39C12'))
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create bar chart
            bars = ax.bar(segments, engagements, color=sentiments, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Customize the chart
            ax.set_xlabel('Conversation Segments', fontsize=12, fontweight='bold')
            ax.set_ylabel('Engagement Level', fontsize=12, fontweight='bold')
            ax.set_title('Customer Engagement Throughout Conversation', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylim(0, 3.5)
            
            # Y-axis labels
            ax.set_yticks([1, 2, 3])
            ax.set_yticklabels(['Low', 'Medium', 'High'])
            
            # Add value labels on bars
            for bar, engagement in zip(bars, engagements):
                height = bar.get_height()
                eng_text = {3: 'High', 2: 'Medium', 1: 'Low'}
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       eng_text[engagement], ha='center', va='bottom', fontweight='bold')
            
            # Add legend
            if MATPLOTLIB_AVAILABLE:
                legend_elements = [patches.Patch(color='#2ECC71', label='Positive Sentiment'),
                                 patches.Patch(color='#F39C12', label='Neutral Sentiment'),
                                 patches.Patch(color='#E74C3C', label='Negative Sentiment')]
                ax.legend(handles=legend_elements, loc='upper right')
            
            # Grid
            ax.grid(True, alpha=0.3, axis='y')
            
            # Rotate x-axis labels if needed
            plt.xticks(rotation=45, ha='right')
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Error creating engagement chart: {e}")
            return None

    def build_cover_page(self):
        """Build the cover page content."""
        story = []
        
        # Main title
        story.append(Paragraph("🎯 CUSTOMER INTENT & SENTIMENT ANALYSIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Call metadata box
        metadata = self.data['call_metadata']
        metadata_text = f"""
        <b>Analysis Date:</b> {metadata['analysis_date']}<br/>
        <b>Call Duration:</b> {metadata['actual_call_duration']}<br/>
        <b>Customer Statements:</b> {metadata['total_customer_statements']}<br/>
        <b>Customer Talk Time:</b> {metadata['talk_time_breakdown']['customer_time']} ({metadata['talk_time_breakdown']['customer_percentage']}%)<br/>
        <b>Agent Talk Time:</b> {metadata['talk_time_breakdown']['agent_time']} ({metadata['talk_time_breakdown']['agent_percentage']}%)
        """
        story.append(Paragraph(metadata_text, self.styles['CustomMetricBox']))
        story.append(Spacer(1, 0.3*inch))
        
        # Token usage and cost information
        if 'token_usage' in self.data and 'cost_breakdown' in self.data:
            token_info = self.data['token_usage']
            cost_info = self.data['cost_breakdown']
            
            # Load segmentation cost data for cover page
            segmentation_data = self.load_segmentation_cost_data()
            
            if segmentation_data:
                seg_cost = segmentation_data['cost_analysis']
                total_cost_usd = cost_info['total_cost_usd'] + seg_cost['total_cost_usd']
                total_cost_inr = cost_info['total_cost_inr'] + seg_cost['total_cost_inr']
                total_tokens = token_info['total_tokens'] + seg_cost['total_tokens']
                
                cost_text = f"""
                <b>💰 Complete Pipeline Cost Summary</b><br/>
                <b>Segmentation:</b> ${seg_cost['total_cost_usd']} USD / ₹{seg_cost['total_cost_inr']} INR ({seg_cost['total_tokens']:,} tokens)<br/>
                <b>Analysis:</b> ${cost_info['total_cost_usd']} USD / ₹{cost_info['total_cost_inr']} INR ({token_info['total_tokens']:,} tokens)<br/>
                <b>Total Pipeline Cost:</b> ${total_cost_usd:.6f} USD / ₹{total_cost_inr:.4f} INR<br/>
                <b>Total Tokens:</b> {total_tokens:,} | <b>Exchange Rate:</b> $1 = ₹{cost_info['usd_to_inr_rate']}
                """
            else:
                cost_text = f"""
                <b>💰 GPT-4o Mini Usage & Cost Analysis</b><br/>
                <b>API Calls Made:</b> {token_info['api_calls_made']}<br/>
                <b>Total Tokens:</b> {token_info['total_tokens']:,} (Input: {token_info['total_input_tokens']:,}, Output: {token_info['total_output_tokens']:,})<br/>
                <b>Total Cost:</b> ${cost_info['total_cost_usd']} USD / ₹{cost_info['total_cost_inr']} INR<br/>
                <b>Exchange Rate:</b> $1 = ₹{cost_info['usd_to_inr_rate']}
                """
            
            story.append(Paragraph(cost_text, self.styles['CustomMetricBox']))
            story.append(Spacer(1, 0.3*inch))
        
        # Key findings
        overall = self.data['overall_analysis']
        key_findings = f"""
        <b>🎯 Overall Intent:</b> {overall['overall_intent']}<br/><br/>
        <b>💰 Purchase Likelihood:</b> {overall['purchase_likelihood']}<br/><br/>
        <b>😊 Overall Sentiment:</b> {overall['sentiment_analysis']['overall_sentiment']} ({overall['sentiment_analysis']['confidence_score']}%)<br/><br/>
        <b>🎪 Decision Stage:</b> {overall['decision_stage']}<br/><br/>
        <b>🤝 Commitment Level:</b> {overall['commitment_level']}
        """
        
        if overall['purchase_likelihood'] == 'High':
            story.append(Paragraph("🚀 HIGH PRIORITY LEAD - IMMEDIATE ACTION REQUIRED!", self.styles['CustomHighlightBox']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(key_findings, self.styles['CustomMetricBox']))
        
        return story

    def build_executive_summary(self):
        """Build the executive summary section."""
        story = []
        
        story.append(Paragraph("📊 EXECUTIVE SUMMARY", self.styles['CustomSectionHeader']))
        
        overall = self.data['overall_analysis']
        summary_text = overall['detailed_analysis']
        story.append(Paragraph(summary_text, self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Create summary metrics table
        metrics = self.data['summary_metrics']
        table_data = [
            ['Metric', 'Value', 'Percentage'],
            ['Segments with Buying Signals', f"{metrics['segments_with_buying_signals']}/{metrics['total_segments']}", 
             f"{(metrics['segments_with_buying_signals']/metrics['total_segments']*100):.1f}%" if metrics['total_segments'] > 0 else "0%"],
            ['High Engagement Segments', f"{metrics['high_engagement_segments']}/{metrics['total_segments']}", 
             f"{(metrics['high_engagement_segments']/metrics['total_segments']*100):.1f}%" if metrics['total_segments'] > 0 else "0%"],
            ['Positive Sentiment Segments', str(metrics['positive_segments']), 
             f"{(metrics['positive_segments']/metrics['total_segments']*100):.1f}%" if metrics['total_segments'] > 0 else "0%"],
        ]
        
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
        ]))
        
        story.append(table)
        
        return story

    def build_key_insights(self):
        """Build the key insights section."""
        story = []
        
        story.append(Paragraph("🔍 KEY INSIGHTS", self.styles['CustomSectionHeader']))
        
        overall = self.data['overall_analysis']
        
        # Primary Interests
        story.append(Paragraph("✅ Primary Interests", self.styles['CustomSubHeader']))
        for interest in overall['key_interests']:
            story.append(Paragraph(f"• {interest}", self.styles['CustomBulletPoint']))
        story.append(Spacer(1, 0.2*inch))
        
        # Concerns & Objections
        story.append(Paragraph("⚠️ Concerns & Objections", self.styles['CustomSubHeader']))
        for concern in overall['concerns_objections']:
            story.append(Paragraph(f"• {concern}", self.styles['CustomBulletPoint']))
        story.append(Spacer(1, 0.2*inch))
        
        # Buying Signals
        story.append(Paragraph("🚀 Buying Signals", self.styles['CustomSubHeader']))
        for signal in overall['buying_signals']:
            story.append(Paragraph(f"• {signal}", self.styles['CustomBulletPoint']))
        story.append(Spacer(1, 0.2*inch))
        
        # Sentiment Indicators
        story.append(Paragraph("💬 Sentiment Indicators", self.styles['CustomSubHeader']))
        for indicator in overall['sentiment_analysis']['sentiment_indicators']:
            story.append(Paragraph(f"• \"{indicator}\"", self.styles['CustomBulletPoint']))
        
        return story

    def build_conversation_flow(self):
        """Build the conversation flow section."""
        story = []
        
        story.append(Paragraph("📈 CONVERSATION FLOW ANALYSIS", self.styles['CustomSectionHeader']))
        
        # Add engagement chart
        engagement_chart = self.create_engagement_chart()
        if engagement_chart:
            story.append(RLImage(engagement_chart, width=7*inch, height=3.5*inch))
            story.append(Spacer(1, 0.3*inch))
        
        # Segment details
        story.append(Paragraph("📍 Segment-by-Segment Analysis", self.styles['CustomSubHeader']))
        
        for segment in self.data['conversation_flow']:
            seg_data = segment['analysis']
            
            # Emoji mapping
            sentiment_emoji = {"Positive": "😊", "Neutral": "😐", "Negative": "😞"}.get(seg_data['sentiment'], "😐")
            engagement_emoji = {"High": "🔥", "Medium": "⚡", "Low": "💤"}.get(seg_data['engagement'], "⚡")
            buying_signal_emoji = "✅" if seg_data['buying_signals'] == 'Yes' else "❌"
            
            segment_text = f"""
            <b>Segment {segment['segment']} ({segment['time_range']})</b><br/>
            {sentiment_emoji} <b>Sentiment:</b> {seg_data['sentiment']}<br/>
            {engagement_emoji} <b>Engagement:</b> {seg_data['engagement']}<br/>
            {buying_signal_emoji} <b>Buying Signals:</b> {seg_data['buying_signals']}
            """
            
            story.append(Paragraph(segment_text, self.styles['CustomBodyText']))
            
            if seg_data.get('key_points'):
                story.append(Paragraph("🔑 <b>Key Points:</b>", self.styles['CustomBodyText']))
                for point in seg_data['key_points']:
                    story.append(Paragraph(f"• {point}", self.styles['CustomBulletPoint']))
            
            story.append(Spacer(1, 0.15*inch))
        
        return story

    def build_analytics_dashboard(self):
        """Build the analytics dashboard section."""
        story = []
        
        story.append(Paragraph("📊 ANALYTICS DASHBOARD", self.styles['CustomSectionHeader']))
        
        # Add sentiment chart
        sentiment_chart = self.create_sentiment_chart()
        if sentiment_chart:
            story.append(RLImage(sentiment_chart, width=6*inch, height=4*inch))
            story.append(Spacer(1, 0.3*inch))
        
        return story

    def load_segmentation_cost_data(self):
        """Load segmentation cost data from JSON file."""
        try:
            # Try to find segmentation cost file in the same directory
            base_dir = os.path.dirname(self.json_file_path)
            
            # Look for segmentation cost file
            for file in os.listdir(base_dir):
                if file.endswith('_SEGMENTATION_COST.json'):
                    segmentation_file = os.path.join(base_dir, file)
                    with open(segmentation_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load segmentation cost data: {e}")
        
        return None

    def build_cost_analysis(self):
        """Build the cost analysis section."""
        story = []
        
        if 'token_usage' not in self.data or 'cost_breakdown' not in self.data:
            return story
        
        story.append(Paragraph("💰 GPT-4o MINI COST ANALYSIS", self.styles['CustomSectionHeader']))
        
        # Load segmentation cost data
        segmentation_data = self.load_segmentation_cost_data()
        
        # Analysis Step Cost Breakdown
        story.append(Paragraph("📊 Analysis Step Costs", self.styles['CustomSubHeader']))
        
        token_info = self.data['token_usage']
        cost_info = self.data['cost_breakdown']
        
        # Create analysis cost breakdown table
        analysis_table_data = [
            ['Metric', 'Value'],
            ['API Calls Made', str(token_info['api_calls_made'])],
            ['Input Tokens', f"{token_info['total_input_tokens']:,}"],
            ['Output Tokens', f"{token_info['total_output_tokens']:,}"],
            ['Total Tokens', f"{token_info['total_tokens']:,}"],
            ['Input Cost (USD)', f"${cost_info['input_cost_usd']}"],
            ['Output Cost (USD)', f"${cost_info['output_cost_usd']}"],
            ['Total Cost (USD)', f"${cost_info['total_cost_usd']}"],
            ['Input Cost (INR)', f"₹{cost_info['input_cost_inr']}"],
            ['Output Cost (INR)', f"₹{cost_info['output_cost_inr']}"],
            ['Total Cost (INR)', f"₹{cost_info['total_cost_inr']}"],
        ]
        
        analysis_table = Table(analysis_table_data, colWidths=[3*inch, 2*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        # Highlight total cost rows
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#E8F4FD')),  # Total USD
            ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor('#E8F4FD')),  # Total INR
            ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
            ('FONTNAME', (0, 10), (-1, 10), 'Helvetica-Bold'),
        ]))
        
        story.append(analysis_table)
        story.append(Spacer(1, 0.15*inch))
        
        # Segmentation Step Cost Breakdown (if available)
        if segmentation_data:
            story.append(Paragraph("🎯 Segmentation Step Costs", self.styles['CustomSubHeader']))
            
            seg_cost = segmentation_data['cost_analysis']
            
            segmentation_table_data = [
                ['Metric', 'Value'],
                ['Blocks Processed', str(segmentation_data['blocks_processed'])],
                ['Success Rate', segmentation_data['success_rate']],
                ['Input Tokens', f"{seg_cost['input_tokens']:,}"],
                ['Output Tokens', f"{seg_cost['output_tokens']:,}"],
                ['Total Tokens', f"{seg_cost['total_tokens']:,}"],
                ['Input Cost (USD)', f"${seg_cost['input_cost_usd']}"],
                ['Output Cost (USD)', f"${seg_cost['output_cost_usd']}"],
                ['Total Cost (USD)', f"${seg_cost['total_cost_usd']}"],
                ['Input Cost (INR)', f"₹{seg_cost['input_cost_inr']}"],
                ['Output Cost (INR)', f"₹{seg_cost['output_cost_inr']}"],
                ['Total Cost (INR)', f"₹{seg_cost['total_cost_inr']}"],
            ]
            
            segmentation_table = Table(segmentation_table_data, colWidths=[3*inch, 2*inch])
            segmentation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            # Highlight total cost rows
            segmentation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#FDF2E9')),  # Total USD
                ('BACKGROUND', (0, 11), (-1, 11), colors.HexColor('#FDF2E9')),  # Total INR
                ('FONTNAME', (0, 8), (-1, 8), 'Helvetica-Bold'),
                ('FONTNAME', (0, 11), (-1, 11), 'Helvetica-Bold'),
            ]))
            
            story.append(segmentation_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Combined Total Cost Summary
            total_cost_usd = cost_info['total_cost_usd'] + seg_cost['total_cost_usd']
            total_cost_inr = cost_info['total_cost_inr'] + seg_cost['total_cost_inr']
            total_tokens = token_info['total_tokens'] + seg_cost['total_tokens']
            
            combined_summary_data = [
                ['PIPELINE STEP', 'USD COST', 'INR COST', 'TOKENS'],
                ['Segmentation', f"${seg_cost['total_cost_usd']}", f"₹{seg_cost['total_cost_inr']}", f"{seg_cost['total_tokens']:,}"],
                ['Analysis', f"${cost_info['total_cost_usd']}", f"₹{cost_info['total_cost_inr']}", f"{token_info['total_tokens']:,}"],
                ['TOTAL PIPELINE', f"${total_cost_usd:.6f}", f"₹{total_cost_inr:.4f}", f"{total_tokens:,}"]
            ]
            
            combined_table = Table(combined_summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            combined_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, 2), colors.HexColor('#F8F9FA')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#D5DBDB')),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('FONTNAME', (0, 1), (-1, 2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(Paragraph("💰 Complete Pipeline Cost Summary", self.styles['CustomSubHeader']))
            story.append(combined_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Update exchange rate info
            exchange_rate = seg_cost.get('usd_to_inr_rate', cost_info.get('usd_to_inr_rate', 85.0))
            
        else:
            # If no segmentation data, show only analysis costs
            total_cost_usd = cost_info['total_cost_usd']
            total_cost_inr = cost_info['total_cost_inr']
            total_tokens = token_info['total_tokens']
            exchange_rate = cost_info.get('usd_to_inr_rate', 85.0)
        
        # Cost efficiency analysis
        if total_tokens > 0:
            cost_per_1k_tokens_usd = (total_cost_usd / total_tokens) * 1000
            cost_per_1k_tokens_inr = (total_cost_inr / total_tokens) * 1000
            
            if segmentation_data:
                efficiency_text = f"""
                <b>💡 Complete Pipeline Cost Efficiency:</b><br/>
                • Total pipeline cost: ${total_cost_usd:.6f} USD / ₹{total_cost_inr:.4f} INR<br/>
                • Cost per 1,000 tokens: ${cost_per_1k_tokens_usd:.4f} USD / ₹{cost_per_1k_tokens_inr:.2f} INR<br/>
                • Exchange rate used: $1 = ₹{exchange_rate}<br/>
                • Segmentation vs Analysis cost ratio: {(seg_cost['total_cost_inr']/total_cost_inr*100):.1f}% : {(cost_info['total_cost_inr']/total_cost_inr*100):.1f}%<br/>
                • Total tokens processed: {total_tokens:,} ({seg_cost['total_tokens']:,} segmentation + {token_info['total_tokens']:,} analysis)
                """
            else:
                efficiency_text = f"""
                <b>💡 Analysis Step Cost Efficiency:</b><br/>
                • Cost per 1,000 tokens: ${cost_per_1k_tokens_usd:.4f} USD / ₹{cost_per_1k_tokens_inr:.2f} INR<br/>
                • Average tokens per API call: {token_info['total_tokens'] // token_info['api_calls_made']:,}<br/>
                • Input/Output ratio: {token_info['total_input_tokens']}/{token_info['total_output_tokens']} 
                ({(token_info['total_input_tokens']/token_info['total_tokens']*100):.1f}% input, {(token_info['total_output_tokens']/token_info['total_tokens']*100):.1f}% output)<br/>
                • Exchange rate used: $1 = ₹{exchange_rate}
                """
            
            story.append(Paragraph(efficiency_text, self.styles['CustomBodyText']))
        
        return story

    def build_recommendations(self):
        """Build the sales recommendations section."""
        story = []
        
        story.append(Paragraph("🎯 SALES RECOMMENDATIONS", self.styles['CustomSectionHeader']))
        
        overall = self.data['overall_analysis']
        
        # Priority level recommendations
        if overall['purchase_likelihood'] == 'High':
            story.append(Paragraph("🚀 HIGH PRIORITY LEAD - ACT FAST!", self.styles['CustomHighlightBox']))
            recommendations = [
                "Schedule immediate follow-up within 24 hours",
                "Prepare customized proposal addressing specific concerns",
                "Focus on value proposition for unique experiences",
                "Provide detailed cost breakdown for transparency"
            ]
        elif overall['purchase_likelihood'] == 'Medium':
            recommendations = [
                "Schedule follow-up within 48-72 hours",
                "Address specific concerns raised during the call",
                "Provide additional information about packages",
                "Follow up with promotional offers if appropriate"
            ]
        else:
            recommendations = [
                "Schedule gentle follow-up in 1 week",
                "Focus on education and relationship building",
                "Address budget constraints with flexible options",
                "Keep in nurture sequence for future opportunities"
            ]
        
        # Commitment level recommendations
        if overall['commitment_level'] == 'High':
            recommendations.extend([
                "Customer is ready to make decisions - present clear options",
                "Focus on closing techniques and next steps",
                "Prepare booking documentation"
            ])
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['CustomBulletPoint']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Next steps table
        next_steps_data = [
            ['Action Item', 'Timeline', 'Priority'],
            ['Follow-up Call', '24-48 hours', 'High'],
            ['Send Proposal', '1-2 business days', 'High'],
            ['Address Concerns', 'During follow-up', 'Medium'],
            ['Booking Assistance', 'As needed', 'Medium']
        ]
        
        next_steps_table = Table(next_steps_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        next_steps_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FADBD8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E74C3C'))
        ]))
        
        story.append(Paragraph("📋 Next Steps Action Plan", self.styles['CustomSubHeader']))
        story.append(next_steps_table)
        
        return story

    def generate_pdf(self, output_filename=None):
        """Generate the complete PDF report."""
        if not self.data:
            print("No data available to generate PDF!")
            return False
        
        if not output_filename:
            # Generate filename based on input
            base_name = os.path.splitext(self.json_file_path)[0]
            output_filename = f"{base_name}_PROFESSIONAL_REPORT.pdf"
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=100
        )
          # Build the complete story
        story = []
        
        # Cover page
        story.extend(self.build_cover_page())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self.build_executive_summary())
        story.append(Spacer(1, 0.5*inch))
        
        # Cost analysis section
        story.extend(self.build_cost_analysis())
        story.append(Spacer(1, 0.3*inch))
        
        # Key insights
        story.extend(self.build_key_insights())
        story.append(PageBreak())
        
        # Analytics dashboard
        story.extend(self.build_analytics_dashboard())
        story.append(Spacer(1, 0.3*inch))
        
        # Conversation flow
        story.extend(self.build_conversation_flow())
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self.build_recommendations())        # Key insights
        story.extend(self.build_key_insights())
        story.append(PageBreak())
        
        # Analytics dashboard
        story.extend(self.build_analytics_dashboard())
        story.append(Spacer(1, 0.3*inch))
        
        # Conversation flow
        story.extend(self.build_conversation_flow())
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self.build_recommendations())
        
        # Build the PDF
        try:
            doc.build(story, onFirstPage=self.create_header_footer, onLaterPages=self.create_header_footer)
            print(f"✅ PDF report generated successfully: {output_filename}")
            return True
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return False

def main():
    """Main function to generate PDF report."""
    import sys
    
    # Default JSON file
    json_file = "CALL_1117711_speaker_segmented_ANALYSIS.json"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"❌ Error: JSON file '{json_file}' not found!")
        print("Please ensure the analysis JSON file exists.")
        print("Run Intent_2.py first to generate the analysis data.")
        return
    
    print("🚀 Starting PDF Report Generation...")
    print("="*60)
    
    # Create PDF generator
    pdf_generator = CustomerAnalysisPDFGenerator(json_file)
    
    # Generate the PDF
    success = pdf_generator.generate_pdf()
    
    if success:
        print("\n🎉 PDF Report Generation Complete!")
        print("="*60)
        output_file = os.path.splitext(json_file)[0] + "_PROFESSIONAL_REPORT.pdf"
        print(f"📄 Output file: {output_file}")
        print("\n📋 Report includes:")
        print("   • Executive Summary with Key Metrics")
        print("   • Customer Intent & Sentiment Analysis")
        print("   • Interactive Charts and Visualizations")
        print("   • Conversation Flow Analysis")
        print("   • Sales Recommendations & Action Plan")
        print("   • Professional Formatting & Design")
    else:
        print("\n❌ PDF generation failed!")

if __name__ == "__main__":
    main()
