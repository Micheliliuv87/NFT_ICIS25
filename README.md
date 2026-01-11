# Research Code and Results for ICIS 2025 Publication

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

# Code Files Structure

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
│   └── [EDA](Analysis/EDA/)                    # Exploratory data analysis
│       ├── Distribution_association.ipynb
│       ├── Offer_data_analysis0915.ipynb
│       └── Transfer_clusters.ipynb
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
├── LICENSE
└── README.md
```