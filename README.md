# Aircraft Spare Parts Inventory Optimization & Simulation System

## 📍 Status

    Section 2: Currently finishing up on the data corruption pipline. 

---
## High-level Description

This project is an **end-to-end supply chain analytics, forecasting, and optimization system** designed to model aircraft spare parts demand, optimize inventory policies, and evaluate cost vs. service-level tradeoffs using **Python, SQL, statistical forecasting, and Monte Carlo simulation**.

It is built to mirror the real responsibilities of an **Inventory Modeling / Supply Chain Analytics** role and demonstrates production-ready data engineering, modeling, and decision-support workflows.

## ⭐ Why Am I Building This?

Having worked for my family's business doing sports and trading card wholesaling while pursuing a master's degree in computer science with a focus on AI/ML I have developed an interest in
forecasting algorithms. I did not know much about the aircraft industry before this project, but I got inspiration from a Boeing job description and went from there.

---

## Formal Project Objectives

- Build and manage clean, structured inventory datasets  
- Forecast intermittent spare-parts demand  
- Optimize reorder points and order quantities under uncertainty  
- Simulate real-world supply chain behavior  
- Quantify cost, service level, and operational risk  
- Provide decision-ready optimization recommendations  

---

##  1. Dataset Creation & SQL Inventory System

A fully relational SQLite inventory database is built to support modeling, simulation, and analysis. The base tables (e.g., parts, warehouses, suppliers) are initially generated using a Large Language Model (LLM) to create realistic, domain-consistent aircraft parts, suppliers, and logistics metadata that mirrors real aerospace Maintenance, Repair, and Overhaul (MRO) systems.

### Data Corruption
To avoid relying on unrealistically perfect synthetic data, the raw datasets are then passed through a **probabilistic data corruption pipeline** that intentionally injects common real-world data quality issues such as missing records, outliers, inconsistent formats, and timing errors. This simulates the kinds of imperfections found in production Enterprise Resource Planning (ERP), maintenance, and supply-chain systems.


### Core Tables
- `aircraft_parts`
- `daily_demand`
- `orders`
- `stock_levels`
- `supplier_lead_times`
- `warehouse_locations`

### Example Fields (Aircraft Part)
- Part ID  
- Part Code  
- Category  
- Description  
- ATA Chapter
- Criticality
- Unit Cost USD
- Lead Time (Days)
 

---

## 2. Data Cleaning & Validation Engine (Python) 📍

The corrupted “raw” data is subsequently processed by a dedicated **data cleaning and validation engine**, producing a clean, model-ready dataset used for forecasting, optimization, and simulation. This approach ensures the downstream models are robust to realistic data issues rather than being tuned to idealized inputs.

### Features
- Missing data handling  
- Outlier detection  
- Bad demand correction  
- Lead-time normalization  
- Demand smoothing  

### Output
- Clean, validated dataset ready for forecasting and simulation

---

## 3. Demand Forecasting Engine

### Forecasting Models 
- Moving Average  
- Exponential Smoothing  
- ARIMA / SARIMAX  

### Model Evaluation
For each part, the system computes:
- MAE (Mean Absolute Error)  
- RMSE (Root Mean Square Error)  
- MAPE (Mean Absolute Percentage Error)  

The **best-performing forecasting model is automatically selected per part** based on accuracy.

---

## 4. Reorder Point & Quantity Optimization Engine

For every part, the system computes:

- Safety Stock  
- Reorder Point  
- EOQ (Economic Order Quantity)  

### Constraints Included
- Service level targets: **90%, 95%, 99%**  
- Lead-time variability

---

## 5. Supply Chain Simulation (Monte Carlo Core)

A **discrete-time Monte Carlo simulation engine** models real operational uncertainty.

### Simulated Processes
- Daily random demand  
- Random supplier delays  
- Order arrivals  
- Stockouts  

### Performance Metrics Tracked
- Inventory level over time  
- Backorders  
- Total cost  
- Service level  
- Cycle time  

### Simulation Scale
- 1,000+ full simulation runs  
- Direct comparison of different inventory policies   

---

## 6. Cost & Performance Analysis Dashboard

This module quantifies tradeoffs between **cost, risk, and performance**.

### Key Metrics Visualized
- Holding cost vs. stockout cost  
- Service level vs. total cost  
- Fill rate  
- Lead-time variability impact  
- Forecast error impact on inventory levels

---

## 7. Automated Optimization Scenario Engine

Users can simulate advanced operational scenarios, including:

- Different supplier delays  
- Demand spikes  
- Multiple warehouse networks  
- Emergency part shortages  

### Output
- System automatically recommends the **optimal inventory policy per scenario**

---

