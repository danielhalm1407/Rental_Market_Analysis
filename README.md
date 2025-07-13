# Rental Market Demand and Cost Inference

This project aims to estimate the impact of key demand and supply factors on rental prices. So far, the analysis focuses in the London Market on rental unit characteristics, particularly on commute times (as opposed to commute distances) above and beyond conventional characteristics such as number of bedrooms and floor space (for which I normalise) and number of bathrooms and description keywords (e.g., luxury, spacious, rennovated). 

Data on rental prices and a majority of unit characteristics has been extracted from Rightmove (including location), whereas commute times were calculated by inputting the co-ordinates of each property into the Travel Time REST API.

The next stage of analysis is to apply statistical machine learning methods to the already gathered data (more than a simple linear regression) to best predict listed prices. 

Nonetheless, the ultimate aim is to use an industrial economic model to estimate the sensitivity of demand and supply to their respective shifters, both in terms of quantities as a function of price and shifters, as well as prices (inverse supply and demand) as a function of quantity and shifters. A key challenge is that property/unit data has limited time variation, yet must be matched to supply shifters, which have greater variation across time but have limited cross-sectional variation.

Given the growing unaffordability of housing across the rich world [(Romei & Fleming, The Financial Times, 2024)](https://www.ft.com/content/f206f6f1-1536-4b29-ad8d-2421fadfc64b), it is increasingly important to understand the dynamics of the housing market, particularly the rental market, into which an ever larger number of households are constrained.

I aim to find evidence that transit-oriented-development (TOD), though a force for raising the level of demand in a city by reducing commute times and hence making housing more attractive at all prices, may, under certain conditions (positive supply shocks), lower overall prices if the level of supply at all prices increases by a greater degree. This is because such development makes it possible (despite not being sufficient on its own) for there to be more housing in time proximity to the places where households wish to live and work.

## Demand Side

I build on previous literature that models the rental market as a differentiated product market (where the utility derived from renting a unit is a function of price, trends (time level shocks), and characteristics at the product, firm, and household level), similarly to a recent paper on the effects of algorithmic pricing on multifamily rentals [(Calder-Wang & Kim, 2024)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4403058). 

Whereas this paper focussed on more robust estimation procedures and more generalised modelling frameworks, I aim to focus on augmenting a similar yet simpler theoretical model and estimation technique with data on additional product characteristics, primarily commute time to employment centres. In order to do this, I aim to input location data from right move into the Travel Time API, which returns an estimate of travel time under different modes for each unit.

## Supply Side

In a similar spirit to the aforementioned paper, I aim to estimate the supply side of this model using a theoretical model for supply prices as a markup (under a specified market structure/form of conduct) above marginal costs. Here, a policy of reducing planning requirements may, by reducing uncertainty and administrative costs, reduce both marginal costs and, through reducing barriers to entry, increase the actual level and/or threat of competition, reduce markups, therefore lowering supply prices. I aim to estimate to what extent the former mechanism is the case.

## DISCLAIMER:

I have used Open AI's Chat GPT 3.5 and GPT4-o, as well as github co-pilot to assist with syntax and structuring across various coding aspects of this project.

Please refer to the saved chat log [here](https://chatgpt.com/share/685ebd07-69c8-800f-8488-2aee5b99e745). 

###  🗂️ Directory Structure
```plaintext
.
├── README.md
├── credentials.json (used to acess data)
├── data
│   └── rental.db (Database for data storage)
├── docs (webpages)
│   ├── subpages_1
│       ├── Images and figures placed on the overview webpage.
│   └── index.html (Project overview web page)
├── notebooks
│   ├── NB01_QS_Uni_Rankings_Hidden_API_Test.ipynb (Testing out a Hidden API as Practice)
│   ├── NB01_Extract_Data.ipynb
│   └── NB03_Analyse_Data.ipynb
├── src
│   ├── rental_utils (custom Python package)
│       └── sql_queries.py (Functions needed for database interaction)
│   └── scripts (runnable Python scripts)
│       └── sql_in.py (saves the excel files into a database as tables)
└── requirements.txt (set of packages to install onto the virtual environment)

```
### 📚 How to get this to work

If you want to replicate the analysis in this notebook, you will need to:

1. Clone this repository to your computer
    ```bash
    git clone git@github.com:danielhalm1407/Rental_Market_Demand_and_Cost_Inference.git
    ```
2. Add it to your VS Code workspace
3. Set up your conda environment on conda's 3.11 version of python:

    ```bash
    conda create -n venv-rental python=3.11 ipython
    conda activate venv-rental
    ```
4. Make sure `pip` is installed inside that environment:

    ```bash
    conda install pip
    ```

5. Now use that pip to install the packages:

    ```bash
    python -m pip install -r requirements.txt
    ```

6. Run the scripts

    If you want to run these separately,
    type 
    ```bash
    cd /src/scripts
    ```
    and then 
    ```bash
    python nb03.py
    ```

    If you want to run these all in one go
    type 
    ```bash
    bash run_all.sh
    ```
7. Alternatively, Run the notebooks

    Run all the notebooks in order, selecting the venv-rental kernel
