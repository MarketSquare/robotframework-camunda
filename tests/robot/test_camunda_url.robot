*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_URL}

*** Variables ***
${CAMUNDA_URL}    http://localhost:8080

*** Test Case ***
Camunda URL shall be normalized without trailing / (Issue #13)
    [Documentation]    https://github.com/MarketSquare/robotframework-camunda/issues/13
    [Tags]    issue-13
    ${current_camunda_url}    Get Camunda Url
    Should be equal as Strings    ${CAMUNDA_URL}/engine-rest    ${current_camunda_url}

Camunda URL shall be normalized with trailing / (Issue #13)
    [Documentation]    https://github.com/MarketSquare/robotframework-camunda/issues/13
    [Tags]    issue-13
    Set Camunda Url    ${CAMUNDA_URL}/
    ${current_camunda_url}    Get Camunda Url
    Should be equal as Strings    ${CAMUNDA_URL}/engine-rest    ${current_camunda_url}

