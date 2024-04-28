WORKFLOW=workflow_single_thread_1_level_composer

python3 orchestration_generator.py \
../workflow-definitions/$WORKFLOW.json \
../workflow-definitions/platform-parameters-dev.json \
result-$WORKFLOW.py \
False