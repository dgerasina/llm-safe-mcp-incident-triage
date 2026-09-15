# Processed result

The clean-room contract passed all checks:

- only the requested run can be returned;
- invalid identifiers and unbounded dependency depth are rejected;
- raw logs and fields outside the response contract are not exposed;
- error excerpts are limited to 500 characters;
- the database role reads the safe view but cannot read the raw table or write;
- the MCP Python SDK registers the documented tool and input schema.
