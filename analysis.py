"""Integration 4 — KPI Dashboard: Amman Digital Market Analytics

Extract data from PostgreSQL, compute KPIs, run statistical tests,
and create visualizations for the executive summary.

Usage:
    python analysis.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine

# ── Database Connection ───────────────────────────────────
def connect_db():
    engine = create_engine(
        "postgresql+psycopg://postgres:postgres@localhost:5432/amman_market"
    )
    return engine

# ── Data Extraction & Cleaning ────────────────────────────
def extract_data(engine):
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    orders = pd.read_sql("SELECT * FROM orders WHERE status != 'cancelled'", engine)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    order_items = pd.read_sql("SELECT * FROM order_items WHERE quantity <= 100", engine)
    
    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items
    }

# ── KPI Calculations ──────────────────────────────────────
def compute_kpis(data_dict):
    customers = data_dict["customers"].copy()
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    # Merge all tables to build the unified revenue dataframe
    df = (
        order_items.merge(orders, on="order_id")
        .merge(products, on="product_id")
        .merge(customers[['customer_id', 'city', 'registration_date']], on='customer_id')
    )
    df['revenue'] = df['quantity'] * df['unit_price']
    df['year_month'] = df['order_date'].dt.to_period('M')
    df['registration_date'] = pd.to_datetime(df['registration_date'])

    # ── KPI 1: Monthly Revenue Trend
    monthly_revenue = df.groupby('year_month')['revenue'].sum().sort_index()

    # ── KPI 2: Month-over-Month Growth Rate
    mom_growth = monthly_revenue.pct_change() * 100
    mom_growth = mom_growth.dropna()

    # ── KPI 3: Average Order Value by Category
    order_value = df.groupby(['order_id','category'])['revenue'].sum().reset_index()
    aov_by_category = order_value.groupby('category')['revenue'].mean().sort_values(ascending=False).reset_index().rename(columns={'revenue':'aov'})

    # ── KPI 4: Revenue by City
    revenue_by_city = df.dropna(subset=['city']).groupby('city')['revenue'].sum().sort_values(ascending=False).reset_index()

    # ── KPI 5: Repeat Purchase Rate by Cohort
    def cohort_label(dt):
        return f"{dt.year}-{'H1' if dt.month<=6 else 'H2'}"
    customers['cohort'] = customers['registration_date'].apply(cohort_label)

    order_counts = orders.groupby('customer_id')['order_id'].nunique().reset_index().rename(columns={'order_id':'order_count'})
    merged = customers.merge(order_counts, on='customer_id', how='left')
    merged['order_count'] = merged['order_count'].fillna(0)
    merged['is_repeat'] = merged['order_count'] >= 2

    cohort_retention = merged.groupby('cohort').agg(total=('customer_id','count'), repeat=('is_repeat','sum')).reset_index()
    cohort_retention['retention_rate'] = cohort_retention['repeat']/cohort_retention['total']*100

    return {
        "monthly_revenue": monthly_revenue,
        "mom_growth": mom_growth,
        "aov_by_category": aov_by_category,
        "revenue_by_city": revenue_by_city,
        "cohort_retention": cohort_retention,
        "revenue_df": df
    }

# ── Statistical Hypothesis Testing ───────────────────────
def run_statistical_tests(data_dict):
    df = compute_kpis(data_dict)['revenue_df']

    # Hypothesis 1: Compare order values between Amman and Irbid
    order_val_city = df.groupby(['order_id','city'])['revenue'].sum().reset_index()
    amman = order_val_city[order_val_city['city']=='Amman']['revenue'].values
    irbid = order_val_city[order_val_city['city']=='Irbid']['revenue'].values
    t_stat_old, p_value_old = stats.ttest_ind(amman, irbid, equal_var=False)
    pooled_std_old = np.sqrt((np.std(amman, ddof=1)**2 + np.std(irbid, ddof=1)**2)/2)
    cohens_d_old = (np.mean(amman)-np.mean(irbid))/pooled_std_old

    test_old = {
        "test":"Welch's t-test (Amman vs Irbid)",
        "t_stat":round(t_stat_old,4),
        "p_value":round(p_value_old,4),
        "cohens_d":round(cohens_d_old,4),
        "significant": p_value_old<0.05
    }

    # Hypothesis 2: Compare order values between new and existing customers
    cutoff_date = pd.Timestamp('2025-01-01')
    customers = df[['customer_id','registration_date']].drop_duplicates().copy()
    customers['type'] = np.where(customers['registration_date'] < cutoff_date, 'old','new')
    order_val_customer = df.groupby(['order_id','customer_id'])['revenue'].sum().reset_index()
    order_val_customer = order_val_customer.merge(customers[['customer_id','type']], on='customer_id')
    new_customers = order_val_customer[order_val_customer['type']=='new']['revenue'].values
    old_customers = order_val_customer[order_val_customer['type']=='old']['revenue'].values

    t_stat_new, p_value_new = stats.ttest_ind(new_customers, old_customers, equal_var=False)
    pooled_std_new = np.sqrt((np.std(new_customers, ddof=1)**2 + np.std(old_customers, ddof=1)**2)/2)
    cohens_d_new = (np.mean(new_customers)-np.mean(old_customers))/pooled_std_new

    test_new = {
        "test":"Welch's t-test (New vs Old Customers)",
        "t_stat":round(t_stat_new,4),
        "p_value":round(p_value_new,4),
        "cohens_d":round(cohens_d_new,4),
        "significant": p_value_new<0.05
    }

    # Hypothesis 3: One-way ANOVA to check if AOV differs across product categories
    order_val_cat = df.groupby(['order_id','category'])['revenue'].sum().reset_index()
    groups = [g['revenue'].values for _, g in order_val_cat.groupby('category')]
    f_stat, p_value_cat = stats.f_oneway(*groups)
    grand_mean = order_val_cat['revenue'].mean()
    ss_between = sum(len(g)*(g.mean()-grand_mean)**2 for g in groups)
    ss_total = sum((order_val_cat['revenue']-grand_mean)**2)
    eta_squared = ss_between/ss_total
    test_anova = {
        "test":"One-way ANOVA (AOV by Category)",
        "f_stat":round(f_stat,4),
        "p_value":round(p_value_cat,4),
        "eta_squared":round(eta_squared,4),
        "significant": p_value_cat<0.05
    }

    return {"city_test":test_old,"customer_test":test_new,"category_aov_test":test_anova}

# ── Chi-Square Test: Category vs City ────────────────────
def run_chiSquare_test(data_dict):
    df = compute_kpis(data_dict)['revenue_df']

    # Build contingency table: product category vs customer city
    contingency_table = pd.crosstab(df['category'], df['city'])

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    # Effect size: Cramér's V
    n = contingency_table.values.sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = round(np.sqrt(chi2 / (n * min_dim)), 4)

    return {
        "test": "Chi-Square Test (Category vs City)",
        "chi2_stat": round(chi2, 4),
        "p_value": round(p_value, 4),
        "degrees_of_freedom": dof,
        "cramers_v": cramers_v,
        "significant": p_value < 0.05
    }

# ── Chart & Plot Generation ───────────────────────────────
def create_visualizations(kpi_results):
    sns.set_theme(style="whitegrid", font_scale=1.05)
    sns.set_palette("colorblind")
    COLORS = sns.color_palette("colorblind")
    os.makedirs("output", exist_ok=True)
    df = kpi_results['revenue_df']

    # KPI 1: Monthly Revenue
    plt.figure(figsize=(12,5))
    x = [str(p) for p in kpi_results['monthly_revenue'].index]
    y = kpi_results['monthly_revenue'].values
    plt.plot(x,y,marker='o',color=COLORS[0])
    plt.fill_between(x,y,alpha=0.1,color=COLORS[0])
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (JOD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/kpi1_monthly_revenue.png",dpi=150)
    plt.close()

    # KPI 2: MoM Growth
    plt.figure(figsize=(12,5))
    y = kpi_results['mom_growth'].values
    bar_colors = [COLORS[2] if v>=0 else COLORS[3] for v in y]
    plt.bar(x,y,color=bar_colors)
    plt.axhline(0, color='black', linestyle='--')
    plt.title("Month-over-Month Revenue Growth")
    plt.xlabel("Month")
    plt.ylabel("MoM Growth (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/kpi2_mom_growth.png",dpi=150)
    plt.close()

    # KPI 3: AOV by Category
    fig, axes = plt.subplots(1,2,figsize=(14,6))
    aov_df = kpi_results['aov_by_category']
    axes[0].barh(aov_df['category'], aov_df['aov'], color=COLORS[:len(aov_df)])
    axes[0].set_title("Average Order Value by Category")
    sns.boxplot(data=df,y='category',x='revenue',order=aov_df['category'].tolist(),palette="colorblind",ax=axes[1])
    axes[1].set_title("Order Value Distribution by Category")
    plt.tight_layout()
    plt.savefig("output/kpi3_aov_by_category.png",dpi=150)
    plt.close()

    # KPI 4: Revenue by City
    city_df = kpi_results['revenue_by_city']
    plt.figure(figsize=(10,6))
    bars = plt.bar(city_df['city'], city_df['revenue'], color=COLORS[:len(city_df)])
    for bar in bars:
        plt.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,f"{bar.get_height():,.0f}",ha='center')
    plt.title("Revenue by City")
    plt.xlabel("City")
    plt.ylabel("Revenue (JOD)")
    plt.tight_layout()
    plt.savefig("output/kpi4_revenue_by_city.png",dpi=150)
    plt.close()

    # KPI 5: Cohort Retention
    cohort_df = kpi_results['cohort_retention']
    plt.figure(figsize=(10,5))
    bars = plt.bar(cohort_df['cohort'],cohort_df['retention_rate'],color=COLORS[:len(cohort_df)])
    for bar, (_, row) in zip(bars,cohort_df.iterrows()):
        plt.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,f"{row['retention_rate']:.0f}%",ha='center')
    plt.title("Repeat Purchase Rate by Cohort")
    plt.xlabel("Cohort")
    plt.ylabel("Retention Rate (%)")
    plt.ylim(0,120)
    plt.tight_layout()
    plt.savefig("output/kpi5_cohort_retention.png",dpi=150)
    plt.close()

# ── Main Pipeline ─────────────────────────────────────────
def main():
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)
    stats_results = run_statistical_tests(data)
    chi_result = run_chiSquare_test(data)
    create_visualizations(kpis)

    # Print summary of all computed KPIs and test results
    print("\n=== KPI SUMMARY ===")
    print(kpis['monthly_revenue'])
    print(kpis['mom_growth'])
    print(kpis['aov_by_category'])
    print(kpis['revenue_by_city'])
    print(kpis['cohort_retention'])

    print("\n=== STATISTICAL TESTS ===")
    for key, val in stats_results.items():
        print(f"{key}: {val}")

    print("\n=== CHI-SQUARE TEST ===")
    print(chi_result)

if __name__ == "__main__":
    main()