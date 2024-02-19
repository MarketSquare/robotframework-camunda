*** Settings ***
Library    CamundaLibrary
Suite Setup    Set Camunda Configuration    ${configuration}
Suite Teardown    Clean Up Process Instance


*** Variables ***
${CAMUNDA_HOST}              http://localhost:8080
${PROCESS_INSTANCE_ID}       ${EMPTY}
${RESPONSE}                  ${EMPTY}
${value}

*** Test Cases ***
Get Process Instance Variable: String
    Given A value    bar
    Given Process Instance Is Present
    When Camunda Is Requested For Variable Of The Process Instance
    Then Camunda Answered With Correct Value

Get Process Instance Variable: List
    Given A List    bar    ber    bir   bor    bur
    Given Process Instance Is Present
    When Camunda Is Requested For Variable Of The Process Instance
    Then Camunda Answered With Correct Value

Get Process Instance Variable: Dictionary
    Given A List    bar=1   ber=2
    Given Process Instance Is Present
    When Camunda Is Requested For Variable Of The Process Instance
    Then Camunda Answered With Correct Value

*** Keywords ***
A Dictionary
    [Arguments]    &{values}
    Set Test Variable    ${value}    ${values}
A List
    [Arguments]    @{values}
    Set Test Variable    ${value}    ${values}

A value
    [Arguments]    ${testvalue}
    Set Test Variable    ${value}    ${testvalue}

Process Instance Is Present
    ${variable}    Create Dictionary    foo=${value}
    ${response}   Start Process Instance    demo_for_robot    variables=${variable}
    Set Global Variable    ${PROCESS_INSTANCE_ID}    ${response}[id]

Camunda Is Requested For Variable Of The Process Instance
    ${RESPONSE}    Get Process Instance Variable
    ...    process_instance_id=${PROCESS_INSTANCE_ID}
    ...    variable_name=foo
    Set Global Variable    ${RESPONSE}

Camunda Answered With Correct Value
    Should Be True    $RESPONSE    Variable could not be read or is empty.
    Should Be Equal    ${RESPONSE}    ${value}

Clean Up Process Instance
    Run Keyword If    $PROCESS_INSTANCE_ID
    ...    Delete Process Instance    ${PROCESS_INSTANCE_ID}
