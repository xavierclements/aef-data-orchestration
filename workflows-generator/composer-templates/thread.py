           # Start thread group definition
           with TaskGroup(group_id="Level_{LEVEL_ID}_Thread_{THREAD_ID}") as tg_level_{LEVEL_ID}_Thread_{THREAD_ID}:
<<THREAD_STEPS>>

                    <<THREAD_STEPS_DEPENDENCIES>>
           # End thread group definition