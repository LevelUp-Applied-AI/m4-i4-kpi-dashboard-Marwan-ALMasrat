# Executive Summary — Amman Digital Market Analytics

## Overview
This analysis covers sales and customer data from the Amman Digital Market spanning January 2024 to June 2025. The dataset includes orders, products, customers, and order items across 6 Jordanian cities. All cancelled orders and erroneous quantity entries were excluded to ensure data accuracy.

---

## Top Findings

1. **Books generate the highest average order value at 140.93 JOD** — nearly 3x more than Food & Beverage (54.52 JOD), and this difference is statistically significant across all categories.
2. **Amman accounts for 38% of total revenue (31,438 JOD)**, but individual customers in Amman do not spend more per order than customers in Irbid — the gap is purely driven by order volume.
3. **Revenue is highly volatile month-to-month**, swinging from −39.4% in April 2025 to +151.7% in June 2025, with no stable growth trend across the 18-month period.

---

## Supporting Data

**Finding 1 — AOV by Category**
A one-way ANOVA confirmed that average order value differs significantly across product categories (F = 56.79, p < 0.001, η² = 0.21). Books lead at 140.93 JOD, followed by Electronics at 104.81 JOD. Food & Beverage trails at 54.52 JOD.
*(See: output/kpi3_aov_by_category.png)*

**Finding 2 — Revenue by City**
Amman generated 31,438 JOD versus Irbid's 14,501 JOD. However, a Welch's t-test showed no significant difference in order value per transaction (t = 0.63, p = 0.527, Cohen's d = 0.09), confirming the gap is volume-driven, not spend-driven.
*(See: output/kpi4_revenue_by_city.png)*

**Finding 3 — Monthly Revenue Volatility**
Month-over-month growth ranged from −39.4% to +151.7% with no consistent direction. The 18-month revenue trend shows irregular spikes rather than organic growth.
*(See: output/kpi1_monthly_revenue.png, output/kpi2_mom_growth.png)*

---

## Recommendations

1. **Invest in Books and Electronics marketing** — these two categories drive the highest order values (140.93 JOD and 104.81 JOD respectively). Targeted promotions or loyalty discounts in these categories will have the highest revenue impact per campaign.

2. **Grow order volume outside Amman** — since customers in Irbid, Zarqa, and other cities spend just as much per order as Amman customers, expanding reach through regional delivery or city-specific campaigns can increase total revenue without requiring higher per-order spending.

3. **Investigate revenue spikes before planning forecasts** — the extreme volatility (especially June 2025 at +151%) suggests the business has no predictable demand pattern. A root cause analysis of high and low months should be conducted before setting revenue targets or inventory plans.