*** Settings ***
Library    Camunda.Deployment    ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test deployment of models
    ${response}    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
    Should Not Be Empty     ${response}
    log    ${response}

Test error when deploying to incorrect url
    # GIVEN
    set camunda url    http://localhost:6666

    # WHEN
    ${pass_message}    ${error}    Run Keyword and ignore error    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

    # THEN
    Should Be Equal    FAIL    ${pass_message}
    Should contain    ${error}    ConnectionError