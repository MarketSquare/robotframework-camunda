*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test 'Notify failure' for existing topic
    # GIVEN
    Start process    ${PROCESS_DEFINITION_KEY}
    ${variables}    Create Dictionary    text=Manna Manna

    # AND
    fetch workload   topic=${existing_topic}
    ${process_instance}    Get fetch response
    log    ${process_instance}

    # EXPECT
    Should Not be Empty    ${process_instance}    Failure while setting up test case. No process instance available to send failure for.

    # WHEN
    notify failure

    # THEN
    ${workload}    Fetch Workload    topic=${existing_topic}
    Should Be Empty    ${workload}    Notifying Failure failed. Process instance should not be available anymore at service task.

    # AND
    ${process_instance_after_failure}    Get process instances    process_instance_ids=${process_instance}[process_instance_id]
    log    ${process_instance_after_failure}
    Should Not Be Empty    ${process_instance_after_failure}    Notifying Failure failed. Process instance is instance but should be an incident.

    ${incident}    Get incidents    process_instance_id=${process_instance}[process_instance_id]
    log    ${incident}
    Should Not be Empty    ${incident}