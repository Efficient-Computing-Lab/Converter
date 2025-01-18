# CEAML

CEAML is an extension of [TOSCA](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html) capable to describe deployment and runtime adaptation for platforms that utilize both Cloud and Edge resources. It supports four entities:

1. [tosca.nodes.Compute.EdgeNode](#toscanodescomputeedgenode)
2. [tosca.nodes.Compute.PublicCloud](#toscanodescomputepubliccloud)
3. [Component](#component)
4. [Platform](#platform)
5. [Complete Examples](#complete-examples)

In a model writen in CEAML it is required to have one or more instances for Component and on instance of Platform. It depends on scenario of the description if the model would contain none, one or more instances of tosca.nodes.Compute.EdgeNode or tosca.nodes.Compute.PublicCloud. 
## tosca.nodes.Compute.EdgeNode

This entity is able to describe a node/host that resides on Edge. The following table presents the descriptions that can be used in this entity.

### Dictionary
| Property      | Value Type | Description                                                                                                                                                                                             |
|---------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| wifi_antenna  | boolean    | If the external WiFi antenna property is present and set to true, it indicates that a device or resource with an external WiFi antenna is required.                                                     |
| gpu_model     | string     | If the GPU map property is present, it indicates that a GPU is required. Further specifications may be needed to specify whether it should be a dedicated GPU or not, as well as the name of the model. |
| building_type | string     | If it is present it means that the described host should belong to a specific building type.                                                                                                            |
| num_cpus      | integer    | The number of CPUs                                                                                                                                                                                      |
| mem_size      | string     | The size of RAM in matters of MBs or GBs                                                                                                                                                                |
| disk_size     | string     | The size of disk in matters of MBs or GBs                                                                                                                                                               |
| architecture  | string     | All the valid values for that property can be found in the documentation of TOSCA. Examples: x86_64 or arm.                                                                                             | 
| type          | string     | All the valid values for this property can be found in the documentation of TOSCA. Examples: Linux or Windows                                                                                           |
| distribution  | string     | All the valid values for this property can be found in the documentation of TOSCA. Examples: Ubuntu                                                                                                     |
| version       | double     | It follows a structure like 20.04                                                                                                                                                                       | 

### Examples
This section includes two examples that use all the above-mentioned properties of the entity.
```yaml
    EdgeNode:
      type: tosca.nodes.Compute.EdgeNode
      properties:
        wifi_antenna: true
        building_type: mall
      capabilities:
        host:
          properties:
            num_cpus: 1
            mem_size: 500 MB
            disk_size: 5 GB
        os:
          properties:
            architecture: arm64
            type: linux
            distribution: Ubuntu
            version: 20.04
```
```yaml
    EdgeNode1:
      type: tosca.nodes.Compute.EdgeNode
      properties:
        gpu_model:
          properties:
            model: nvidia.com/TU117_GEFORCE_GTX_1650
            dedicated: true
      capabilities:
        host:
          properties:
            num_cpus: 8
            mem_size: 8 GB
            disk_size: 20 GB
        os:
          properties:
            architecture: x86_64
            type: linux
```

## tosca.nodes.Compute.PublicCloud

This entity is able to describe a node/host that resides on Cloud. The new entity at the moment supports the same values with its predecessor tosca.nodes.Compute. The following table presents the descriptions that can be used in this entity.

### Dictionary
| Property      | Value Type | Description                                                                                                                                                                                             |
|---------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| num_cpus      | integer    | The number of CPUs                                                                                                                                                                                      |
| mem_size      | string     | The size of RAM in matters of MBs or GBs                                                                                                                                                                |
| disk_size     | string     | The size of disk in matters of MBs or GBs                                                                                                                                                               |
| architecture  | string     | All the valid values for that property can be found in the documentation of TOSCA. Examples: x86_64 or arm.                                                                                             | 
| type          | string     | All the valid values for this property can be found in the documentation of TOSCA. Examples: Linux or Windows                                                                                           |
| distribution  | string     | All the valid values for this property can be found in the documentation of TOSCA. Examples: Ubuntu                                                                                                     |
| version       | double     | It follows a structure like 20.04                                                                                                                                                                       | 

### Examples
This section includes one example that uses all the above-mentioned entities.

```yaml
    PublicCloud:
      type: tosca.nodes.Compute.PublicCloud
      capabilities:
        host:
          properties:
            num_cpus: 2
            mem_size: 2 GB
            disk_size: 35 GB
        os:
          properties:
            architecture: x86_64
            type: linux
```

## Component

This entity is able to describe an application component that should be deployed on a host that resides on Cloud or Edge. The following table presents the descriptions that can be used in this entity.

### Dictionary
| Property        | Value Type | Description                                                                                                                                                                                               |
|-----------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name            | string     | The designation given to a component while it is operational within a platform.                                                                                                                           |        
| application     | string     | Specifies the application to which the component is associated                                                                                                                                            |
| external_ip     | boolean    | Specifies whether the component requires an external IP address or not                                                                                                                                    |
| ports           | list       | This property specifies the port(s) and corresponding protocol(s) used by the component. If the protocol description is not provided, it is assumed to be TCP                                             | 
| deployment_unit | string     | Specifies whether the component is a Docker container or a virtual machine                                                                                                                                |
| flavor          | string     | When the deployment unit is a VM, this is where we specify the image on which it was built.                                                                                                               |
| dependency      | list       | Specifies whether the component has dependencies on other component(s) property.                                                                                                                          | 
| storage         | string     | Specifies whether the component requires persistent storage, ephemeral storage, or none at all.                                                                                                           |
| daemon_set      | boolean    | Specifies whether an application component should be deployed on every cluster host or only on a single host.                                                                                             |
| registry        | map        | This property includes the related image that the component should use                                                                                                                                    |
| ip              | string     | This property cannot have an actual value since IP is being initialized durin runtime. For that reason you could use the TOSCA function named get_input. IP property will be removed in the next version  | 
### Examples
This section includes two examples that use all the above-mentioned properties of the entity.

```yaml
    GameServer:
      type: Component
      properties:
        registry:
          properties:
            image: registry.gitlab.com/orbkaccserver:latest
        name: gameserver
        application: orbk
        external_ip: true
        daemon_set: false
        instance: 1
        deployment_unit: container
        ip: {get_input: ip}
        storage_type: none
        ports:
          - port: 20765
            protocol: UDP
      requirements:
        - host: EdgeNode
```

```yaml
    RelayServer:
      type: Component
      properties:
        registry:
          properties:
            image: registry.gitlab.com/relayserver:latest
        name: relayserver
        application: ovr
        external_ip: true
        daemon_set: false
        ip: { get_input: ip }
        deployment_unit: vm
        flavor: win2k12-iso
        instance: 1
        storage_type: ephemeral
        ports:
          - port: 5055
            protocol: UDP
          - port: 5056
            protocol: UDP
          - port: 5058
            protocol: UDP
          - port: 4520
            protocol: TCP
          - port: 4533
            protocol: TCP
          - port: 4530
            protocol: TCP
          - port: 4531
            protocol: TCP
          - port: 9093
            protocol: TCP
          - port: 9090
            protocol: TCP
          - port: 9091
            protocol: TCP
        dependency:
          - component: relayserver
            property: external_ip
      requirements:
        - host: PublicCloud
```

## Platform

This entity is able to describe an orchestrator of a platform capable to deploy and adapt application components on one or more Cloud and Edge clusters. The following tables present the descriptions that can be used in this entity.

### Dictionary
Platform has two subsections to describe deployment phase and runtime adaptation of application components.

| Property         | Value Type | Description                                                                                                              |
|------------------|------------|--------------------------------------------------------------------------------------------------------------------------|
| deployment_phase | map        | It contains all the actions that can be performed during deployment time                                                 |        
| workflows        | map        | It contains all the actions that should be performed under certain conditions to adapt application components on runtime |

Supported actions of the current version of CEAML are the ones that are shown in the next table.

| Action         | Description                                                                                                  |
|----------------|--------------------------------------------------------------------------------------------------------------|
| deploy         | It outlines the deployment of an application component                                                       |        
| terminate      | It outlines the termination of an application component.                                                     |
| requestSession | It specifies that an application component must establish communication with another application component   |

Each of the supported actions has a structure that includes the properties shown in the below table.

| Property     | Value Type | Description                                                                                                  |
|--------------|------------|--------------------------------------------------------------------------------------------------------------|
| name         | string     | It specifies the name of the action                                                                          |        
| order        | integer    | It delineates the hierarchical order or sequence of the action.                                              |
| components   | list       | It provides details of the target components and their deployment type (container/VM) in the form of a list  |

As it was mentioned earlier in the workflows actions should be performed under certain conditions. For that reason workflows section supports a conditional syntax which is shown in the following table.

| Property  | Value Type | Description                                                                            |
|-----------|------------|----------------------------------------------------------------------------------------|
| scenario  | string     | Textual description of QoE degradation scenario                                        |        
| target    | string     | It provides details about the specific component being targeted in the given scenario. |
| condition | string     | Conditions are expressed using either equalities or thresholds                         |
| actions   | list       | It comprises a set of actions aimed at ensuring a high QoE                             |



### Examples
This section includes one example that uses all the above-mentioned properties of the entity.

```yaml
    Cloud_Framework:
      type: Platform
      properties:
        application: plexus
        deployment_phase:
          - name: deploy
            order: 1
            components:
              - component: localservice
                type: container
              - component: lsnuc
                type: container
        workflows:
          - scenario: LocalService Hardware Overload
            target: localservice
            condition: component_cpu > 80% or component_memory > 80%
            actions:
              - name: terminate
                components:
                  - component: localservice
                    type: container
                order: 1
              - name: deploy
                components:
                  - component: localservice
                    type: container
                order: 2
          - scenario: LocalService Network Overload
            target: localservice
            condition: bandwidth > 80% or avg_latency > 20 ms
            actions:
              - name: terminate
                components:
                  - component: localservice
                    type: container
                order: 1
              - name: deploy
                components:
                  - component: localservice
                    type: container
                order: 2
          - scenario: ls QoE degredation
            target: localservice
            condition: qoe_metric < 3
            actions:
              - name: migrate
                components:
                  - component: localservice
                    type: container
                order: 1
          - scenario: lsnuc QoE degredation
            target: lsnuc
            condition: qoe_metric < 3
            actions:
              - name: scale_in
                components:
                  - component: lsnuc
                    type: container
                order: 1
          - scenario: LSNUC Hardware Overload
            target: lsnuc
            condition: component_cpu > 80% or component_memory > 80%
            actions:
              - name: terminate
                components:
                  - component: lsnuc
                    type: container
                order: 1
              - name: deploy
                components:
                  - component: lsnuc
                    type: container
                order: 2
          - scenario: LSNUC Network Overload
            target: lsnuc
            condition: bandwidth > 80% or avg_latency > 20 ms
            actions:
              - name: terminate
                components:
                  - component: lsnuc
                    type: container
                order: 1
              - name: deploy
                components:
                  - component: lsnuc
                    type: container
                order: 2

```

## Complete Examples
To view complete examples of CEAML, you can check [tosca_orbk.yaml](tosca_orbk.yaml), [tosca_ovr.yaml](tosca_ovr.yaml), and [tosca_plexus.yaml](tosca_plexus.yaml). We also advise using [Sommelier](https://github.com/di-unipi-socc/Sommelier) to check the validity of our models.
Sommelier requires the definition of extended TOSCA entities to perform validation in TOSCA extensions. Definition file can be found [here](definitions/custom_types.yaml).
