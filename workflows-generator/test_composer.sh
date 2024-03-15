WORKFLOW=2_workflow_threaded_1_level

python3 composer_dag_generator.py \
../workflows-definition/$WORKFLOW.json \
../workflows-definition/platform-parameters-dev.json \
result-$WORKFLOW.py \111111111111 \
False