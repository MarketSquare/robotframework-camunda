*** Settings ***
Library    ../../../Camunda/Deployment/Deployment.py    ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test deployment of models
    ${response}    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
    Should Not Be Empty     ${response}
    log    ${response}