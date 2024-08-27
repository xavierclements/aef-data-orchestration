    # Start level group definition
    with TaskGroup(group_id="Level_{LEVEL_ID}") as tg_Level_{LEVEL_ID}:
        <<THREADS>>

           <<THREAD_DEPENDENCIES>>
    # End level group definition
