# GameBreaker CLV dashboard (Streamlit)

Shows every SETTLED pick (a Pinnacle closing price exists) with the price taken, the closing price, CLV, and the time it was logged.
The logged time comes from the git commit history of pinnacle_clv_drift.csv, so it is a timestamp set before kick-off.
Unsettled picks are never exported, so no live pre-kick-off pick can appear.

## Refresh the data
    python build_data.py        # reads C:\Users\RODNE\pinnacle_clv_drift.csv and the git history, writes data/bets.csv

## Run locally (only your own machine can reach it)
    python -m streamlit run app.py --server.address localhost --server.port 8511

## Share it (optional)
Streamlit Community Cloud deploys from a GitHub repo. Put this folder in its own repo, point Cloud at app.py.
Only data/bets.csv (settled picks) goes in the repo. Never add the raw tracking files or any key.
Decide first whether the full settled history should be public. The page is built so it can be.

## Notes
- Percent signs in the pin_clv column must be stripped before averaging (build_data.py does this).
- "Logged at" finds the first commit where the match string appeared. If the same fixture text ever repeats in a season, check that row by hand.
- CLV is not profit. The page says so. It also shows a rough 95% range for the average (assumes independent picks).
