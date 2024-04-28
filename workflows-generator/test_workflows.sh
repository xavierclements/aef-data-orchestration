WORKFLOW=workflow_single_thread_1_level_dataproc

python3 orchestration_generator.py \
../workflow-definitions/$WORKFLOW.json \
../workflow-definitions/platform-parameters-dev.json \
result-$WORKFLOW.yaml \111111111111 \
False
