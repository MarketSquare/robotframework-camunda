*** Settings ***
Library     CamundaLibrary    ${CAMUNDA_HOST}
Resource    ../cleanup.resource
Suite Setup    Prepare camunda

*** Variables ***
${MODEL}    ${CURDIR}/../../bpmn/message_test.bpmn
${PROCESS_DEFINITION_KEY_SEND_MESSAGE}    process_send_message
${PROCESS_DEFINITION_KEY_RECEIVE_MESSAGE}    process_receive_message
${TOPIC_SEND_MESSAGE}    send_message
${TOPIC_RECEIVE_MESSAGE}    read_message
${MESSAGE_NAME}    receive_message


*** Test Cases ***
Test Messaging
    [Setup]    Start process    ${PROCESS_DEFINITION_KEY_SEND_MESSAGE}
    #GIVEN
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have no workload
    ${workload}    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    
    # EXPECT
    Last topic should have workload
    
    # WHEN
    ${response}    Deliver Message    ${MESSAGE_NAME}
    Complete task
    
    # THEN 
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have workload
    Complete task

    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    Last topic should have no workload


*** Keywords ***
Prepare camunda
    Deploy    ${MODEL}
    Delete all instances from process '${PROCESS_DEFINITION_KEY_SEND_MESSAGE}'
    Delete all instances from process '${PROCESS_DEFINITION_KEY_RECEIVE_MESSAGE}'

Get workload from topic '${topic}'
    ${workload}    Fetch Workload    ${topic}
    [Return]    ${workload}

Last topic should have workload
    ${recent_process_instance}    Get fetch response
    Should not be empty    ${recent_process_instance}

Last topic should have no workload
    ${recent_process_instance}    Get fetch response
    Should Be Empty    ${recent_process_instance}