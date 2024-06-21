filename = f'tgw_output-{account_name}.json'
    output_path = Path('output') / account_name
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to write JSON file: {e}")
