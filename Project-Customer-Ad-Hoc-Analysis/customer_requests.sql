-- Request 01 ( Provide the list of markets in which customer  "Atliq  Exclusive"  operates its 
-- business in the  APAC  region.)
Select  count( customer) as total_count , customer ,region from dim_customer
where region = 'APAC' and customer = 'Atliq Exclusive' group by region;

--  Request 02 -- What is the percentage of unique product increase in 2021 vs. 2020? The 
-- final output contains these fields.

select  *
from 
(with cte1 as (select count(distinct product_code) cnt , fiscal_year from fact_sales_monthly
group by  fiscal_year having fiscal_year)
select fiscal_year,
case when fiscal_year = 2020 then cnt else 0 end as unique_product2020,
case when fiscal_year = 2021 then cnt else 0 end as unique_product2021
from cte1) sq1
join fact_sales_monthly fm
on sq1.fiscal_year = fm.fiscal_year;

show tables;
-- Request 03 -- Provide a report with all the unique product counts for each  segment  and 
-- sort them in descending order of product counts. The final output contains  2 fields, 
select count(distinct product_code) as prod_cnt , segment from dim_product
group by segment order by prod_cnt desc;


--  Request 04 -- Follow-up: Which segment had the most increase in unique products in 2021 vs 2020?
select * from fact_sales_monthly;
select * from dim_product;
select * , abs(cnt2020-cnt2021) as diffrence
from
(select segment , 
SUM(CASE WHEN cnt2020 > 0 THEN cnt2020 ELSE 0 END) AS cnt2020,
    SUM(CASE WHEN cnt2021 > 0 THEN cnt2021 ELSE 0 END) AS cnt2021
 from 
(with cte1 as (select dp.segment, fm.fiscal_year,
count(fm.product_code) as cnt
from fact_sales_monthly as fm
join dim_product as dp
on fm.product_code  = dp.product_code
group by dp.segment, fm.fiscal_year)
select segment, case when fiscal_year = 2020 then cnt else 0 end as cnt2020,
case when fiscal_year = 2021 then cnt else 0 end as cnt2021
from cte1) sq1
group by segment) sq2;

-- Request 05 -- Get the products that have the highest and lowest manufacturing costs. The final output should contain these fields,
select * from fact_manufacturing_cost;
select * from dim_product; 

(select fm.product_code , dp.product , sum(fm.manufacturing_cost) as total_cost
from fact_manufacturing_cost as fm
join dim_product as dp
on fm.product_code = dp.product_code
group by fm.product_code , dp.product
order by total_cost desc limit 1 )
union all
(select fm.product_code , dp.product , sum(fm.manufacturing_cost) as total_cost
from fact_manufacturing_cost as fm
join dim_product as dp
on fm.product_code = dp.product_code
group by fm.product_code , dp.product
order by total_cost limit 1 );


--  Generate a report which contains the top 5 customers who received an average high  pre_invoice_discount_pct  for the  fiscal  year 2021  and in the 
-- Indian  market.

select * from fact_pre_invoice_deductions;
select * from dim_customer; 

select customer_code , customer, market,
avg(case when discount2021 > 0 then discount2021 else 0 end) as discount2021
from 
(select fp.customer_code , dc.customer, dc.market,
case when fp.fiscal_year = 2021 then fp.pre_invoice_discount_pct else 0 end as discount2021
from fact_pre_invoice_deductions as fp
join dim_customer as dc 
on fp.customer_code = dc.customer_code
where dc.market = 'India'
)sq1
group by customer_code , customer,market;



select * from fact_sales_monthly; 
select * from dim_customer;
select * from  fact_gross_price;

select month , year , round(sum(gross_amt),2) as gross_amt
from
(select 
extract(month from sq1.Date) as month,extract(year from sq1.Date) as year,  sq1.gross_amt
from(select 
fm.Date,fm.product_code , fm.customer_code , (fm.sold_quantity * fp.gross_price) as gross_amt
from fact_sales_monthly as fm
join fact_gross_price as fp
on fm.product_code = fp.product_code)sq1
join dim_customer as dc 
on sq1.customer_code  = dc.customer_code
where dc.customer = 'Atliq Exclusive')sq2
group by month, year
order by month;


-- Request 08 -  In which quarter of 2020, got the maximum total_sold_quantity? The final output contains these fields sorted by the total_sold_quantity, 
select * from fact_sales_monthly;
select distinct qtr ,total_max_qty
from
(select
qtr, 
max(sold_quantity) over (partition by qtr ) as total_max_qty 
from(with cte1 as (select extract(month from date) as months, sold_quantity
from fact_sales_monthly
where fiscal_year = 2020)
select months , sold_quantity,case when months in (9,10,11) then 1
	when months in(12,1,2) then 2
    when months in (3,4,5) then 3 
    else 4 end as qtr
from cte1) sq1
group by qtr) sq2
;

--  Request 09 -  Which channel helped to bring more gross sales in the fiscal year 2021 
-- and the percentage of contribution?  The final output  contains these fields
select * from fact_sales_monthly;
select * from fact_gross_price;
select * from  dim_customer;

select
sq2.channel , round(sq2.total_sales,2) as total_sales 
from (select 
  dc.channel,sum(sq1.gross_sale) as total_sales 
from (select fm.date,fm.product_code , fm.customer_code, sum(fm.sold_quantity * fp.gross_price) as gross_sale
from fact_sales_monthly as fm
join fact_gross_price as fp
on fm.product_code = fp.product_code
where fm.fiscal_year = 2021 and fp.fiscal_year = 2021
group by fm.date,fm.product_code, fm.customer_code)sq1
join dim_customer as dc
on sq1.customer_code = dc.customer_code
group by dc.channel) sq2;

-- Request 10--  Get the Top 3 products in each division that have a high total_sold_quantity in the fiscal_year 2021?
select * from fact_sales_monthly;
select * from dim_product; 

select *
from (with cte1 as (select 
dp.product , dp.division , sum(sold_quantity) as total_sold_quantity
from fact_sales_monthly as fm
join dim_product as dp
on fm.product_code = dp.product_code
where fm.fiscal_year = 2021
group by dp.product , dp.division)
select *,
dense_rank() over(partition by division order by total_sold_quantity desc) as rnk
from cte1) sq1
where rnk <=3;
