# KPI Framework — Amman Digital Market

Define 5 KPIs for the Amman Digital Market. At least 2 must be time-based and 1 must be cohort-based.

---

## KPI 1 *(Time-Based)*

- **Name:** Monthly Revenue Trend
- **Definition:** Total revenue generated across all non-cancelled orders per calendar month
- **Formula:** `SUM(quantity × unit_price)` grouped by year-month
- **Data Source (tables/columns):** `order_items.quantity`, `order_items.unit_price`, `orders.order_date`, `orders.status`
- **Baseline Value:** January 2024 = 5,878 JOD | Peak: June 2025 = 10,173 JOD | Low: May 2025 = 4,042 JOD
- **Interpretation:** Revenue is highly volatile with no consistent upward trend. The spike in June 2025 (+151%) warrants investigation — it may reflect a seasonal campaign or a data anomaly.

---

## KPI 2 *(Time-Based)*

- **Name:** Month-over-Month Revenue Growth Rate
- **Definition:** The percentage change in total revenue compared to the previous month
- **Formula:** `(current_month_revenue - prev_month_revenue) / prev_month_revenue × 100`
- **Data Source (tables/columns):** `order_items.quantity`, `order_items.unit_price`, `orders.order_date`
- **Baseline Value:** Average MoM growth ≈ 12.3% | Best month: June 2025 (+151.7%) | Worst month: April 2025 (−39.4%)
- **Interpretation:** Growth is inconsistent and swings between large gains and losses, suggesting the market lacks a stable demand engine. Months with negative growth should trigger a review of marketing activity.

---

## KPI 3

- **Name:** Average Order Value (AOV) by Product Category
- **Definition:** The mean revenue per order broken down by product category
- **Formula:** `SUM(revenue) / COUNT(DISTINCT order_id)` grouped by category
- **Data Source (tables/columns):** `order_items.quantity`, `order_items.unit_price`, `order_items.order_id`, `products.category`
- **Baseline Value:** Books = 140.93 JOD | Electronics = 104.81 JOD | Clothing = 96.02 JOD | Home & Garden = 90.65 JOD | Sports = 55.41 JOD | Food & Beverage = 54.52 JOD
- **Interpretation:** Books have the highest AOV despite typically being low-cost items, which may indicate bulk purchasing. Food & Beverage has the lowest AOV and may need bundling strategies to increase basket size.

### Statistical Validation (ANOVA)
| Element | Value |
|---|---|
| H₀ | AOV is equal across all product categories |
| H₁ | At least one category has a significantly different AOV |
| Test Used | One-way ANOVA — appropriate for comparing means across 3+ independent groups |
| F-Statistic | 56.7853 |
| p-value | 0.0000 |
| Effect Size (η²) | 0.2111 — medium-to-large effect |
| Interpretation | We reject H₀. AOV differs significantly across categories. Category drives roughly 21% of the variance in order value, meaning product category is a meaningful lever for revenue strategy. |

---

## KPI 4

- **Name:** Revenue by City
- **Definition:** Total revenue contributed by customers in each city
- **Formula:** `SUM(quantity × unit_price)` grouped by customer city
- **Data Source (tables/columns):** `order_items.quantity`, `order_items.unit_price`, `customers.city`
- **Baseline Value:** Amman = 31,438 JOD | Irbid = 14,501 JOD | Zarqa = 9,684 JOD | Madaba = 9,382 JOD | Salt = 8,954 JOD | Aqaba = 8,335 JOD
- **Interpretation:** Amman dominates with 38% of total revenue. However, Irbid, Zarqa, and other cities collectively generate more, suggesting untapped growth potential outside the capital.

### Statistical Validation (Welch's t-test)
| Element | Value |
|---|---|
| H₀ | Mean order value is equal between Amman and Irbid customers |
| H₁ | Mean order value differs between Amman and Irbid customers |
| Test Used | Welch's t-test — appropriate for two independent groups with potentially unequal variances |
| t-statistic | 0.6338 |
| p-value | 0.5273 |
| Effect Size (Cohen's d) | 0.0943 — negligible effect |
| Interpretation | We fail to reject H₀. Despite Amman generating more total revenue, individual order values are not significantly different from Irbid. Amman's revenue lead is driven by volume of orders, not higher spending per order. |

---

## KPI 5 *(Cohort-Based)*

- **Name:** Repeat Purchase Rate by Registration Cohort
- **Definition:** The percentage of customers in each registration cohort who placed 2 or more orders
- **Formula:** `COUNT(customers with order_count ≥ 2) / COUNT(total customers in cohort) × 100`
- **Data Source (tables/columns):** `customers.customer_id`, `customers.registration_date`, `orders.order_id`, `orders.customer_id`
- **Baseline Value:** All cohorts (2023-H1 through 2025-H1) show a retention rate of 100%
- **Interpretation:** A 100% repeat purchase rate across all cohorts is statistically improbable and likely reflects a data quality issue — either the seed data was generated with guaranteed repeat purchases, or the cutoff for "repeat" is too lenient. This KPI should be re-evaluated with real transactional data before being used for business decisions.