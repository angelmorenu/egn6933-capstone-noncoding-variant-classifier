# M.S. Applied Data Science: Capstone Project Proposal

**Due Date:** January 25, 2025  
**Student Name:** Angel Morenu  
**Course:** EGN 6933 – Project in Applied Data Science  
**Project Type:** Individual

---

## 1. Project Title & Team Members

**Project Name:** Machine Learning Classification of Pathogenic vs. Benign Non-Coding Genetic Variants Using DNA Sequence Embeddings

**Team Lead:** Angel Morenu (Individual Project)

**Collaboration:** Dylan Tan provided guidance and reference code on handling embedding-style feature datasets. Because the dataset shared is limited to coding variants, it will not be used in this project, which focuses on non-coding variants.

---

## 2. Problem Statement & Impact

The majority of genetic variants associated with human disease occur in non-coding regions of the genome, where their functional effects are difficult to interpret experimentally. While coding variants typically produce observable consequences on protein structure and function, non-coding variants exert subtler regulatory effects that remain largely opaque and represent a major bottleneck in rare disease interpretation and precision medicine workflows.

This capstone focuses on a prediction-focused, semester-feasible supervised learning task: binary classification of non-coding genetic variants as pathogenic versus benign using pretrained DNA sequence embeddings. The objective is not to resolve the complete mechanistic basis of variant pathogenicity, but rather to construct a reproducible machine learning pipeline that can effectively prioritize non-coding variants for downstream experimental validation and clinical follow-up.

The stakeholders for this work include rare disease research teams seeking to accelerate variant interpretation, clinical genomics analysts requiring computational decision-support tools, and computational genomics researchers developing scalable variant annotation workflows. The work is positioned within the broader precision medicine context, where accurate computational variant classification can reduce the burden of manual expert review and allow limited experimental resources to be focused on the most promising research directions.

From a societal and ethical perspective, this project operates with publicly available, de-identified genetic variant data (Landrum et al., 2018). The project treats variant data responsibly and explicitly notes that model predictions are not intended for clinical diagnosis without independent laboratory confirmation and expert medical interpretation. The project will address class imbalance and label uncertainty explicitly by excluding ambiguous records (e.g., variants of uncertain significance, records with conflicting clinical interpretations) and by reporting performance metrics that remain valid under class imbalance.

This project integrates applied data science—encompassing machine learning, rigorous statistical evaluation, and reproducible model deployment—with computational genomics and healthcare workflows, demonstrating how variant prioritization connects practical machine learning methods to clinically relevant research applications.

---

## 3. Data Acquisition & Viability

The primary data source for this project is the ClinVar repository (https://www.ncbi.nlm.nih.gov/clinvar/), a public database maintained by the National Center for Biotechnology Information (NCBI) and freely accessible to researchers worldwide. ClinVar aggregates clinical interpretations of genetic variants submitted by laboratories, clinicians, and researchers; for each variant, the repository provides chromosomal coordinates, reference and alternate alleles, genome assembly identifiers, clinical significance classifications (such as Pathogenic, Likely Pathogenic, Benign, Likely Benign, and Uncertain Significance), and supporting literature citations. A recent ClinVar release has been successfully downloaded and validated, confirming data accessibility and compatibility with the project's parsing pipeline (verified January 13, 2026).

Clinical significance labels will be strictly defined to maximize confidence in the training signal. Variants labeled as Pathogenic or Likely Pathogenic will be assigned to the pathogenic class, while variants labeled as Benign or Likely Benign will be assigned to the benign class. Variants classified as Uncertain Significance or those with conflicting clinical interpretations across submitters will be excluded from model training and evaluation to reduce label noise and maintain high-confidence positive and negative examples.

Non-coding variants will be identified using computational consequence annotation via the Ensembl Variant Effect Predictor (VEP; McLaren et al., 2016). This tool predicts the functional consequence of each variant by comparing variant positions to known gene annotations; non-coding consequences include variants within introns, untranslated regions (UTRs), upstream and downstream intergenic regions, and other non-exonic genomic elements. This computational filtering allows scalable and reproducible isolation of non-coding variants from the full ClinVar dataset.

For the primary non-coding variant analysis, fixed-length DNA sequence windows will be extracted centered on each variant's genomic position from public reference genome sequences. These sequence windows will then be embedded using a pretrained DNA foundation model in the style of DNABERT (Ji et al., 2021), producing fixed-dimensional feature vectors suitable for machine learning. The project plans to explore multiple window sizes (101 base pairs, 201 base pairs, 501 base pairs) during exploratory data analysis to determine which encoding best captures variant-specific signal.

Data curation and versioning will follow software engineering best practices. The curated labeled dataset will be stored as versioned Parquet files that explicitly record the ClinVar release date, consequence annotation parameters, window size, and label filtering criteria applied during construction. All dataset processing steps will be deterministic and fully scripted, ensuring that researchers can reconstruct the labeled dataset deterministically from the original ClinVar public release. Embedding features will be cached to disk in standardized formats to enable reproducible model training without requiring re-computation of expensive embedding operations.

ClinVar is public, de-identified, and accessible without special data-use agreements or institutional review. The project will be executed in accordance with university research and data-handling best practices, treating genetic variant information responsibly and ensuring that no participant health information is collected or retained. The computational workflow will be thoroughly documented and sufficient implementation detail will be provided that other researchers can reproduce the analysis using only publicly available data sources. The project is structured as a research proof-of-concept and explicitly disclaims clinical utility; model predictions are intended for research-driven variant prioritization rather than clinical diagnostic use.

---

## 4. Technical Execution & Complexity

The end-to-end pipeline comprises seven major computational phases. First, ClinVar releases are downloaded and parsed, variant representations are normalized, and clinical significance labels are applied and filtered. Second, genomic consequences are computed using Ensembl VEP and the dataset is subsetted to non-coding variants. Third, fixed-length DNA sequence windows are extracted from the reference genome centered at each variant position. Fourth, pretrained DNA embeddings are generated for each sequence window using a DNABERT-style foundation model. Fifth, train, validation, and test splits are created using chromosome-based stratification to prevent data leakage (ensuring that sequences from the same genomic region do not appear in both training and test sets). Sixth, multiple classifier models are trained on the embedding features and compared using rigorous statistical tests. Seventh, the best-performing model is calibrated, validated, and deployed as both a web application and command-line tool.

The project will implement three complementary classifier architectures, all trained on the same embedding features. Logistic Regression will serve as an interpretable, well-behaved baseline model. Random Forest will provide a nonlinear, ensemble-based alternative that can capture complex patterns in the embedding space. Optionally, a shallow Multi-Layer Perceptron will be implemented as a neural network baseline to assess whether additional model complexity provides incremental improvements in predictive performance.

This project addresses several technically sophisticated challenges at the Master's level. First, it implements transfer learning by applying pretrained DNA foundation models (DNABERT-style embeddings) to a genomic variant classification task, requiring both understanding of language model representations and their effective application to biological sequence data. Second, the project employs leakage-aware experimental design using chromosome-based stratification to prevent overoptimistic performance estimates that would arise if similar genomic sequences appeared in both training and test sets. Third, the project implements rigorous statistical testing (DeLong tests for AUROC comparison, paired bootstrap and permutation tests for AUPRC comparison) to distinguish genuine performance differences from random variation. Fourth, the project delivers a complete machine learning system suitable for production deployment, including model serialization, reproducible computation environments (via conda and optional Docker containerization), and user-facing interfaces (interactive web application and command-line tool).

Reproducibility is central to the project's design. All random seeds are fixed at every stage (embedding computation, train/test splitting, model training) to enable deterministic replication of results. Hyperparameters and dataset filtering criteria are specified in tracked configuration files, allowing different analysis variants to be reproduced by simply changing configuration parameters. Train, validation, and test splits are explicitly saved to disk so that identical data partitions can be used for future analyses or by other researchers. The computational environment will be captured via conda environment files, documenting exact package versions and dependencies. The codebase will follow professional Python standards, including type annotations, modular organization into separate modules for data loading, feature engineering, model training, evaluation, and deployment, and formatting/linting via tools such as Black and Ruff. Unit tests will be implemented for critical pipeline steps to catch regressions and ensure long-term maintainability.

---

## 5. Deployment Plan: "The App"

The final deliverable includes a user-facing application that scores genetic variants and returns calibrated pathogenicity probabilities. The application will be implemented as a Streamlit web application, accepting as input either a single variant (specified by chromosome, genomic position, reference allele, alternate allele, and genome assembly) or a small CSV file containing multiple variants. The application returns for each variant a calibrated probability of pathogenicity and a predicted class label (pathogenic or benign) based on a documented decision threshold.

Additionally, a command-line interface will be provided to enable batch scoring of larger variant datasets provided as CSV or VCF-derived tables. This command-line tool allows seamless integration into automated variant interpretation pipelines and bioinformatics workflows used by computational research laboratories.

The complete set of end-to-end project deliverables includes: (1) a reproducible pipeline with associated configuration files that can rebuild the dataset and models from the original public ClinVar release; (2) trained model artifacts (serialized scikit-learn or PyTorch models) accompanied by an evaluation report documenting performance metrics, statistical tests, and detailed error analysis; (3) a Streamlit web application for interactive variant scoring; and (4) a command-line tool for batch processing of variant sets.

---

## 6. Statistical Analysis & Evaluation

Classification performance will be evaluated using two primary metrics selected for their appropriateness to imbalanced binary classification problems. Area Under the Receiver Operating Characteristic Curve (AUROC) and Area Under the Precision-Recall Curve (AUPRC) are both threshold-independent metrics that remain valid across different class imbalance ratios. Secondary metrics will include precision, recall, F1 score, and balanced accuracy to provide a comprehensive view of model behavior on both the majority and minority classes.

The experimental design incorporates leakage-aware splitting to avoid artificially inflated performance estimates. Specifically, the dataset will be divided into training, validation, and test subsets using chromosome-based stratification, where entire chromosomes (or contiguous chromosome groups) are assigned to test, while other chromosomes are reserved for training and validation. This strategy reduces the risk of data leakage wherein very similar genomic sequences from the same chromosomal region appear in both training and test sets, which would inflate apparent performance. As a sensitivity analysis, the chromosome assignment strategy will be varied across multiple random seeds to test whether performance estimates remain stable across different chromosome partitions.

The project will train and compare three complementary models—Logistic Regression, Random Forest, and optionally a shallow Multi-Layer Perceptron—all using the same embedding feature sets. Performance comparisons will employ rigorous statistical tests appropriate for paired predictions on the same test set. The DeLong test will be used to compare AUROC values between models, while paired bootstrap and permutation tests will compare AUPRC values. Bootstrapped 95% confidence intervals will be constructed for AUROC and AUPRC on the held-out test set, providing not merely point estimates but ranges of plausible performance values.

Because the non-coding variant dataset is expected to exhibit class imbalance (more benign than pathogenic variants in ClinVar), the project will employ class weighting during model training to penalize misclassification of the minority (pathogenic) class more heavily. Decision thresholds will be tuned on the validation set to optimize a desired trade-off between sensitivity and specificity. Performance will be reported as precision-recall curves to clearly visualize the trade-off between precision and recall across different operating points.

The final trained model will be calibrated using the validation set (via Platt scaling or isotonic regression) to ensure that predicted probabilities reflect true conditional class probabilities. Calibration will be assessed using calibration curves and the Brier score, enabling downstream users to interpret predicted probabilities as genuine probability estimates rather than arbitrary model scores.

Supporting interpretability analyses will provide insights into model predictions and feature importance. For tree-based models, feature importance scores will identify which embedding dimensions and sequence features most strongly influence predictions. For all models, calibrated probability outputs will serve as risk scores for downstream decision-making. Lightweight attribution analysis will be performed for a small set of representative variants, showing which regions of the sequence window most influence model predictions. If time permits, SHAP (SHapley Additive exPlanations) analysis will provide model-agnostic, local and global explanations of model behavior within the embedding feature space.

If, during exploratory analysis, the positive class (pathogenic non-coding variants) is discovered to be too small after strict filtering to support reliable model training, the filtering criteria will be relaxed iteratively: for example, expanding the label set to include Likely Pathogenic variants, or slightly relaxing the non-coding consequence criteria, while maintaining high confidence by continuing to exclude ambiguous records (VUS, conflicting interpretations).

---

## 7. Project Timeline & Milestones

The project is organized into seven phases across fifteen weeks.

During weeks 1–4, the focus is on data acquisition and preparation. Activities include downloading and parsing ClinVar releases, defining and applying label filtering rules, performing consequence annotation via Ensembl VEP, conducting exploratory data analysis, finalizing window size choices through ablation studies, and designing the chromosome-based split strategy.

Weeks 5–8 focus on feature engineering and baseline model development. Embedding vectors will be generated for all variants. Logistic Regression and Random Forest classifiers will be trained on the embedding features, and initial performance estimates using AUROC and AUPRC will be computed. Iterative analysis of class imbalance effects will inform threshold tuning and the selection of decision operating points.

Weeks 9–12 are dedicated to model refinement and rigorous statistical evaluation. If time permits, a shallow Multi-Layer Perceptron will be implemented as an optional extension. Final model evaluation will include bootstrapped confidence intervals, paired statistical tests comparing model performance, and detailed error analysis to understand which types of variants are misclassified and why.

Weeks 13–15 focus on deployment, documentation, and presentation. The Streamlit web application and command-line interface will be implemented. Project documentation, inline code comments, and the final capstone report will be completed. A project presentation and interactive demo will be prepared for peer and instructor review.

This is an individual capstone project. Feedback will be iteratively solicited from the instructor and advisor throughout the semester, and a final project presentation will be delivered to peers for collaborative review.

---

## 8. New Knowledge Acquisition

This project offers hands-on experience with a number of modern computational genomics and machine learning methods. It first shows how pretrained DNA language models (DNABERT-style embeddings) may be used practically for feature extraction in a genomic prediction job, relating fundamental transfer learning ideas to domain-specific bioinformatics problems. Second, the initiative promotes fluency with common genomic data representations and workflows by developing deep literacy in biological data sources and annotation tools (ClinVar, Ensembl VEP). Lastly, the project exemplifies professional software engineering techniques (typed code, reproducible environments, modular architecture, unit testing) applied to a machine learning context, preparing the student for collaborative research environments and industry-scale data science roles.

---

## References

Ji, Y., Zhou, Z., Liu, H., and Davuluri, R. V. (2021). "DNABERT: pre-trained Bidirectional Encoder Representations from Transformers model for DNA-language in genome." *Bioinformatics*, 37(15), 2112–2120.

Landrum, M. J., Lee, J. M., Benson, M., Brown, G. R., Chao, C., Chitipiralla, S., and others (2018). "ClinVar: improving access to variant interpretations and supporting evidence." *Nucleic Acids Research*, 46(D1), D1062–D1067.

McLaren, W., Gil, L., Hunt, S. E., Riat, H. S., Ritchie, G. R., Thormann, A., and others (2016). "The Ensembl Variant Effect Predictor." *Genome Biology*, 17(1), 122.

---

## Resources

**Data sources:**
- ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/
- Ensembl VEP: https://www.ensembl.org/info/docs/tools/vep/

**Tools and libraries:**
- scikit-learn: https://scikit-learn.org/ (machine learning models and evaluation)
- Streamlit: https://streamlit.io/ (web application framework)
- PyTorch: https://pytorch.org/ (neural network implementation, optional)
