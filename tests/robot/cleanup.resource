*** Settings ***
Library    CamundaLibrary   ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Keywords ***
Delete all instances from process '${process_key}'
    ${instances}    Get all active process instances    ${process_key}
    FOR    ${instance}    IN    @{instances}
        Delete process instance    ${instance}[id]
    END
    ${instances}    Get all active process instances    ${process_key}
    Should Be Empty    ${instances}    Process ${process_key} should not have any processes anymore.
