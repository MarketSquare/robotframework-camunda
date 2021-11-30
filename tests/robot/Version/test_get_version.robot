*** Settings ***
Library    CamundaLibrary
Library    String
Suite Setup    Set Camunda Configuration    ${configuration}


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080


*** Test Cases ***
There Should Be A Version String
    ${version_dto}    Get Version
    ${version}    Set Variable    ${version_dto.version}
    ${matches}    Get Regexp Matches    ${version}    \\d+\\.\\d+\\.\\d+
    Length Should Be    ${matches}    1
