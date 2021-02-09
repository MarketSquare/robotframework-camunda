*** Settings ***
Library    CamundaLibrary   ${CAMUNDA_HOST}

*** Variable ***
${CAMUNDA_HOST}    http://localhost:8080

*** Keywords ***
Delete all instances from process '${process_key}'
    ${instances}    Get all active process instances    ${process_key}
    FOR    ${instance}    IN    @{instances}
        Delete process instance    ${instance}[id]
    END
