# Camunda & Robot Framework
*Introducing robotframework-camunda library*

Resources:
- [Source Code on GitLab.com](https://gitlab.com/postadress/robotframework/robotframework-camunda)
- [Example Test Cases](https://gitlab.com/postadress/robotframework/robotframework-camunda/-/tree/master/tests/robot)
- [Issue Board](https://gitlab.com/postadress/robotframework/robotframework-camunda/-/issues)

**If you are Camunda user, you probably wonder: *What is Robot Framework?***

Robot Framework is an open source automation framework for task automation. Among
other features, it offers a customizable domain language for developing tasks.
It was originally developed for test automation providing the unique advantage
making human readable test description executable.
But most importantly: it comes with the enormous api universe from python.
Meaning any python library can be integrated in to your task automation.

**If you are Robot Framework user, you probably wonder: *What is Camunda?***

2 sentences won't do it justice, just as the above summary about Robot Framework.
In their words: Camunda is a collection of "open source workflow and decision
automation tools [to] enable thousands of developers to automate business
processes and gain the agility, visibility and scale that is needed to achieve
digital transformation".

As Robot Framework enables testers around the world automating their test cases
by simply describing them, Camunda enables process designers to automate processes
by describing in BPMN. You might summerize their power with the slogan: *Automation by documentation*
Both might look like low code, but still offer the full power
for developers to enhance their ecosystem.

## Integrating Camunda and Python

Camunda is primarily built for Java developers, yet implemented the [External Task Pattern](https://docs.camunda.org/manual/7.10/user-guide/process-engine/external-tasks/#the-external-task-pattern)
enabling developers from all programming languages integrating with Camunda through
the very well documented [Camunda REST API](https://docs.camunda.org/manual/7.10/reference/rest/).
For Robot Framework, all you need is implementing a few keywords for convenience
wrapping requests to endpoints from Camunda REST API. Now you'd only need to
package your library, publish it on pypi.org and there you go: the [robotframework-camunda](https://pypi.org/project/robotframework-camunda/) library.

## Library structure
As of November 2020, the `robotframework-camunda` library is in beta. However,
it is already that useful in our production environment that we could not keep
this to ourselves.

The library currently consist of only 5 keywords. Due to the vast amount of endpoints
and use cases for the Camunda REST API there are much more keywords expected to
be implemented. Therefore, the library is structured in sub libraries:

- Camunda.Deployment
- Camunda.ProcessDefinition
- Camunda.ProcessInstance
- Camunda.ExternalTask

### Deployment.Deploy model from file

[Reference](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/deployment/#Deploy%20model%20from%20file)

This keyword simply take a bpmn file created with the [Camunda Modeler](https://camunda.com/de/products/camunda-bpm/modeler/) and uploads
it to a Camunda instance configured in your library:

```robot
*** Settings ***
Library    Camunda.Deployment    http://localhost:8080

*** Task ***
Upload my favorite model to camunda
    Deploy model from file    data/my_favorite.bpmn
```

**This keyword is very convenient when running Camunda for integration tests in a pipeline.**
You may upload your process model to a temporary Camunda instance and
run your tests.

### ProcessDefinition.Start process

[Reference](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/processdefinition/#Start%20process)

This keyword starts a process.

```robot
*** Settings ***
Library    Camunda.ProcessDefinition    http://localhost:8080

*** Task ***
Start my favorite process
    ${my_process_definition_key}    Set Variable    My_favorite_process
    ${my_value}    Create Dictionary    value=This is my actual value    type=String
    ${variables}    Create Dictionary    my_value=${my_value}

    Start Process    ${my_process_definition_key}    ${variables}
```

Creating variables for a process is a bit inconvenient. [Fixing it is on our list.](https://gitlab.com/postadress/robotframework/robotframework-camunda/-/issues/10)

### ExternalTask.Fetch and lock workloads

[Reference](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/externaltask/#Fetch%20and%20Lock%20workloads)

This keyword fetches work items from a certain topic of a process in Camunda:

```robot
*** Settings ***
Library    Camunda.ExternalTask    http://localhost:8080

*** Task ***
Fetch and process workload
    ${workloads}    fetch and lock workloads    my_favorite_topic_in_my_favorite_process
    FOR    ${workload}    IN    @{workloads}
        log    ${workload}[my_value]
        # Access
        Should be equal as String    ${workload}[my_value]    This is my actual value
    END
```

Variables of workloads are typed as dictionaries: `${workload}[my_value]`

**Right now, this keyword only fetches at max 1 work item from Camunda**
[Fixing it is on our list](https://gitlab.com/postadress/robotframework/robotframework-camunda/-/issues/9)

**You cannot provide more options for fetching, yet, like for instance locking duration**

### ExternalTask.Complete task

[Reference](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/externaltask/#Complete%20task)

Only fetching a work item is not worth anything when you do not inform Camunda
about the result. You do that using this keyword:

```robot
*** Settings ***
Library    Camunda.ExternalTask    http://localhost:8080

*** Task ***
Fetch and process workload
    # Fetch workload
    ${workloads}    fetch and lock workloads    my_favorite_topic_in_my_favorite_process

    # Do something with it
    ${workload}    Set Variable    ${workload}[0]
    Should be equal as String    ${workload}[my_value]    This is my actual value

    # Create return value
    ${my_return_value}    Create Dictionary    value=This is my return value    type=String
    ${return_variables}    Create Dictionary    my_value=${my_return_value}

    complete task    my_favorite_topic_in_my_favorite_process    ${return_variables}    
```

**The library caches the process instance that provided the variables. This cached
process instance is automatically used when calling `complete task` so you don't have
to deal with it.**
