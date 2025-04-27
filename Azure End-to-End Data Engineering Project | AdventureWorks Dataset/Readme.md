Azure End-to-End Data Engineering Project | AdventureWorks Dataset

![Screenshot 2025-04-27 at 8 30 44 PM](https://github.com/user-attachments/assets/7d536cb2-43ef-4ee5-9759-3d8f5e48f310)


Welcome to my Azure Data Engineering project!
In this project, I built a complete end-to-end cloud data pipeline using Microsoft's Azure platform, simulating a real-world data engineering workflow.

Project Overview:

The goal was to create a fully automated, scalable data pipeline.

The project uses the popular AdventureWorks dataset, covering multiple tables such as customers, sales, products, and returns.

The architecture follows the Medallion design pattern (Bronze → Silver → Gold), ensuring clean separation between raw, transformed, and curated data.

Technologies Used:

Azure Data Factory (for orchestration and ingestion)

Azure Data Lake Storage Gen2 (for storing raw and transformed data)

Azure Databricks (for big data processing using Apache Spark)

Azure Synapse Analytics (for data warehousing and SQL-based querying)

Power BI (for business reporting and dashboarding)

Project Highlights:

Pulled data from GitHub APIs using dynamic pipelines in Azure Data Factory.

Organized data in Bronze, Silver, and Gold layers following best practices.

Built parameterized, reusable pipelines for scalable ingestion and transformations.

Processed and cleaned data using Databricks notebooks (Spark SQL).

Designed fact and dimension models in Synapse for efficient querying.

Connected Power BI to Synapse to build real-time dashboards.

Why this project? This project mimics real-world data engineering scenarios, including dynamic ingestion, schema design, warehouse optimization, and building business intelligence solutions.
It helped me sharpen practical skills necessary for cloud-based data engineering roles.

