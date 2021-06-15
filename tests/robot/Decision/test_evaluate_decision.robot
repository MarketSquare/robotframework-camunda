*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Library    Collections


*** Variables ***
${CAMUNDA_HOST}        http://localhost:8080
${DMN_KEY}             demo_decision
${DECISIONS}           ${EMPTY}


*** Test Cases ***
Decision Table Provides Correct Value
    # Given
    Decision DMD Was Deployed

    # When
    Decision DMD Is Requested

    # Then
    Decision Will Be Correct


*** Keywords ***
Decision DMD Was Deployed
    ${response}    Deploy    tests/bpmn/evaluate_decision.dmn
    Should Be True    $response['id']
    ...    msg=Failed to deploy decision table.

Decision DMD Is Requested
    ${DECISIONS}    Create List
    Set Global Variable    ${DECISIONS}
    Request Decision    Max    20    ${True}
    Request Decision    Bea    30    ${False}
    Request Decision    Zen    99    ${False}

Request Decision
    [Arguments]    ${firstname}    ${age}    ${married}
    ${infos}    Create Dictionary    married=${married}
    ${variables}    Create Dictionary
    ...    firstname    ${firstname}
    ...    age     ${age}
    ...    infos    ${infos}
    ${response}    Evaluate Decision
    ...    ${DMN_KEY}
    ...    variables=${variables}
    Append To List    ${DECISIONS}    ${response}

Decision Will Be Correct
    Log    ${DECISIONS}
    Should Be Equal As Integers    3001001001    ${DECISIONS}[0][0][level]
    Should Be Equal As Integers    0             ${DECISIONS}[1][0][level]
    Should Be Equal As Integers    -1            ${DECISIONS}[2][0][level]
