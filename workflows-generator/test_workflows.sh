WORKFLOW=7_workflow_single_thread_1_level_dataproc

python3 orchestration_generator.py \
../workflows-definition/$WORKFLOW.json \
../workflows-definition/platform-parameters-dev.json \
result-$WORKFLOW.yaml \111111111111 \
False
