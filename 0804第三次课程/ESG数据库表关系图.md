# ESG 数据库（esg_db）表关系图

PostgreSQL 15.15，`public` schema 共 32 张表（本图含 28 张，排除 5 张 `hkex_climate_disclosure_backup_*` 备份表）。表间无显式外键，连线为按共享键（`stock_code / report_id / credit_code / facility_id / permit_id / doc_id` 等）推断的逻辑关系。

```mermaid
flowchart LR
    classDef hkex fill:#1e3a8a,color:#fff,stroke:#000
    classDef core fill:#065f46,color:#fff,stroke:#000
    classDef sumz fill:#9a3412,color:#fff,stroke:#000
    classDef indus fill:#4c1d95,color:#fff,stroke:#000
    classDef ai fill:#9d174d,color:#fff,stroke:#000
    classDef sys fill:#374151,color:#fff,stroke:#000

    subgraph G1["① 港交所披露数据 hkex_*"]
        C1["hkex_companies<br/>2303 家港股公司"]
        R1["hkex_esg_reports<br/>4954 份 ESG 报告"]
        I1["hkex_esg_indicators<br/>84.3万 条指标"]
        D1["hkex_climate_disclosure<br/>3.6万 条气候披露"]
        E1["hkex_emissions<br/>排放记录"]
        F1["hkex_facilities<br/>704 个设施"]
        S1["hkex_supply_chain<br/>3.9万 条供应链"]
    end

    subgraph G2["② 加工核心 esg_*"]
        CO["companies<br/>2398 家企业"]
        RP["esg_reports<br/>5497 份报告"]
        IN["esg_indicators<br/>22.8万 条指标"]
        SCD["supply_chain_data<br/>1万 条供应链"]
    end

    subgraph G3["③ 中国上市公司/企业环境数据 sumz_*"]
        SR["sumz_company_registry<br/>47.6万 家企业注册库"]
        WP["sumz_waste_permit<br/>24.1万 排污许可"]
        AIR["sumz_air_emission<br/>114万 大气排放"]
        WAT["sumz_water_emission<br/>45.6万 水排放"]
        DISC["sumz_env_disclosure<br/>1.7万 环境披露"]
        RAT["sumz_third_party_ratings<br/>5113 第三方评级"]
    end

    subgraph G4["④ 工业企业 industrial_*"]
        IF["industrial_facilities<br/>1117 个设施"]
        IEM["industrial_emissions<br/>2295 排放"]
        IAC["industrial_accidents<br/>事故记录"]
        EIA["eia_projects<br/>环评项目"]
    end

    subgraph G5["⑤ 研究 / AI 应用"]
        RM["research_mda_multimodal_reports<br/>139 份多模态报告"]
        OV["research_mda_esg_supply_chain_overlay<br/>供应链叠加分析"]
        KC["env_knowledge_chunks<br/>4.7万 知识切片(向量库)"]
    end

    subgraph G6["⑥ API 服务"]
        AU["api_users<br/>API 账户"]
        AL["api_usage_logs<br/>调用日志"]
        DL["data_update_logs<br/>数据更新日志"]
    end

    %% --- 港交所组内部 ---
    C1 -->|"company_id · stock_code"| R1
    R1 -->|"report_id"| I1
    R1 -->|"report_id"| D1
    R1 -->|"report_id"| E1
    R1 -->|"report_id"| F1
    R1 -->|"report_id"| S1
    E1 -->|"facility_id"| F1

    %% --- 加工核心 ---
    CO -->|"company_id · stock_code"| RP
    RP -->|"report_id"| IN
    SCD -->|"report_id"| R1

    %% --- sumz 环境数据链 ---
    SR -->|"company_id"| WP
    WP -->|"permit_id"| AIR
    WP -->|"permit_id"| WAT
    SR -->|"credit_code"| DISC
    SR -->|"stock_code"| RAT

    %% --- 工业企业 ---
    IF -->|"facility_id"| IEM
    IF -->|"facility_id"| IAC
    IF -->|"facility_id"| EIA

    %% --- 研究 / AI ---
    RM -->|"doc_id"| OV
    RM -->|"stock_code"| CO
    KC -->|"document_id → doc_id"| RM

    %% --- API 服务 ---
    AU -->|"user_id"| AL

    class C1,R1,I1,D1,E1,F1,S1 hkex
    class CO,RP,IN,SCD core
    class SR,WP,AIR,WAT,DISC,RAT sumz
    class IF,IEM,IAC,EIA indus
    class RM,OV,KC ai
    class AU,AL,DL sys
```
