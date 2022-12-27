import time

from sagemaker.session import _logs_init, _get_initial_job_state, LogState, _rule_statuses_changed, _flush_log_streams
from sagemaker.utils import secondary_training_status_message, secondary_training_status_changed


def logs_for_job(  # noqa: C901 - suppress complexity warning for this method
        job_name, sagemaker_session,  wait=False, poll=10, log_type="All", ws=None, model_name=None
):
    """Display logs for a given training job, optionally tailing them until job is complete.

    If the output is a tty or a Jupyter cell, it will be color-coded
    based on which instance the log entry is from.

    Args:
        job_name (str): Name of the training job to display the logs for.
        wait (bool): Whether to keep looking for new log entries until the job completes
            (default: False).
        poll (int): The interval in seconds between polling for new log entries and job
            completion (default: 5).

    Raises:
        exceptions.CapacityError: If the training job fails with CapacityError.
        exceptions.UnexpectedStatusException: If waiting and the training job fails.
    """

    description = sagemaker_session.sagemaker_client.describe_training_job(TrainingJobName=job_name)
    msg = secondary_training_status_message(description, None)
    print(msg, end="")
    if ws:
        ws.emit(model_name, msg.split('-')[-1].strip())


    instance_count, stream_names, positions, client, log_group, dot, color_wrap = _logs_init(
        sagemaker_session, description, job="Training"
    )

    state = _get_initial_job_state(description, "TrainingJobStatus", wait)

    # The loop below implements a state machine that alternates between checking the job status
    # and reading whatever is available in the logs at this point. Note, that if we were
    # called with wait == False, we never check the job status.
    #
    # If wait == TRUE and job is not completed, the initial state is TAILING
    # If wait == FALSE, the initial state is COMPLETE (doesn't matter if the job really is
    # complete).
    #
    # The state table:
    #
    # STATE               ACTIONS                        CONDITION             NEW STATE
    # ----------------    ----------------               -----------------     ----------------
    # TAILING             Read logs, Pause, Get status   Job complete          JOB_COMPLETE
    #                                                    Else                  TAILING
    # JOB_COMPLETE        Read logs, Pause               Any                   COMPLETE
    # COMPLETE            Read logs, Exit                                      N/A
    #
    # Notes:
    # - The JOB_COMPLETE state forces us to do an extra pause and read any items that got to
    #   Cloudwatch after the job was marked complete.
    last_describe_job_call = time.time()
    last_description = description
    last_debug_rule_statuses = None
    last_profiler_rule_statuses = None

    while True:
        _flush_log_streams(
            stream_names,
            instance_count,
            client,
            log_group,
            job_name,
            positions,
            dot,
            color_wrap,
        )
        if state == LogState.COMPLETE:
            break

        time.sleep(poll)

        if state == LogState.JOB_COMPLETE:
            state = LogState.COMPLETE
        elif time.time() - last_describe_job_call >= 30:
            description = sagemaker_session.sagemaker_client.describe_training_job(TrainingJobName=job_name)
            last_describe_job_call = time.time()

            if secondary_training_status_changed(description, last_description):
                print()
                msg = secondary_training_status_message(description, last_description)
                print(msg, end='')
                if ws:
                    ws.emit(model_name, msg.split('-')[-1].strip())
                last_description = description

            status = description["TrainingJobStatus"]

            if status in ("Completed", "Failed", "Stopped"):
                print()
                state = LogState.JOB_COMPLETE

            # Print prettified logs related to the status of SageMaker Debugger rules.
            debug_rule_statuses = description.get("DebugRuleEvaluationStatuses", {})
            if (
                    debug_rule_statuses
                    and _rule_statuses_changed(debug_rule_statuses, last_debug_rule_statuses)
                    and (log_type in {"All", "Rules"})
            ):
                for status in debug_rule_statuses:
                    rule_log = (
                        f"{status['RuleConfigurationName']}: {status['RuleEvaluationStatus']}"
                    )
                    print(rule_log)
                    if ws:
                        ws.emit(model_name, rule_log)

                last_debug_rule_statuses = debug_rule_statuses

            # Print prettified logs related to the status of SageMaker Profiler rules.
            profiler_rule_statuses = description.get("ProfilerRuleEvaluationStatuses", {})
            if (
                    profiler_rule_statuses
                    and _rule_statuses_changed(profiler_rule_statuses, last_profiler_rule_statuses)
                    and (log_type in {"All", "Rules"})
            ):
                for status in profiler_rule_statuses:
                    rule_log = (
                        f"{status['RuleConfigurationName']}: {status['RuleEvaluationStatus']}"
                    )
                    print(rule_log)
                    if ws:
                        ws.emit(model_name, rule_log)

                last_profiler_rule_statuses = profiler_rule_statuses

    if wait:
        sagemaker_session._check_job_status(job_name, description, "TrainingJobStatus")
        if dot:
            print()
        # Customers are not billed for hardware provisioning, so billable time is less than
        # total time
        training_time = description.get("TrainingTimeInSeconds")
        billable_time = description.get("BillableTimeInSeconds")
        msg = ''
        if training_time is not None:
            msg += f"Training seconds: {training_time * instance_count}\n"
        if billable_time is not None:
            msg += f"Billable seconds: {billable_time * instance_count}\n"
            if description.get("EnableManagedSpotTraining"):
                saving = (1 - float(billable_time) / training_time) * 100
                msg += "Managed Spot Training savings: {:.1f}%\n".format(saving)
        print(msg)
        if ws and msg:
            ws.emit(model_name, msg)
