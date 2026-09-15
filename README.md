# Clean-room incident gateway

This directory contains only synthetic data contracts and a dependency-free
Python core. It never connects to a production system.

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

`schema.sql` is for a disposable local PostgreSQL database. The intended role
has `SELECT` only on `assistant_task_failures`, not on the raw table.
