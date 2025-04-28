# #!/bin/bash

curl -X POST http://localhost:8081/compatibility/subjects/invoice-topic-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @PosInvoice.json
