# Manual LLM Evaluation for Financial Data Extraction - Project Summary Report

## 📅 Project Details
- **Date**: June 4, 2025
- **Time**: Manual evaluation conducted via web interfaces
- **Duration**: Multi-session manual testing across 3 LLM platforms
- **Status**: ✅ Successfully Completed with Comprehensive Analysis

## 🤖 LLM Configuration
- **Models Evaluated**: ChatGPT (GPT-4o), Claude Sonnet 4, Gemini 2.5 Pro
- **Evaluation Method**: Manual prompt submission through web interfaces
- **Test Scope**: 6 PDF credit card statements (MC & VS, Feb-Apr 2025)
- **Ground Truth**: 57 verified transactions worth $5,120,378 COP

## 🎯 Task Objective
Evaluate and compare the accuracy of three major Large Language Models in extracting structured financial data (dates, descriptions, amounts) from credit card PDF statements through manual web interface testing.

### Scope Requirements
- ✅ Test 3 LLMs: ChatGPT, Claude, Gemini
- ✅ Process 6 PDF statements (MC-FEB/MAR/ABR, VS-FEB/MAR/ABR 2025)
- ✅ Extract structured JSON data: date, description, amount
- ✅ Calculate precision, recall, and accuracy metrics
- 🧪 Success Criteria: Comprehensive performance comparison with actionable recommendations

## 🛠 What Was Done

### 1. Test Methodology Setup
- Created standardized prompt template for consistent testing
- Established ground truth dataset with 57 manually verified transactions
- Implemented evaluation framework using [`llms_evaluator.py`](Tests/(Nima) PBA/test #0/Metricas/llms_evaluator.py:1)

### 2. Manual LLM Testing
- **ChatGPT (GPT-4o)**: Direct web interface testing with standardized prompts
- **Claude Sonnet 4**: Manual evaluation through Anthropic web interface
- **Gemini 2.5 Pro**: Testing via Google's web interface
- **Output Format**: Structured JSON with bill_name and transactions array

### 3. Performance Analysis
- **Metrics Calculated**: Precision, Recall, True/False Positives, F1-Score
- **Matching Criteria**: Date exact match, amount ±5 peso tolerance, normalized description comparison
- **Results Storage**: JSON format for each model with comprehensive analysis

### 4. Key Features Implemented
- Standardized prompt engineering for fair comparison
- Comprehensive evaluation metrics framework
- Per-bill and overall performance analysis
- Error pattern identification and categorization

## 🎯 Key Decisions Made

### 1. Evaluation Approach
- **Manual Testing**: Chose web interface testing for realistic user experience
- **Standardized Prompts**: Used identical prompts across all models for fair comparison
- **JSON Output**: Required structured format for automated evaluation

### 2. Metrics Framework
- **Precision Focus**: Emphasized accuracy of extracted transactions
- **Recall Measurement**: Tracked coverage of actual transactions
- **Tolerance Levels**: ±5 peso tolerance for amount matching to handle minor variations

### 3. Ground Truth Strategy
- **Manual Verification**: All 57 transactions manually verified against source PDFs
- **Comprehensive Coverage**: Included both simple (MC) and complex (VS) document layouts
- **Quality Assurance**: Double-checked all ground truth entries for accuracy

## 📊 Results Achieved

### Overall Performance Rankings
| Rank | Model | Precision | Recall | F1-Score | True Positives | Success Rate |
|------|-------|-----------|--------|----------|----------------|--------------|
| 🥇 1st | **Claude Sonnet 4** | **93.8%** | **78.9%** | **85.7%** | **45/57** | **84.2%** |
| 🥈 2nd | **ChatGPT (GPT-4o)** | **89.6%** | **75.4%** | **81.9%** | **43/57** | **84.2%** |
| 🥉 3rd | **Gemini 2.5 Pro** | **92.5%** | **64.9%** | **76.2%** | **37/57** | **70.2%** |

### Key Performance Insights
- ✅ **Perfect MC Performance**: All models achieved 100% accuracy on MasterCard statements
- ✅ **VS Complexity**: Visa statements showed significant performance variations between models
- ✅ **Claude Leadership**: Best balance of precision and recall across all document types
- ⚠️ **Gemini Inconsistency**: Complete failure on VS-ABR-2025 (missed all 17 transactions)

## ⚠️ Potential Risks & Considerations

### 1. Document Complexity Dependencies
- **Risk**: Performance varies significantly with PDF layout complexity
- **Evidence**: Perfect performance on simple MC layouts, variable results on complex VS layouts
- **Mitigation**: Document preprocessing and complexity assessment

### 2. Manual Process Limitations
- **Risk**: Human error in prompt submission and result collection
- **Impact**: Potential inconsistencies in testing methodology
- **Mitigation**: Standardized procedures and API integration for future testing

### 3. Model-Specific Failure Patterns
- **Risk**: Gemini showed complete failure on complex documents
- **Impact**: Unreliable for production use without document screening
- **Mitigation**: Implement fallback mechanisms and document complexity detection

### 4. Prompt Engineering Sensitivity
- **Risk**: Results heavily dependent on prompt design
- **Impact**: Different prompts could yield different performance rankings
- **Mitigation**: Continuous prompt optimization based on error patterns

## 🚀 Recommended Enhancements & Next Steps

### Phase 1: Immediate Improvements
1. **API Integration**: Move from manual web interface to API-based processing
2. **Prompt Optimization**: Refine prompts based on identified error patterns
3. **Automated Validation**: Implement automated result verification systems
4. **Document Preprocessing**: Add PDF optimization before LLM processing

### Phase 2: Advanced Features
1. **Multi-Model Ensemble**: Combine results from multiple LLMs for improved accuracy
2. **Confidence Scoring**: Add reliability metrics to extraction results
3. **Error Recovery**: Implement fallback mechanisms for failed extractions
4. **Real-time Processing**: Build streaming extraction capabilities

### Phase 3: Production Deployment
1. **Monitoring Dashboard**: Real-time performance tracking and alerting
2. **Cost Optimization**: Dynamic model selection based on accuracy requirements
3. **Scalability Architecture**: High-volume processing infrastructure
4. **Compliance Integration**: Audit trails and regulatory reporting features

## 🔧 Technical Settings & Configuration

### Evaluation Framework
```python
# Key evaluation metrics from llms_evaluator.py
precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
```

### Standardized Prompt Template
```markdown
"You will be given one credit card bill (in PDF or image format). 
Your task is to extract valid transactions and return them in a strict, structured format.

Output Format: JSON with bill_name and transactions array
Instructions: Use VALOR COMPRA column, amounts > 0, YYYY-MM-DD dates, integer amounts"
```

### File Structure
```
Tests/(Nima) PBA/test #0/
├── 2025.06.04 - Prompt para ejecutar prueba.md    # Test methodology
├── Metricas/
│   ├── llms_evaluator.py                          # Evaluation framework
│   └── result_sumarizer.py                        # Summary statistics
├── Resultados/
│   ├── ChatGPT.json                               # GPT-4o results
│   ├── Claude.json                                # Claude Sonnet 4 results
│   ├── Gemini.json                                # Gemini 2.5 Pro results
│   └── 2025.06.04 - Comparacion de LLMs.xlsx     # Comprehensive analysis
└── project_summary_report.md                      # This report
```

### Ground Truth Dataset
- **Source**: [`ground_truth.json`](Tests/(Nima) PBA/ground_truth.json:1)
- **Coverage**: 6 bills, 57 transactions, $5,120,378 total value
- **Quality**: 100% manually verified against source PDFs

## 📝 Development Notes
- Manual testing provides realistic user experience but limits scalability
- Standardized evaluation framework enables fair model comparison
- Error patterns reveal document complexity as key performance factor
- Results provide clear guidance for production LLM selection

## 🎯 Success Metrics
- ✅ Successfully evaluated all 3 target LLMs across 6 PDF statements
- ✅ Established comprehensive performance benchmarks with precision/recall metrics
- ✅ Identified clear performance hierarchy: Claude > ChatGPT > Gemini
- ✅ Documented error patterns and provided actionable model selection guidance
- ✅ Created reproducible evaluation framework for future LLM assessments

