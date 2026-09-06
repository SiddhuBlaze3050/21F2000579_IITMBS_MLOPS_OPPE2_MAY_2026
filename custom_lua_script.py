import json
import pandas as pd

df = pd.read_csv("data/generated_100.csv")
records = df.to_dict(orient="records")

lua_content = """wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

local payloads = {
"""

for record in records:
    lua_content += f"  {json.dumps(json.dumps(record))},\n"

lua_content += """}

local counter = 0

request = function()
    counter = (counter % #payloads) + 1
    return wrk.format(nil, nil, nil, payloads[counter])
end
"""

with open("post_data.lua", "w") as f:
    f.write(lua_content)

print("Generated post_data.lua successfully.")