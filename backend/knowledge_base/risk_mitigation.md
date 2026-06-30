# Startup Risks and SWOT Analysis Framework

Startup validation requires looking closely at the risks and failure modes of the venture. This document provides structures for SWOT analyses and risk matrices.

## 1. The Top Startup Failure Modes
Based on historical startup analyses, the major reasons startups fail are:
1. **No Market Need (35%)**: Building a product that nobody wants.
2. **Ran Out of Cash (20%)**: Failing to raise capital or generate revenue before running out of money.
3. **Not the Right Team (15%)**: Missing technical skills or having founder misalignment.
4. **Outcompeted (10%)**: Competitors matching the offering or blocking distribution.
5. **Pricing / Cost Issues (10%)**: Selling products for less than the cost of customer acquisition (CAC > LTV).

## 2. Risk Assessment Framework (Risk Matrix)
Risks are graded based on **Probability (1-5)** and **Impact (1-5)**:

| Impact \ Probability | 1. Rare | 2. Unlikely | 3. Possible | 4. Likely | 5. Certain |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **5. Catastrophic** | Medium | Medium | High | Critical | Critical |
| **4. Major** | Low | Medium | High | High | Critical |
| **3. Moderate** | Low | Low | Medium | High | High |
| **2. Minor** | Low | Low | Low | Medium | Medium |
| **1. Negligible** | Low | Low | Low | Low | Low |

### Core Risk Types
1. **Market Risk**: Do customers care? Is the market large enough?
2. **Execution Risk**: Can we build and distribute this with the current budget/team?
3. **Technical Risk**: Are there unresolved technical barriers (e.g., LLM hallucinations, high API costs, complex real-time video processing)?
4. **Financial Risk**: Will the business burn through capital before finding Product-Market Fit (PMF)?
5. **Regulatory & Legal Risk**: Are there compliance issues (e.g., HIPAA for healthcare, COPPA for children, GDPR/CCPA for privacy)?

## 3. SWOT Analysis Template
A SWOT analysis categorizes internal and external factors:

```
                  INTERNAL                      EXTERNAL
       +----------------------------+----------------------------+
       | STRENGTHS                  | OPPORTUNITIES              |
       |  - Core IP / algorithms    |  - Emerging markets / trends|
       |  - Unique founder insight  |  - Competitor weaknesses   |
       |  - Execution speed         |  - Partnership opportunities|
  HELP |                            |                            |
-------+----------------------------+----------------------------+-------
  HURT | WEAKNESSES                 | THREATS                    |
       |  - Small budget / resource |  - Platform dependency     |
       |  - No brand visibility     |  - Aggressive competitors  |
       |  - Lack of distribution    |  - Changing regulations    |
       +----------------------------+----------------------------+
```

### Prompting Questions for SWOT
- **Strengths**: What is your unfair advantage? (e.g., proprietary dataset, domain expertise).
- **Weaknesses**: What resources are you lacking? Where do you have dependencies?
- **Opportunities**: What shift in technology, customer behavior, or policy makes this idea viable *now*?
- **Threats**: What could destroy this business overnight? (e.g., Google launching a free version).
