*** Settings ***
Library    CamundaLibrary
Test Setup    Set Camunda Configuration    ${configuration}

*** Test Cases ***
Test deployment of models
    ${response}    deploy    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
    Should Not Be Empty     ${response}

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
    ${pass_message}    ${error}    Run Keyword and ignore error    deploy    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

    # THEN
    Should Be Equal    FAIL    ${pass_message}
    Should contain    ${error}    ConnectionError
    [Teardown]    set camunda url     ${configuration}[host]