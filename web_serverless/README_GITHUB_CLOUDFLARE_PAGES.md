# ALTAR-NASA • Flame in Freefall (v6.3) — Serverless Static Web Bundle

This folder (`web_serverless/`) contains the zero-backend static browser edition deployed on GitHub Pages, bundled with `sample_data/ALTAR_NASA_Comprehensive_Experiment_Dataset.csv` and the 36-investigation NASA PSI archive snapshot.

## Key Capabilities
1. **In-Browser Physics & 3D Twin:** Runs directly in the browser with no background server or open ports — including the 3D WebGL Combustion Chamber, 3D Orion MCP 5-compartment spacecraft digital twin, phase-specific `d²` / `de Ris` / `Burke-Schumann` laws, thermophysical custom material analog matching, opposed/concurrent airflow analysis, `0.38G Mars` and `0.16G Moon` flammability boundary curves (`±1σ`), ISS `0G` benchmark calibration (`R²` / `RMSE`), `NASA JSC-20584` crew survival clock, and dynamic NASA PSI investigation ranking.
2. **Local Data Privacy:** Contains zero embedded API keys; flame photographs, videos, or tabular files you drop into the interface are processed strictly inside browser memory without leaving your device.

## Publishing on GitHub Pages
1. Copy the contents of `web_serverless/` (`index.html`, `css/`, `js/`, `nasa_flame.ico`, `sample_data/`, `.nojekyll`) to the root of the `gh-pages` branch.
2. Under repository **Settings -> Pages -> Deploy from a branch (`gh-pages` / `/root`)**, save the branch configuration.
3. Live web URL: `https://faruk042.github.io/Nasa-English/`
