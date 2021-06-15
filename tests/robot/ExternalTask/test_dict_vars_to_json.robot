*** Settings ***
Library     CamundaLibrary    ${CAMUNDA_HOST}
Library     Collections
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element


*** Test Cases ***
Dictionary variable remains dictionary
    # GIVEN
    ${variables}    Process with dictionary variable

    # WHEN
    ${return_variables}    Workload is fetched

    #THEN
    Should Not Be Empty    ${return_variables}    Fetching failed. Expected workload at topic '${EXISTING_TOPIC}'

    #AND
    Should Be Equal    ${return_variables}[map][a]    ${variables}[map][a]    Dictionary value returned not as expected
    Should Be Equal    ${return_variables}[map][b]    ${variables}[map][b]    Dictionary value returned not as expected


Dictionary variable is of type JSON in camunda
    #GIVEN
    ${process_instance}     Process with dictionary variable is started

    ${variable_instance}    Get Process Instance Variable
    ...    process_instance_id=${process_instance}[id]
    ...    variable_name=map

    Should Be Equal    Json    ${variable_instance.type}    Datatype for dictionary was supposed to be Json

List variable remains list
    # GIVEN
    ${variables}    Process with list variable

    # WHEN
    ${return_variables}    Workload is fetched

    #THEN
    Should Not Be Empty    ${return_variables}    Fetching failed. Expected workload at topic '${EXISTING_TOPIC}'

    #AND
    Should Be Equal    ${return_variables}[map][0]    ${variables}[map][0]    Dictionary value returned not as expected
    Should Be Equal    ${return_variables}[map][1]    ${variables}[map][1]    Dictionary value returned not as expected


List variable is of type JSON in camunda
    #GIVEN
    ${process_instance}     Process with list variable is started

    ${variable_instance}    Get Process Instance Variable
    ...    process_instance_id=${process_instance}[id]
    ...    variable_name=map

    Should Be Equal    Json    ${variable_instance.type}    Datatype for dictionary was supposed to be Json


*** Keywords ***
Process with dictionary variable
    ${my_dict}    Create Dictionary    a=1    b=2
    ${variables}    Create Dictionary    map=${my_dict}
    ${process_instance}    start process    ${PROCESS_DEFINITION_KEY}    variables=${variables}
    [Return]    ${variables}

Process with list variable
    ${my_dict}    Create list    1    2
    ${variables}    Create Dictionary    map=${my_dict}
    ${process_instance}    start process    ${PROCESS_DEFINITION_KEY}    variables=${variables}
    [Return]    ${variables}

Workload is fetched
    ${return_variables}    fetch workload    ${EXISTING_TOPIC}
    [Return]    ${return_variables}

Process with dictionary variable is started
    ${my_dict}    Create Dictionary    a=1    b=2
    ${variables}    Create Dictionary    map=${my_dict}
    ${process_instance}    start process    ${PROCESS_DEFINITION_KEY}    variables=${variables}
    [Return]    ${process_instance}

Process with list variable is started
    ${my_dict}    Create Dictionary    a=1    b=2
    ${variables}    Create Dictionary    map=${my_dict}
    ${process_instance}    start process    ${PROCESS_DEFINITION_KEY}    variables=${variables}
    [Return]    ${process_instance}
