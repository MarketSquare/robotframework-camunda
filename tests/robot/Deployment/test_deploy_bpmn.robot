*** Settings ***
Library    CamundaLibrary   ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test deployment of models
    ${response}    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
    Should Not Be Empty     ${response}
    log    ${response}

Test deployment of models and forms
    # WHEN
    ${response}    deploy    ${CURDIR}/../../form/embeddedSampleForm.html    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

    # THEN
    Should Not Be Empty     ${response}

    # AND
    ${deployment}    get deployments    id=${response}[id]
    Should Not Be Empty    ${deployment}    No deployment found for id ${response}[id]

Test error when deploying to incorrect url
    # GIVEN
    set camunda url    http://localhost:6666

    # WHEN
    ${pass_message}    ${error}    Run Keyword and ignore error    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

    # THEN
    Should Be Equal    FAIL    ${pass_message}
    Should contain    ${error}    ConnectionError
    [Teardown]    set camunda url     ${CAMUNDA_HOST}