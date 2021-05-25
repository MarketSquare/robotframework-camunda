*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Suite Teardown    Clean Up Process Instance


*** Variables ***
${CAMUNDA_HOST}              http://localhost:8080
${PROCESS_INSTANCE_ID}       ${EMPTY}
${RESPONSE}                  ${EMPTY}


*** Test Cases ***
Get Process Definitions
    # Given
    Process Instance Is Present

    # When
    Camunda Is Requested For Variable Of The Process Instance

    # Then
    Camunda Answered With Correct Value


*** Keywords ***
Process Instance Is Present
    ${variable}    Create Dictionary    foo=bar
    ${response}   Start Process    demo_for_robot    variables=${variable}
    Set Global Variable    ${PROCESS_INSTANCE_ID}    ${response}[id]

Camunda Is Requested For Variable Of The Process Instance
    ${RESPONSE}    Get Process Instance Variable
    ...    process_instance_id=${PROCESS_INSTANCE_ID}
    ...    variable_name=foo
    Set Global Variable    ${RESPONSE}

Camunda Answered With Correct Value
    Should Be True    $RESPONSE    Variable could not be read or is empty.
    Should Be Equal    ${RESPONSE.value}    bar

Clean Up Process Instance
    Run Keyword If    $PROCESS_INSTANCE_ID
    ...    Delete Process Instance    ${PROCESS_INSTANCE_ID}
