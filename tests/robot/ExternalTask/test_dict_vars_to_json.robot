*** Settings ***
Library     CamundaLibrary    ${CAMUNDA_HOST}
Library     Collections
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element


*** Tasks ***
Dict remains a dict
    #GIVEN
    ${my_dict}    Create Dictionary    a=1    b=2
    ${variables}    Create Dictionary    map=${my_dict}
    start process    ${PROCESS_DEFINITION_KEY}    variables=${variables}
    #WHEN
    ${return_variables}    fetch workload    ${EXISTING_TOPIC}
    #THEN
    Should Not Be Empty    ${return_variables}    Fetching failed. Expected workload at topic '${EXISTING_TOPIC}'
    #AND
    Should Be Equal    ${return_variables}[map][a]    ${variables}[map][a]
    Should Be Equal    ${return_variables}[map][b]    ${variables}[map][b]