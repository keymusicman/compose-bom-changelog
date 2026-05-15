#!/usr/bin/env bash
set -e

cp data/bom-data.json site/static/data/bom-data.json
cd site && npm run dev
