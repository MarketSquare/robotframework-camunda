*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}    ${configuration}
Library    Collections
Resource    ../cleanup.resource
Suite Setup    Deploy    ${MODEL}

*** Variables ***
${MODEL}    ${CURDIR}/../../bpmn/message_test.bpmn
${PROCESS_DEFINITION_KEY_SEND_MESSAGE}    process_send_message
${PROCESS_DEFINITION_KEY_RECEIVE_MESSAGE}    process_receive_message
${TOPIC_SEND_MESSAGE}    send_message
${TOPIC_RECEIVE_MESSAGE}    read_message
${MESSAGE_NAME}    receive_message


*** Test Cases ***
Test Messaging with Message Result
    [Setup]    Prepare testcase
    #GIVEN
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have no workload
    ${workload}    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    
    # EXPECT
    Last topic should have workload
    
    # WHEN
    ${message_response}    Deliver Message    ${MESSAGE_NAME}
    Complete task
    
    # THEN 
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have workload
    Complete task

    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    Last topic should have no workload

    Should Not Be Empty   ${message_response}

Test Messaging without Message Result
    [Setup]    Prepare testcase
    #GIVEN
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have no workload
    ${workload}    Get workload from topic '${TOPIC_SEND_MESSAGE}'

    # EXPECT
    Last topic should have workload

    # WHEN
    ${message_response}    Deliver Message    ${MESSAGE_NAME}    result_enabled=${False}
    Complete task

    # THEN
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have workload
    Complete task

    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    Last topic should have no workload

    Should Be Empty   ${message_response}

Test Messaging with variable
    [Setup]    Prepare testcase
    #GIVEN
    ${process_variables}    Create Dictionary    message=Hello World
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have no workload
    ${workload}    Get workload from topic '${TOPIC_SEND_MESSAGE}'

    # EXPECT
    Last topic should have workload

    # WHEN
    ${message_response}    Deliver Message    ${MESSAGE_NAME}    process_variables=${process_variables}
    Complete task

    # THEN
    ${received_message_workload}    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have workload
    Dictionaries Should Be Equal    ${process_variables}    ${received_message_workload}
    Complete task

    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    Last topic should have no workload

    Should Not Be Empty   ${message_response}
    [Teardown]   Complete Task

Test Messaging with dict variable
    [Setup]    Prepare testcase
    #GIVEN
    ${languages}    Create List    Suomi    English
    ${person}    Create Dictionary    firstname=Pekka    lastname=Klärck    languages=${languages}
    ${process_variables}    Create Dictionary    person=${person}
    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have no workload
    ${workload}    Get workload from topic '${TOPIC_SEND_MESSAGE}'

    # EXPECT
    Last topic should have workload

    # WHEN
    ${message_response}    Deliver Message    ${MESSAGE_NAME}    process_variables=${process_variables}
    Complete task

    # THEN
    ${received_message_workload}    Get workload from topic '${TOPIC_RECEIVE_MESSAGE}'
    Last topic should have workload
    Dictionaries Should Be Equal    ${process_variables}    ${received_message_workload}
    Complete task

    Get workload from topic '${TOPIC_SEND_MESSAGE}'
    Last topic should have no workload

    Should Not Be Empty   ${message_response}


*** Keywords ***
Prepare testcase
    Delete all instances from process '${PROCESS_DEFINITION_KEY_SEND_MESSAGE}'
    Delete all instances from process '${PROCESS_DEFINITION_KEY_RECEIVE_MESSAGE}'
    Start process    ${PROCESS_DEFINITION_KEY_SEND_MESSAGE}


Get workload from topic '${topic}'
    ${workload}    Fetch Workload    ${topic}
    [Return]    ${workload}

Last topic should have workload
    ${recent_process_instance}    Get fetch response
    Should not be empty    ${recent_process_instance}

Last topic should have no workload
    ${recent_process_instance}    Get fetch response
    Should Be Empty    ${recent_process_instance}