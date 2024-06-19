name: Generate Wiki

on:
  push:
    branches:
      - main

jobs:
  generate-wiki:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pandas
          pip install markdown

      - name: Run Script to Generate Markdown
        run: |
          python your_script.py  # Replace with the path to your script

      - name: Commit and Push Wiki Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          cp output/tgw_output-*.md ../wiki/  # Adjust the source and destination paths as necessary
          cd ../wiki
          git add .
          git commit -m "Update Wiki with latest TGW output"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
