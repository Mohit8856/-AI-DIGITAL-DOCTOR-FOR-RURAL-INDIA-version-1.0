from pathlib import Path

folder = Path(__file__).parent

input_file = folder / "Healthcare(1).csv"
output_file = folder / "Healthcare_clean.csv"

with open(input_file, "r", encoding="utf-8") as f, \
     open(output_file, "w", encoding="utf-8") as out:

    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split(",")

        age = parts[0].strip()
        gender = parts[1].strip()
        disease = parts[-1].strip()

        symptoms = " ".join(
            part.strip() for part in parts[2:-1]
        )

        out.write(f"{age},{gender},{symptoms},{disease}\n")

print("Done!")
print(f"Output file: {output_file}")