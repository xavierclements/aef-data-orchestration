WORKFLOW=etl_example_1

python3 workflows_generator.py \
../workflows-definition/$WORKFLOW.json \
../workflows-definition/platform-parameters-dev.json \
result-$WORKFLOW.json \111111111111 \
False