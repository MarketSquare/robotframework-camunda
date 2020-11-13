*** Settings ***
Library    CamundaLibrary.ExternalTask

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Never write recent process instance id when no workitem is fetched
    [Setup]    set camunda url    ${CAMUNDA_HOST}
    # GIVEN
    ${not_existing_topic}    Set Variable    asdfawesadas
    ${work_items}    fetch and lock workloads    topic=${not_existing_topic}

    # EXPECT
    Should be Empty    ${work_items}    Did not expect to receive work items for not existing topic:\t${not_existing_topic}

    # WHEN
    ${recent_task}    Get recent process instance

    # THEN
    Should Be Empty    ${recent_task}    Should not have stored a recent task for none existing topic, but registered recent task id:\t${recent_task}