*** Settings ***
Library    CamundaLibrary.ProcessInstance    ${CAMUNDA_URL}
Library    CamundaLibrary.ProcessDefinition
Library    CamundaLibrary.Deployment

*** Variables ***
${CAMUNDA_URL}    http://localhost:8080

*** Test Cases ***
Get all instances
    # Given
    Upload process
    ${process_instances_before}    get all active process instances
    start process    demo_for_robot
    ${process_instances_after}    get all active process instances

    # EXPECT
    should be 1 more process    ${process_instances_before}    ${process_instances_after}

    # WHEN
    FOR    ${process_instance}    IN    @{process_instances_after}
        delete process instance    ${process_instance}['id']
    END

*** Keywords ***
Upload process
    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

should be 1 more process
    [Arguments]    ${before}    ${after}
    ${count_before}    Evaluate    len($before)+1
    ${count_after}    Evaluate    len($after)
    Should be equal as integer    ${count_before}    ${count_after}