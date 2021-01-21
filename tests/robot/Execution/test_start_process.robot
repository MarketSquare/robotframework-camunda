*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Library    Collections
Library    OperatingSystem
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot

*** Test Cases ***
Test starting process
    # WHEN
    ${process_instance}    start process    ${PROCESS_DEFINITION_KEY}

    [Teardown]    delete process instance    ${process_instance}[id]

Test starting process with variables
    #GIVEN
    ${PROCESS_DEFINITION_KEY}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    test1
    ${variable1_key}    Set Variable    my_value
    ${variables}    Create Dictionary    ${variable1_key}=${variable1_value}

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   ${variables}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    ${variable1_key}
    Should Not be empty    ${first_workload}[${variable1_key}]
    Should Be Equal    ${variable1_value}    ${first_workload}[${variable1_key}]
    [Teardown]    complete task

Test starting process with variables after activity
    #GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    After activity test
    ${variable1_key}    Set Variable    my_value
    ${variables}    Create Dictionary    ${variable1_key}=${variable1_value}

    ${after_activity_id}    Set Variable    Activity_service_1

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   ${variables}    after_activity_id=${after_activity_id}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should be empty    ${first_workload}

    [Teardown]    complete task

Test starting process with variables before activity
    #GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    Before activity test
    ${variable1_key}    Set Variable    my_value
    ${variables}    Create Dictionary    ${variable1_key}=${variable1_value}

    ${before_activity_id}    Set Variable    Activity_service_1

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   ${variables}    before_activity_id=${before_activity_id}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    ${variable1_key}
    Should Not be empty    ${first_workload}[${variable1_key}]
    Should Be Equal    ${variable1_value}    ${first_workload}[${variable1_key}]
    [Teardown]    complete task

Test starting process with dict variables
    #GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    test1
    ${variable1_key}    Set Variable    my_value
    ${variables1}    Create Dictionary    ${variable1_key}=${variable1_value}
    ${variables}    Create Dictionary    variables1=${variables1}

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   ${variables}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    variables1
    dictionary should contain key    ${first_workload}[variables1]    ${variable1_key}
    Should Not be empty    ${first_workload}[variables1][${variable1_key}]
    Should Be Equal    ${variable1_value}    ${first_workload}[variables1][${variable1_key}]
    [Teardown]    complete task

Test starting process with file variables
    #GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    ${files}    Create Dictionary    my_file=tests/resources/rf-logo.png

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   files=${files}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    my_file

    # AND
    Should not be empty    ${first_workload}[my_file]
    ${file}    Download file from variable    my_file
    [Teardown]    complete task

Test file content from starting process variable
    #GIVEN
    ${existing_topic}    Set Variable    process_demo_element
    ${testfile}    Set Variable    tests/resources/test.txt
    ${testfile_content}    Get File    ${testfile}

    ${files}    Create Dictionary    my_file=${testfile}

    # WHEN
    start process    ${PROCESS_DEFINITION_KEY}   files=${files}

    # AND
    ${first_workload}     fetch workload   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    my_file

    # AND
    Should not be empty    ${first_workload}[my_file]
    ${process_file}    Download file from variable    my_file
    ${process_file_content}    Get File    ${process_file}
    Should be equal as Strings    ${testfile_content}    ${process_file_content}
    [Teardown]    complete task

Test starting process with file variables
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element

    ${files}    Create Dictionary    my_file=tests/resources/rf-logo.png

    # WHEN
    start process    ${process_definition_key}   files=${files}

    # AND
    ${first_workload}     fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    my_file

    # AND
    Should not be empty    ${first_workload}[my_file]
    ${file}    Download file from variable    my_file
    [Teardown]    complete task

Test file content from starting process variable
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element
    ${testfile}    Set Variable    tests/resources/test.txt
    ${testfile_content}    Get File    ${testfile}

    ${files}    Create Dictionary    my_file=${testfile}

    # WHEN
    start process    ${process_definition_key}   files=${files}

    # AND
    ${first_workload}     fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    my_file

    # AND
    Should not be empty    ${first_workload}[my_file]
    ${process_file}    Download file from variable    my_file
    ${process_file_content}    Get File    ${process_file}
    Should be equal as Strings    ${testfile_content}    ${process_file_content}
    [Teardown]    complete task
