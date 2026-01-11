# **Research Code and Results for ICIS 2025 Publication**

If you would like to cite my paper: 

```
Liu, Qirui and Garg, Rajiv, "Unveiling NFT Price Dynamics: The Interplay of Traits, Timing, and Social Signaling" (2025). ICIS 2025 Proceedings. 12. https://aisel.aisnet.org/icis2025/fintech/fintech/12
```

LaTex: 

```
@inproceedings{LiuGarg2025,
  author = {Liu, Qirui and Garg, Rajiv},
  title = {Unveiling {NFT} Price Dynamics: The Interplay of Traits, Timing, and Social Signaling},
  booktitle = {ICIS 2025 Proceedings},
  year = {2025},
  pages = {12},
  url = {https://aisel.aisnet.org/icis2025/fintech/fintech/12},
  note = {[Online]. Available: \url{https://aisel.aisnet.org/icis2025/fintech/fintech/12}}
}
```

### **Code Files Structure**

```markdown
NFT_ICIS25/
├── [Analysis](Analysis/)                       # Research analysis notebooks and models
│   ├── [Analysis](Analysis/Analysis/)
│   │   ├── [Final_Models](Analysis/Analysis/Final_Models/)
│   │   │   ├── Model1_Final.ipynb
│   │   │   ├── Model2_0805.ipynb
│   │   │   ├── Model3_Final.ipynb
│   │   │   ├── Panel_for_Model2.csv
│   │   │   ├── df_offer_monthly.csv
│   │   │   ├── df_table1.csv
│   │   │   ├── df_table2.csv
│   │   │   ├── df_table3.csv
│   │   │   ├── df_table4.csv
│   │   │   ├── df_table5.csv
│   │   │   ├── df_table6.csv
│   │   │   └── df_table7.csv
│   │   └── [Results](Analysis/Analysis/Results/)
│   │       ├── 0805Model_Comparison_Table.csv
│   │       ├── best_AdaBoost.joblib
│   │       ├── best_GradientBoosting.joblib
│   │       ├── best_RandomForest.joblib
│   │       ├── best_XGBoost.joblib
│   │       ├── cluster_2_features.csv
│   │       ├── dummies_result.csv
│   │       ├── feature_importance.png
│   │       └── [more model outputs...]
│   │ 
│   └── [EDA](Analysis/EDA/)                    # Exploratory data analysis
│       ├── Distribution_association.ipynb
│       ├── Offer_data_analysis0915.ipynb
│       └── Transfer_clusters.ipynb
│ 
├── [Data](Data/)                               # Raw and processed datasets
│   ├── [Collection](Data/Collection/)          # Data collection scripts
│   │   ├── nft_transaction_data/
│   │   │   ├── EVENT_JSON_format.json
│   │   │   └── nft_event_offer.py
│   │   └── user_address_data/
│   │       ├── Etherscan_User.py
│   │       ├── etherscan_fix.py
│   │       └── rename_address.py
│   └── [Handling](Data/Handling/)              # Data cleaning notebooks
│       └── Table_NFTs.ipynb
│ 
├── LICENSE
│ 
├── requirements.txt
│ 
└── README.md
```

## **Detail Guide**

#### **Data** 

Data consists two parts: 

**Collection** ([`Data/Collection/`](Data/Collection/)) contains the code used to collect the data for both <ins>*NFT Characteristics*</ins> and <ins>*Buyer/Seller Characteristics*</ins>. 

* Under `nft_transaction_data`, the scripts retrieve detailed NFT event information (7 event types; see the [OpenSea API documentation](https://docs.opensea.io/reference/list_events_by_nft_1) for specifics). You must edit `nft_event_offer.py` to add your own OpenSea API key and configure your preferred file paths before running the code.

* Under `user_address_data`, the scripts obtain the address information of the Buyer/Seller that appeared in both N and N-1 sales. Table creation is a requirement in order to run any code under this file. `Etherscan_User.py` is the primary script to obtain the data, and `etherscan_fix.py` is for validating the data collection and recollecting the missing data due to API Errors. `rename_address.py` helps you organize the data collected to have its name by correct buyer and seller addresses. 


**Handling** ([`Data/Handling/`](Data/Handling/)) contains the code used for Table Creation (Parsing the very large json files).

* This is very necessary for table creations. Tables are made for various purposes. Please view the detailed `Table_NFTs.ipynb` for specific information (what each table is for). Note: This section is primarily created for Github Repo showcase, where some portions are different than the original file handling. 

```
In order to do your own data collection, you must go through the steps above. The data (198 GB) is too large for the GitHub Repo to handle.
```

#### **Analysis**

Because the raw data is large, all derived tables are stored in [`Analysis/Analysis/Final_Models/`](Analysis/Analysis/Final_Models/). This folder also contains the final models for each section of the paper, with results documented in the corresponding `.ipynb` notebooks. [`Analysis/EDA/`](Analysis/EDA/) contains the exploratory data analysis notebooks. The `Results` folder stores selected saved outputs and artifacts for the final models.


#### **Environment**

Install dependencies with:

```bash
pip install -r requirements.txt
```