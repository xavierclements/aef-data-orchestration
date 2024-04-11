WORKFLOW=1_workflow_single_thread_1_level_composer

python3 orchestration_generator.py \
../workflows-definition/$WORKFLOW.json \
../workflows-definition/platform-parameters-dev.json \
result-$WORKFLOW.py \111111111111 \
False